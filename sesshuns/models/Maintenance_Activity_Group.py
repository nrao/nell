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
from datetime                           import datetime, timedelta
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
        app_label = "sesshuns"

    def __unicode__(self):
        sr = "%i -- %s; (%s); %s; %s; " % (self.id, self.week.date(), self.get_start().date(),
                                           self.rank, "deleted" if self.deleted else "active")
        
        if self.maintenance_activity_set.count():
            sr += ", ".join([e.get_subject() for e in self.maintenance_activity_set.all()])
        else:
            sr += "Empty"
        return sr

    def get_week(self):
        """
        Returns the start-of-week date of the week this activity will
        take place in.
        """
        return TimeAgent.truncateDt(self.week)

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
    # associated with this group.  However, when a group is assigned
    # to a scheduled period--i.e. goes from 'floating' to 'fixed',
    # with a firm date and time--is is then possible to go through the
    # repeat templates to see if any should be instantiated for the
    # date of the scheduled period.  If so this function does this and
    # folds them into the existing maintenance activity set and
    # returns it.
    ######################################################################

    def get_maintenance_activity_set(self):
        """
        Returns a set of maintenance activities occuring during this
        group's duration, in time order.
        """

        if not self.period:
            mas = self.maintenance_activity_set.all()
        else:
            period = self.period
            # To handle repeat maintenance activity objects:
            repeatQ = models.Q(deleted = False) \
                & (models.Q(repeat_interval = 1) \
                       | models.Q(repeat_interval = 7) \
                       | models.Q(repeat_interval = 30)) \
                       & (models.Q(_start__lte = period.end()) \
                              & models.Q(repeat_end__gte = period.end()))

            start_endQ = models.Q(start__gte = period.start) \
                & models.Q(start__lte = period.end())
            today = TimeAgent.truncateDt(period.start)
            other_groups_today = Maintenance_Activity_Group.objects\
                .filter(period__start__gte = today)\
                .filter(period__start__lt = today + timedelta(1))\
                .exclude(id = self.id)

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
        period, should any of those be scheduled.
        """
        utc_day = TimeAgent.truncateDt(utc_day)
        mags = []

        try:
            delta = timedelta(days = 7)
            # get maintenance periods for the date span
            mp = Period.objects\
                .filter(session__observing_type__type = "maintenance")\
                .filter(start__gte = utc_day)\
                .filter(start__lt = utc_day + delta)\
                .filter(elective = None)\
                .exclude(state__abbreviation = 'D')

            # get maintenance electives for the date span
            me = Elective.objects\
                .filter(session__observing_type__type = 'maintenance')\
                .filter(periods__start__gte = utc_day)\
                .filter(periods__start__lt = utc_day + delta)\
                .distinct()

            # need as many groups as there are maintenance days
            # (floating or fixed).  First, count up the maintenance
            # days, then the groups.  If not equal, we must either
            # truncate the groups or add to them.  Finally any groups
            # within the tally must be marked not deleted (in case
            # they were deleted earlier), and any outside the tally
            # must be marked deleted.
            maintenance_periods = mp.count() + me.count()
            dbmags = Maintenance_Activity_Group.objects\
                .filter(week__gte = utc_day)\
                .filter(week__lt = utc_day + delta)\
                .order_by("rank")
            mags = [mag for mag in dbmags]

            if maintenance_periods != len(mags):
                if len(mags) > maintenance_periods:
                    for i in range(maintenance_periods, len(mags)):
                        mag = mags[i]
                        mag.deleted = True
                        mag.period = None
                        mag.save()
                if len(mags) < maintenance_periods:
                    for i in range(len(mags), maintenance_periods):
                        mag = Maintenance_Activity_Group()
                        mag.week = utc_day
                        mag.deleted = False
                        mag.rank = chr(65 + i)
                        mag.save()
                        mags.append(mag)

            for i in range(0, maintenance_periods):
                mag = mags[i]
                if mag.deleted:
                    mag.deleted = False
                    mag.save()

            # now make sure scheduled periods/electives get assigned
            # the correct group.
            sched_periods = []

            # start with non-elective periods
            for i in mp:
                if i.isScheduled():
                    sched_periods.append(i)

            # add any elective's scheduled periods
            for i in me:
                sched_periods += i.periodsByState('S')

            # sort periods by start, groups by rank.  Makes them easy
            # to match up.  Any previous matchups will be undone.
            sched_periods.sort(key = lambda x: x.start)
            mags.sort(key = lambda x: x.rank)

            for i in range(0, len(mags)):
                mag = mags[i]

                if i < len(sched_periods):
                    p = sched_periods[i]

                    if mag.period != p:
                        mag.period = p
                        mag.save()
                else:
                    if mag.period:
                        mag.period = None
                        mag.save()
        except:
            if settings.DEBUG == True:
                printException(formatExceptionInfo())

        if not include_deleted:
            mags = [m for m in mags if not m.deleted]

        return mags

