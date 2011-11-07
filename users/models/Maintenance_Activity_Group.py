######################################################################
#
#  Maintenance_Activity_Group.py - defines the model classes for the
#  resource calendar.
#
#  Copyright (C) 2010 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

from django.db                          import models, transaction
from scheduler.models                   import Period, Window, Elective
from Maintenance_Activity               import Maintenance_Activity
from datetime                           import datetime, timedelta, time
from nell.utilities                     import TimeAgent
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException

import settings

######################################################################
# Maintenance_Activity_Group is a collection points for all
# maintenance activities contemplated for a single maintenance period.
# When future maintenance periods take the form of pending periods or
# electives their exact date is not known.  It is not even known if
# one will precede another.  So the system creates as many
# Maintenance_Activity_Groups as there are possible maintenance
# activity dates for that week, labeling them 'A', 'B', etc.  It is
# guaranteed that 'A' will be then attached to the earliest
# maintenance date, 'B' to the next one, etc.
#
# The following is a use case, assuming 2 maintenance days denoted by
# equal electives (date range exactly the same: Tuesday-Friday).
#
#   1) The system sees the two electives for that week.  It then
#   creates (as needed) 2 Maintenance_Activity_Groups, labeling one
#   'A' and the other 'B'.  It does nothing if they are already
#   created.  It truncates the list if the number of elective
#   maintenance electives decreased, deleting the lowest rank ('A' is
#   highest).  It increases the list if the number of maintenance
#   electives increased.  Deletions of Maintenance_Activity_Groups are
#   'soft', enabling the administrators to restore them or the
#   activities attached to them.
#
#   2) These are now be displayed on the calendar in order, on the
#   Monday of the week, where maintenance personnel can attach
#   activities to them.  They are not attached to any periods yet.
#
#   3) The scheduler schedules one of the electives.
#
#   4) The calendar notes this and attaches group 'A' to the published
#   period.
#
#   5) The scheduler schedules the second one, at a date that comes
#   after the first one.
#
#   6) The calendar notes this and attaches group 'B' to the published
#   period.
#
#       ---OR---
#
#   5) The scheduler schedules the second one, but on a date that
#   comes before the first scheduled elective.
#
#   6) The calendar notes that 'B' will come before 'A', and swaps the
#   two.  Now 'A' is attached to the earlier date, and 'B' to the
#   later date.
#
#   7) Maintenance_Activity_Groups remain attached to periods even
#   after periods are published.  This allows the calendar to maintain
#   this 'A', 'B' ... ordering even if the scheduler alters the date
#   of an already published period.
######################################################################

class Maintenance_Activity_Group(models.Model):

    period  = models.ForeignKey(Period, null = True)
    rank    = models.CharField(max_length = 2)          # 'A', 'B', etc.
    deleted = models.BooleanField(default = False)
    # The Monday of the maintenance week.  This is here so that
    # maintenance activity groups can be queried by the week of
    # interest.
    week    = models.DateTimeField(null = True)

    class Meta:
        db_table  = "maintenance_activity_group"
        app_label = "users"

    def __unicode__(self):
        sr = "%i -- %s; (%s); %s; %s; " % (self.id, self.week.date() if self.week else '',
                                           self.get_start().date(),
                                           self.rank, "deleted" if self.deleted else "active")

        if self.maintenance_activity_set.count():
            sr += ", ".join([e.get_subject() for e in self.maintenance_activity_set.all() \
                                 if not e.is_repeat_template()])
        else:
            sr += "Empty"
        return sr

    def get_week(self):
        """
        Returns the start-of-week date of the week this activity will
        take place in.
        """
        return TimeAgent.truncateDt(self.week) if self.week else None

    def get_start(self, tzname = None):
        """
        If this is a fixed maintenance period there will have been a
        period assigned.  If so, return this period's start.  If not,
        return the start-of-week date.
        """
        if self.period:
            start = self.period.start
            return TimeAgent.utc2est(start) if tzname == 'ET' else start
        else:
            return self.get_week()

    def get_end(self, tzname = None):
        """
        If this is a fixed maintenance period then return the period's
        end, if not return the end of the week.
        """

        if self.period:
            end = self.period.end()
            return TimeAgent.utc2est(end) if tzname == 'ET' else end
        else:
            return self.get_week() + timedelta(7)

    ######################################################################
    # The model already has a 'maintenance_activity_set' attribute
    # wich can be used to access the Maintenance_Activity objects
    # associated with this group.  This code adds instances of repeat
    # activities to this set based on any repeat templates that are
    # currently active.  Repeats are added to both published and
    # unpublished maintenance activity groups.  The following lays out
    # the heuristics.
    #
    # We start out with an example of what we want, based on the following week:
    #
    #                    Week
    #   Monday    Tuedsay    Wednestay  Thurdsay   Friday     Saturday   Sunday
    # |----------|----------|----------|----------|----------|----------|----------|
    #     'B'                 'x'                   'Ap'
    #     'C'
    #
    # 'B', 'C': floating unpublished
    # 'x'     : fixed published
    # 'Ap'    : floating published
    #
    # Note: when 'add'ing below the assumption is that it first checks
    # to ensure this hasn't already been done.
    #
    # Assigning repeats.  Here is what we want to do:
    #
    #    - Daily:   * add one to all '*p', and to 'x' if not 'Unscheduled Maintenance'.
    #                 Ensure only one per day.
    #               * add one each to 'A' and 'B'.
    #               * done.
    #
    #    - Weekly:  * See if any 'x' or '*p' fits the bill.
    #                 - Yes:  done.
    #                 - No: continue.
    #               * affix to 'A'
    #               * done.
    #
    #    - Monthly: * See if this week is due.
    #                 - Yes: Do as weekly.
    #                 - No: done.
    #
    # From the above it can be seen that we don't really deal in
    # periods here, only in maintenance activity groups.  There are 5
    # kinds of maintenance activity groups:
    #
    #    * floating unpublished
    #    * fixed unpublished
    #    * floating published
    #    * fixed published
    #    * fixed published that are emergency.
    #
    # Of those we are only interested in three:
    #
    #    * floating unpublished
    #    * fixed published, except emergency
    #    * floating published
    #
    # These can be reduced to two groups of mags by query:
    #
    #    * Ux: maintenance activity groups that have no period (remaining floating)
    #    * P:  maintenance activity groups with periods that don't belong
    #          to session "Uncheduled Maintenance".
    #
    # This reduces all the above to:
    #
    #         Week
    #   Monday    Tuedsay    Wednestay  Thurdsay   Friday     Saturday   Sunday
    # |----------|----------|----------|----------|----------|----------|----------|
    #     'U1'                 'P'                   'P'
    #     'U2'
    #
    # This function is done from the perspective of the MAG.
    # Instantiating a template is therefore is like claiming it.  But
    # before claiming it we check to make sure no other MAG has a
    # better claim.. From the perspective of the MAG, assigning
    # repeats becomes:
    #
    #    - Daily:   * Is self a P?
    #                   - Yes: Is there another P today?
    #                            - Yes: Is other P more suitable?
    #                                     -Yes: continue;
    #                            - No: add one to self
    #                   - No: Is self a 'U'?
    #                           - Yes: add one to self
    #               * done.
    #
    #    - Weekly:  * See if any other 'P' fits the bill.
    #                 - Yes: done.
    #               * If self a 'P', is self suitable?
    #                 - Yes: add, and done.
    #                 - No: continue
    #               * If self a 'U', see if highest ranking 'U'
    #                 - Yes : add the repeat activity.
    #               * done.
    #
    #    - Monthly: * See if this week is due.
    #                 - Yes: Do as weekly.
    #                 - No: done.
    #
    # There is one final step, which is to clean up after the 'U*'
    # become published, in case two or more are published to the same
    # day as each other or another maintenance activity group which
    # has already received a repeat.  Look for MAGs on the same day.
    # If found, ensure that a particular repeat activity only shows up
    # on the appropriate MAG.
    ######################################################################

    def get_maintenance_activity_set(self):
        """
        Returns a set of maintenance activities occuring during this
        group's duration, in time order.
        """

        floating_maintenance = u'Maintenance day'
        fixed_maintenance = u'Maintenance'

        # We need some functions...
        def is_P(mag):
            return True if mag.period and \
                mag.period.session.name == fixed_maintenance \
                else False

        def is_U(mag):
            return True if not mag.period else False

        def is_highest_U(mag):
            if not is_U(mag):
                return False

            week = mag.week
            mags = Maintenance_Activity_Group.objects.filter(week = week)\
                .filter(period = None).order_by("rank")
            return mag == mags[0]

        def already_instantiated(template, mag):
            # the answer is 'True' if it is in this mag...
            for j in mag.maintenance_activity_set.all():
                if j.repeat_template == template:
                    return True

            # or, if daily template, in another mag today...
            if template.repeat_interval == 1:
                for omag in other_groups_today:
                    for j in omag.maintenance_activity_set.all():
                        if j.repeat_template == template:
                            return True

            # or, if weekly or monthly, if it is in another mag this week.
            if template.repeat_interval == 7 or template.repeat_interval == 30:
                for omag in other_groups_this_week:
                    for j in omag.maintenance_activity_set.all():
                        if j.repeat_template == template:
                            return True
            # Not instantiated.
            return False

        def get_monthly_due_dates(template):
            start_date = template._start.date()
            end = template.repeat_end
            dates = []
            midnight = time(0, 0, 0)
            months = 0
            ddate = start_date

            while ddate < end:
                dates.append(datetime.combine(ddate, midnight))
                months = months + 1
                ddate = TimeAgent.add_months(start_date, months)
            return dates

        def get_due_date(template):
            if template.repeat_interval == 30:
                due_dates = get_monthly_due_dates(template)

                for i in range(0, 7):
                    dday = self.week + timedelta(days = i)
                    
                    if dday in due_dates:
                        return dday
                    
            if template.repeat_interval == 7:
                week = TimeAgent.truncateDt(self.week)
                start_date = TimeAgent.truncateDt(template.get_start())
                diff = timedelta(days = (week - start_date).days % \
                                     template.repeat_interval)
                return week + timedelta(7) - diff
            return None


        def template_due(template):
            # daily and weekly will always be due this week.
            if template.repeat_interval == 1 or template.repeat_interval == 7:
                return True

            return False if not get_due_date(template) else True


        def good_fit(template, mag):
            # Checks to see if this template wouldn't work better
            # elsewhere.  If so, returns False.  If not, returns True.

            # first, take care of simple cases: repeat = 1, or no
            # published mags this week, the template is due, and this
            # is the highest U:

            if template.repeat_interval == 1:
                return False if better_fit(t, other_groups_today) else True

            if len(published_groups_this_week) == 0 \
                    and is_highest_U(mag):
                return True

            if is_P(self):
                dm = {-4: 40, -3: 30, -2: 20, -1: 10, 0: 0, 1: 15, 2: 25, 3: 35, 4: 45}
                today = TimeAgent.truncateDt(self.period.start)
                p = [mag.period for mag in published_groups_this_week]
                due_date = get_due_date(template)
                diff = (today - due_date).days

                if diff:
                    # doesn't fall on this date.  Is this the closest
                    # period though?
                    for j in p:
                        if j != self.period:  # check only other periods
                            mod = (TimeAgent.truncateDt(j.start) - due_date).days

                            # Test to see if it's a better fit in
                            # another period.  and if so, don't
                            # use here.
                            if dm[mod] < dm[diff]:
                                return False
                return True
            return False


        def better_fit(template, other_mags):
            for g in other_mags:
                if template.get_start().time() >= g.get_start().time() \
                        and template.get_start().time() < g.get_end().time():
                    return True
            return False

        def instantiate(template, mag):
            ma = template.clone(mag)

        if is_P(self) or is_U(self):
            # set up all the data we need:
            if is_P(self):
                today = TimeAgent.truncateDt(self.period.start)
                end = self.period.end()
            else:
                today = self.week
                end = self.week + timedelta(days = 7)

            # Get repeat templates
            repeatQ = models.Q(deleted = False) \
                & (models.Q(repeat_interval = 1) \
                       | models.Q(repeat_interval = 7) \
                       | models.Q(repeat_interval = 30)) \
                       & (models.Q(_start__lte = end) \
                              & models.Q(repeat_end__gte = today))
            dbrmas = Maintenance_Activity.objects.filter(repeatQ)
            templates = [p for p in dbrmas]

            allowed_sessionsQ = models.Q(period__session__name = fixed_maintenance) \
                | models.Q(period__session__name = floating_maintenance)

            if is_P(self):
                today = TimeAgent.truncateDt(self.period.start)
                # Get other groups today.  They will be used below to see
                # if any of them is a better fit.  We must exclude any
                # possible emergency maintenance periods:

                other_groups_today = Maintenance_Activity_Group.objects\
                    .exclude(id = self.id) \
                    .filter(period__start__gte = today)\
                    .filter(period__start__lt = today + timedelta(1))\
                    .filter(allowed_sessionsQ)
            else:
                other_groups_today = []

            this_week = self.get_week()

            published_groups_this_week =  Maintenance_Activity_Group.objects\
                .exclude(id = self.id) \
                .filter(period__start__gte = this_week)\
                .filter(period__start__lt = today + timedelta(7))\
                .filter(allowed_sessionsQ)

            unpublished_groups_this_week =  Maintenance_Activity_Group.objects\
                .exclude(id = self.id) \
                .filter(week__gte = this_week)\
                .filter(week__lt = today + timedelta(7))\
                .filter(period = None)

            other_groups_this_week = [mag for mag in published_groups_this_week] \
                + [mag for mag in unpublished_groups_this_week]

            # Meat and potatoes: For each template, see if we must
            # instantiate it.  We do so if it is due and hasn't been
            # taken care of yet.

            for t in templates:
                if template_due(t):
                    if not already_instantiated(t, self):
                        if good_fit(t, self):
                            instantiate(t, self)

        groupQ  = models.Q(group = self)
        dbmas   = Maintenance_Activity.objects.filter(groupQ)
        # remove all activities marked deleted.  This must be done
        # after all the above to prevent a replacement being generated
        # for a deleted activity, for repeat activities.
        mas = [i for i in dbmas if not i.deleted and not i.is_repeat_template()]
        mas.sort(cmp = lambda x, y: cmp(x.get_start(),
                                        y.get_start()))
        return mas

    def get_maintenance_activity_set2(self):
        """
        Returns a set of maintenance activities occuring during this
        group's duration, in time order.
        """

        unscheduled_maintenance = "Unscheduled Maintenance"

        if not self.period or self.period.session.name == unscheduled_maintenance:
            mas = self.maintenance_activity_set.all()
        else:
            # To handle repeat maintenance activity objects:
            period = self.period

            # Get the templates:
            repeatQ = models.Q(deleted = False) \
                & (models.Q(repeat_interval = 1) \
                       | models.Q(repeat_interval = 7) \
                       | models.Q(repeat_interval = 30)) \
                       & (models.Q(_start__lte = period.end()) \
                              & models.Q(repeat_end__gte = period.end()))

            # Get the time period
            start_endQ = models.Q(start__gte = period.start) \
                & models.Q(start__lte = period.end())
            today = TimeAgent.truncateDt(period.start)
            # Get other groups today.  They will be used below to see
            # if any of them is a better fit.  We must exclude any
            # possible emergency maintenance periods:
            other_groups_today = Maintenance_Activity_Group.objects\
                .filter(period__start__gte = today)\
                .filter(period__start__lt = today + timedelta(1))\
                .exclude(id = self.id) \
                .exclude(period__session__name = unscheduled_maintenance)

            groupQ  = models.Q(group = self)
            dbmas   = Maintenance_Activity.objects.filter(groupQ)
            dbrmas  = Maintenance_Activity.objects.filter(repeatQ)
            mas     = [i for i in dbmas if not i.is_repeat_template()]
            rmas    = [i for i in dbrmas]

            # rmas is the list repeating activity templates that may
            # apply for this period.  We need clones of these to
            # include in mas.  If however there are already clones in
            # mas, we'll want to skip that template.  We will also
            # skip the template if there is a better candidate
            # maintenance activity group on this day (by better, a
            # better match in time, defined by the activity's start
            # time being within the maintenance activity group's time
            # span).

            x = []

            for i in rmas:
                for j in mas:
                    if j.repeat_template == i:
                        x.append(i)

                for g in other_groups_today:
                    if i.get_start().time() >= g.get_start().time() \
                            and i.get_start().time() < g.get_end().time():
                        x.append(i)


            # Weekly repeats have a problem: what if the repeat falls on a
            # day that is not a maintenance day?  Where should we put it?
            # One strategy is to examine the maintenance periods from 3
            # days in the past to 3 days into the future.  if none of
            # those is more suitable, we keep the weekly activity here. If
            # there is a tie, we favor the earlier date. This is done by
            # taking the modulo 7 of start - maintenance_activity.start
            # and mapping it to the values in 'dm'.  Lowest value wins.

            dm = {4: 30, 5: 20, 6: 10, 0: 0, 1: 15, 2: 25, 3: 35}
            delta = timedelta(days = 3)
            today = TimeAgent.truncateDt(period.start)
            p = Period.get_periods_by_observing_type(today - delta,
                                                     today + delta,
                                                     "maintenance")

            for i in rmas:
                if i.repeat_interval > 1:
                    start_date = TimeAgent.truncateDt(i.get_start())
                    diff = (today - start_date).days % i.repeat_interval

                    if diff:
                        # doesn't fall on this date.  Is this the closest
                        # period though?

                        if diff > 6:     # monthly not due
                            x.append(i)
                        else:            # weekly or monthly that is due this week
                            for j in p:
                                if j != period:  # check only other periods
                                    mod = (j.start.date() \
                                               - start_date.date()).days \
                                               % i.repeat_interval

                                    # Test to see if it's a better fit in
                                    # another period.  and if so, don't
                                    # use here.
                                    if mod < 7 and dm[mod] < dm[diff]:
                                        x.append(i)
                                        break

            # Now that we have a list of templates that are not suitable,
            # cull the template list:
            for i in x:
                if i in rmas:
                    rmas.remove(i)

            # The remaining templates may be used:
            for i in rmas:
                ma = i.clone(self)
                mas.append(ma)

        # remove all activities marked deleted.  This must be done
        # after all the above to prevent a replacement being generated
        # for a deleted activity, for repeat activities.
        mas = [i for i in mas if not i.deleted]
        mas.sort(cmp = lambda x, y: cmp(x.get_start(),
                                        y.get_start()))

        return mas

    @staticmethod
    @transaction.commit_on_success
    def get_maintenance_activity_groups(utc_day, include_deleted = False):
        """
        Returns a list of maintenance activity groups for the week
        starting on 'utc_day'.  This list will be sorted by rank, and
        each group will have been assigned to the correct maintenance
        period, should any of those be scheduled.  Those groups with
        rank 'x' are fixed, already have periods, and do not get
        sorted by rank.
        """

        mags = []

        pmags = Maintenance_Activity_Group._get_fixed_mags(utc_day)
        emags = Maintenance_Activity_Group._get_elective_mags(utc_day)

        mags = emags + pmags # electives first, then fixed.

        if not include_deleted:
            mags = [m for m in mags if not m.deleted]

        return mags

    @staticmethod
    def _get_fixed_mags(utc_day):
        mags = []

        try:
            delta = timedelta(days = 7)
            # get maintenance periods for the date span
            mp = Period.objects\
                .filter(session__observing_type__type = "maintenance")\
                .filter(start__gte = utc_day)\
                .filter(start__lt = utc_day + delta)\
                .filter(session__session_type__type = 'fixed')\
                .filter(state__name = "Scheduled")

            for i in mp:
                if i.maintenance_activity_group_set.count() == 0:
                    mag = Maintenance_Activity_Group()
                    mag.deleted = False
                    mag.rank = 'x'
                    mag.week = utc_day
                    i.maintenance_activity_group_set.add(mag)
                else:
                    mag = i.maintenance_activity_group_set.all()[0]
                    # for backwards compatibility, mark groups
                    # belonging to fixed periods with rank 'x' so that
                    # they are not picked up by _get_elective_mags().
                    if mag.rank != 'x':
                        mag.rank = 'x'
                        mag.save()

                    if not mag.week:
                        mag.week = utc_day
                        mag.save()

                mags.append(mag)
                mags.sort(key = lambda x: x.get_start())
        except:
            if settings.DEBUG == True:
                printException(formatExceptionInfo())

        return mags

    @staticmethod
    def _get_elective_mags(utc_day):
        mags = []

        try:
            delta = timedelta(days = 7)
            # get maintenance electives for the date span
            me = Elective.objects\
                .filter(session__observing_type__type = 'maintenance')\
                .filter(periods__start__gte = utc_day)\
                .filter(periods__start__lt = utc_day + delta)\
                .distinct()

            # don't care about elective with all deleted periods.
            me = [e for e in me if e.periods.count() > e.deletedPeriods().count()]

            # need as many floating groups as there are elective
            # maintenance days.  First, count up the maintenance days,
            # then the groups.  If not equal, we must either truncate
            # the groups or add to them.  Finally any groups within
            # the tally must be marked not deleted (in case they were
            # deleted earlier), and any outside the tally must be
            # marked deleted.

            maintenance_periods = len(me)
            # When obtaining the maintenance activity groups for this
            # week, ensure that the query will match the mag's 'week'
            # field by stripping off the time of 'utc_day'.  Otherwise
            # it may not pick it up.  Also we include a generous time
            # range for 'week' just to make sure time issues don't
            # crop in and exclude any group.
            dbmags = Maintenance_Activity_Group.objects\
                .filter(week__gte = TimeAgent.truncateDt(utc_day))\
                .filter(week__lt = TimeAgent.truncateDt(utc_day) + delta)\
                .exclude(rank = 'x') \
                .order_by("rank")
            mags = [mag for mag in dbmags]

            # these are all ordered by rank now, relabel rank in case
            # it doesn't start with 'A' ('B', 'C', etc.), or there is
            # a gap ('A', 'B', 'D', etc.) (would occur if manually
            # deleted from database, etc., and leaving old rank might
            # confuse users.)
            for i in range(0, len(mags)):
                if mags[i].rank != chr(65 + i):
                    mags[i].rank = chr(65 + i)
                    mags[i].save()

            # either too many or not enough mags.  Deal with it
            # accordingly...
            if maintenance_periods != len(mags):
                # too many; mark the excess as deleted.
                if len(mags) > maintenance_periods:
                    for i in range(maintenance_periods, len(mags)):
                        mag = mags[i]
                        mag.deleted = True
                        mag.period = None
                        mag.save()
                # too few; create more to make up the numbers.
                if len(mags) < maintenance_periods:
                    for i in range(len(mags), maintenance_periods):
                        mag = Maintenance_Activity_Group()
                        mag.week = TimeAgent.truncateDt(utc_day)
                        mag.deleted = False
                        mag.rank = chr(65 + i)
                        mag.save()
                        mags.append(mag)

            # Mark all mags from 0 to number of maintenance periods as
            # undeleted.  This reuses any previously deleted mags.
            for i in range(0, maintenance_periods):
                mag = mags[i]
                if mag.deleted:
                    mag.deleted = False
                    mag.save()

            # now make sure scheduled electives get assigned the
            # correct group.
            sched_periods = []

            for i in me:
                sched_periods += i.periodsByState('S')

            # sort periods by start, groups by rank.  Makes them easy
            # to match up.  Any previous matchups will be undone.
            sched_periods.sort(key = lambda x: x.start)
            mags.sort(key = lambda x: x.rank)

            def in_query_set(item, qset):
                for i in qset:
                    if item == i:
                        return True
                    return False

            for i in range(0, len(mags)):
                mag = mags[i]

                if i < len(sched_periods):
                    p = sched_periods[i]

                    # update the period if the mag is not the right
                    # one, or if it has more than one mag, to ensure
                    # just one per period.
                    if not in_query_set(mag, p.maintenance_activity_group_set.all()) \
                            or p.maintenance_activity_group_set.count() > 1:
                        p.maintenance_activity_group_set.clear()
                        p.maintenance_activity_group_set.add(mag)
                else:
                    if mag.period:
                        mag.period = None
                        mag.save()
        except:
            if settings.DEBUG == True:
                printException(formatExceptionInfo())

        return mags
