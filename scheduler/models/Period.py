# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from django.db              import models
from django.core.exceptions import ObjectDoesNotExist
from datetime               import datetime, timedelta
from utilities            import AnalogSet
from utilities.TimeAgent  import range_to_days
from utilities.TimeAgent  import timedelta2minutes
from utilities.TimeAgent  import adjustDateTimeTz
from utilities.AnalogSet  import overlaps
from Observing_Type       import Observing_Type
from Project              import Project
from Sesshun              import Sesshun
from Period_Accounting    import Period_Accounting
from Period_State         import Period_State
from Receiver             import Receiver
from Receiver_Schedule    import Receiver_Schedule

import urllib2
import simplejson as json

class Period(models.Model):
    session    = models.ForeignKey(Sesshun)
    accounting = models.ForeignKey(Period_Accounting, null=True)
    state      = models.ForeignKey(Period_State, null=True)
    start      = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm")
    duration   = models.FloatField(help_text = "Hours")
    score      = models.FloatField(null = True, editable=False, blank = True)
    forecast   = models.DateTimeField(null = True, editable=False, blank = True)
    backup     = models.BooleanField()
    moc        = models.NullBooleanField(default = True)
    moc_ack    = models.BooleanField(default = False)
    receivers  = models.ManyToManyField(Receiver, through = "Period_Receiver")
    window     = models.ForeignKey("Window", blank=True, null=True, related_name = "periods")
    elective   = models.ForeignKey("Elective", blank=True, null=True, related_name = "periods")
    last_notification = models.DateTimeField(blank=True, null=True, help_text = "yyyy-mm-dd hh:mm")


    class Meta:
        db_table  = "periods"
        app_label = "scheduler"
    
    def end(self):
        "The period ends at start + duration"
        return self.start + timedelta(hours = self.duration)

    def on_day(self, day):
        "Does this period ever take place on the specified day (a datetime)?"
        next_day = day + timedelta(days = 1)
        return (self.end() > day) and (self.start < next_day)

    def __unicode__(self):
        return "Period (%d) for Session (%d): %s for %5.2f Hrs (%s) - %s" % \
            (self.id,self.session.id, self.start, self.duration, self.state.abbreviation, self.accounting)

    def __str__(self):
        return "%s: %s for %5.2f Hrs" % \
            (self.session.name, self.start, self.duration)

    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def display_name(self):
        return self.__str__()

    def isDeleted(self):
        return self.state.abbreviation == 'D'

    def isScheduled(self):
        return self.state.abbreviation == 'S'

    def isPending(self):
        return self.state.abbreviation == 'P'

    def isCompleted(self):
        return self.state.abbreviation == 'C'

    def toHandle(self):
        if self.session.original_id is None:
            original_id = ""
        else:
            original_id = str(self.session.original_id)
        return "%s (%s) %s" % (self.session.name
                             , self.session.project.pcode
                             , original_id)

    def get_rcvr_ranges(self):
        ranges = ["%5.2f - %5.2f".strip() % (r.freq_low, r.freq_hi) for r in self.receivers.all()]
        return ", ".join(ranges)

    def receiver_list(self):
        "Simply what JSON returns"
        return self.get_rcvrs_json()

    def receiver_list_simple(self):
        "Removes redudancies, and makes sure it's ordered"
        rcvrs = []
        for r in self.receivers.all().order_by('abbreviation'):
            if r.abbreviation not in rcvrs:
                rcvrs.append(r.abbreviation)
        return ", ".join(rcvrs)       
    
    def get_rcvrs_json(self):
        rcvrs = [r.abbreviation for r in self.receivers.all()]
        return ", ".join(rcvrs)

    def has_required_receivers(self):

        # Find all the required receiver sets for this period and schedule.
        # E.g. for one session:
        #     [[a, b, c], [x, y, z]] = (a OR b OR c) AND (x OR y OR z)
        required = [self.session.receiver_group_set.all()]
        if all([len(rx_set) == 0 for rx_set in required]):
            return False # No receivers, problem!

        # NOTE: get schedule for two days, to catch receivers going
        # up/down on the day of interest.  There is no way to know for
        # sure via the database the exact time that a receiver went up
        # or down.  Instead the break-point is assumed to be 1600
        # hours UT on any given day (it's in the database, but that is
        # how Receiver_Schedule.extract_schedule() operates).  So if
        # the receiver changes at some other hour this function could
        # return an erroneous value unless it considers the union of
        # the receivers up before and after 1600 hours.
        schedule = Receiver_Schedule.extract_schedule(self.start, 1)
        if schedule == {} or \
           (len(schedule.values()) == 1 and schedule.values()[0] == []):
            return False # no schedule, no required rcvrs!

        receivers = set(schedule.values()[0])

        # There might not be a second day...
        if len(schedule.values()) == 2:
            map(lambda x: receivers.add(x), schedule.values()[1])

        if not any([all([set(g.receivers.all()).intersection(receivers) \
                        for g in rx_set]) for rx_set in required]):
            return False # Receiver isn't up
        else:
            return True # Receiver is up

    def has_observed_rcvrs_in_schedule(self):


        #obs_rcvrs = [r.abbreviation for r in self.receivers.all()]
        obs_rcvrs = self.receivers.all()

        schedule = Receiver_Schedule.extract_schedule(self.start, 0)
        if schedule == {} or \
           (len(schedule.values()) == 1 and schedule.values()[0] == []):
            return False # no schedule, no required rcvrs!

        # should return a single date w/ rcvr list
        dt, receivers = schedule.items()[0]

        for r in obs_rcvrs:
            if r not in receivers:
                return False # Receiver isn't up

        return True # Receiver is up

    def move_to_deleted_state(self):
        "all in the name"
        self.state = Period_State.get_state("D")
        self.save()

    def move_to_scheduled_state(self):
        "worker for publish method: pending -> scheduled, and init time accnt."
        if self.state.abbreviation == "P":
            self.state = Period_State.objects.get(abbreviation = 'S')
            self.accounting.scheduled = self.duration
            self.accounting.save()
            self.save()

    def publish(self):
        "pending state -> scheduled state: and init the time accounting"
        if self.state.abbreviation == 'P':
            self.move_to_scheduled_state()
            # if this is part of a window, deal w/ the consequences
            if self.is_windowed() and self.window is not None:
                self.window.publish() 
                self.window.save()
            # if this is part of an elective, deal w/ the consequences
            if self.is_elective() and self.elective is not None:
                self.elective.publish()                
                self.elective.save()


    def delete(self):
        """
        Keep non-pending periods from being deleted.  Also prevent any
        periods with associated maintenance activities from being
        deleted.
        """

        if self.state.abbreviation != 'P' or self.maintenance_activity_group_set.exists():
            self.move_to_deleted_state()
        else:
            models.Model.delete(self)  # pending can really get removed!

    def remove(self):
        "A backdoor method for really deleting!"
        models.Model.delete(self)

    def is_windowed(self):
        return self.session.session_type.type == "windowed"

    def is_elective(self):
        return self.session.session_type.type == "elective"

    def get_default_window(self):
        "Get the window this period is a default period for."
        try:
            return self.default_window
        except ObjectDoesNotExist:
            return None

    def is_windowed_default(self):
        """
        Is this period the default period for a window?
        If not, is it the chosen"
        """
        return self.get_default_window() is not None

    def assign_a_window(self):
        """
        For assigning a period belonging to a windowed session a window.
        Currently this could happen if a period for a win. sess. is 
        created in the Period Explorer (even via Nominees) in the UI.
        This is harmless if a window cant' be assigned.
        """
        if not self.session.isWindowed() or not self.session.window_set.exists():
            return
        
        # look for a window (any) that this period at least starts in 
        for win in self.session.window_set.all():
            start = win.start_datetime()
            end   = win.end_datetime()
            if start is not None and end is not None and \
                self.start >= start and self.start < end:
                self.window = win
                self.save()
                return # take the first one you find!

    def reinit_score(self):
        """
        If the Period has changed in certain ways (ex: time range)
        it will need to be rescored; but nell doesn't score, so just
        prepare it to be rescored.
        """
        self.score = -1.0
        self.forecast = None
        self.moc = None

    @staticmethod
    def get_periods(start, duration, ignore_deleted = True):
        "Returns all periods that overlap given time interval (start, minutes)"
        end = start + timedelta(minutes = duration)

        # there is no Period.end in the database, so, first cast a wide net.
        # we can do this because periods won't last more then 16 hours ...
        beforeStart = start - timedelta(days = 1)
        afterEnd    = end   + timedelta(days = 1)
        some = Period.objects.filter(start__gt = beforeStart
                                   , start__lt = afterEnd).order_by('start')
        # now widdle this down to just the periods that overlap  
        ps = [p for p in some if (p.start >= start and p.end() <= end) \
                              or (p.start <= start and p.end() > start) \
                              or (p.start < end    and p.end() >= end)]
        if ignore_deleted:                      
            ps = [p for p in ps if p.state.abbreviation != 'D']
        return ps

    @staticmethod
    def get_prescheduled_times(start, end, project = None):
        """
        Returns a list of binary tuples of the form (start, end) that
        describe when this project cannot observe because other 
        projects already have scheduled telescope periods during
        the time range specified by the start and end arguments.
        NOTE: this is functionally identical to 
        Project.get_prescheduled_times, but uses a DB query to
        improve performance; Project cannot do this becuase the query
        causes circular references.
        """

        def truncatePeriodRange(p, start, end):
            "we don't care about periods outside of range"
            s = max(p.start, start)
            e = min(p.end(), end)
            return (s, e) 

        # first query DB simply by the time range
        minutes = timedelta2minutes(end - start)
        ps1 = Period.get_periods(start, minutes)

        # now filter out other stuff
        pId = None
        if project is not None:
            pId = project.id
        scheduled = Period_State.get_state('S')
        times = [truncatePeriodRange(p, start, end) for p in ps1 \
            if p.session.project.id != pId \
            and p.state == scheduled \
            and AnalogSet.overlaps((p.start, p.end()), (start, end))]
        return sorted(AnalogSet.unions(times))

    @staticmethod
    def get_prescheduled_days(start, end, project = None):
        return range_to_days(Period.get_prescheduled_times(start
                                                         , end
                                                         , project = project))

    @staticmethod
    def day_is_prescheduled(day, project = None):
        nextDay = day + timedelta(days = 1)
        return len(Period.get_prescheduled_days(day
                                              , nextDay
                                              , project = project)) > 0
    
    @staticmethod
    def create(*args, **kws):
        """
        Recomended way of 'overriding' the constructor.  Here we want to make
        sure that all new Periods init their rcvrs correctly.
        """
        p = Period(**kws)
        # don't save & init rcvrs unless you can
        if not kws.has_key("session"):
            # need the session first!
            return p
        p.save()
        return p
            
    @staticmethod
    def get_periods_by_observing_type(start, end, ot):
        typeQ = models.Q(session__observing_type__type = ot)
        start_endQ = models.Q(start__gte = start) & models.Q(start__lte = end)
        p = Period.objects.filter(typeQ & start_endQ)
        return p
        
    @staticmethod    
    def in_time_range(begin, end, ignore_deleted = True):
        """
        Returns all periods in a time range, taking into account that periods
        can overlap into the first day.
        """
        ps = Period.objects.filter(start__gt = begin - timedelta(days = 1)
                                 , start__lt = end).order_by('start')
        ps = [p for p in ps if p.end() > begin]

        if ignore_deleted:                      
            ps = [p for p in ps if p.state.abbreviation != 'D']

        return ps

    @staticmethod
    def publish_periods(start, duration):

        periods = Period.get_periods(start, duration)
        for p in periods:
            
            if p.session.observing_type != Observing_Type.objects.get(type = "maintenance"):
                p.publish()
                p.save()

    @staticmethod
    def delete_pending(start, duration):
        """
        Removes any periods falling in the given time range that are:
           * from open sessions
           * from windowed sessions, but are not the default period
        """


        for p in Period.get_periods(start, duration):
            if p.isPending() and \
                (p.session.isOpen() or \
                    (p.session.isWindowed() and \
                        not p.is_windowed_default())):
                p.delete()            
      
    @staticmethod
    def restore_electives(start, duration):
        """
        Looks for any elective periods in the deleted state, 
        and brings them back to pending.
        """

        for p in Period.get_periods(start
                                  , duration
                                  , ignore_deleted = False):
            if p.isDeleted() and p.session.isElective():
                p.state = Period_State.get_state("P") 
                p.save()

    @staticmethod
    def restore_windows(start, duration):
        """
        Looks for any windowed periods in the deleted state, 
        and brings them back to pending if:
            * a default period 
            * from a non-gauranteed window
        """

        for p in Period.get_periods(start
                                  , duration
                                  , ignore_deleted = False):

            if p.isDeleted() and p.session.isWindowed() and \
                p.is_windowed_default() and not p.session.guaranteed():
                    p.state = Period_State.get_state("P") 
                    p.save()                
