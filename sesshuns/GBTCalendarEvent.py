######################################################################
#
#  GBTCalendarEvent.py - this is a GBT Schedule calendar event adapter.
#  Events may consist of: science periods, maintenance periods, a
#  non-maintenance-period maintenance event, etc.  This adapter will
#  contain all the attributes and functions expected from a calendar
#  event: start time, stop time, etc.
#
#  Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
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

from django.core.exceptions import ObjectDoesNotExist
from scheduler.models       import *
from sesshuns.models        import *
from datetime               import datetime, timedelta

import inspect

from nell.utilities   import TimeAgent

######################################################################
# CalEvent(object)
#
# A base calendar event class for objects that contains whatever thing
# one wishes to display on the GBT Schedule calendar.  The enclosed
# object may be a science period, maintenance period, maintenance
# elective, stand-alone maintenance event(s), etc.
#
######################################################################

class CalEvent(object):

    '''
    GBT Schedule calendar event.
    '''

    def __init__(self, start_cutoff, end_cutoff, moc_met, TZ):
        self.start_cutoff = start_cutoff
        self.end_cutoff = end_cutoff
        self.moc_met = moc_met
        self.TZ = TZ
        self._mas = []
        self.contained = None

    def __eq__(self, other):
        if type(self) == type(other):
            return self.contained == other.contained
        else:
            return False

    # define less-than (<) for sorting purposes
    def __lt__(self, other):
        return self.start() < other.start()

    # these methods all return some value and take no parameters, as
    # they are intended to be used from within a template.  Methods
    # that raise 'TypeError' should be overridden.

    # returns the start time of the event
    def start(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # returns the end time of the event
    def end(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # returns a string (pcode)
    def pcode(self):
        return ""

    # returns a string (project notes)
    def project_notes(self):
        return ""
    
    # returns a string (project title)
    def project_title(self):
        return ""

    # the responsible person, a User object
    def principal_investigator(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # other observers
    def sactioned_observers(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # friends
    def friends(self):
        return []

    # returns the project/observing type.  This one must be
    # implemented, as there is no reasonable default.
    def project_type(self):
        return ''

    # returns the contained object's database ID.
    def contained_id(self):
        return self.contained.id

    # returns true if project is science
    def is_science(self):
        return self.project_type() == 'A'

    # returns true if the project is non-science.
    def non_science(self):
        return self.project_type() != 'A'

    def is_maintenance(self):
        return self.project_type() == 'M'

    def is_calibration(self):
        return self.project_type() == 'K'

    def is_comissioning(self):
        return self.project_type() == 'C'

    def is_concurrent(self):
        return self.project_type() == 'I'

    def is_shutdown(self):
        return self.project_type() == 'D'

    # returns True if MOC degraded after period started. Should be
    # overrided if contained object cares about MOC.
    def moc_degraded(self):
        return False

    # returns True if MOC not met in the 30 minute period before
    # start. Should be overrided if contained object cares about MOC.
    def moc_reschedule(self):
        return False

    # returns boolean True if the event is cut off (crosses midnight)
    def cutoff(self):
        return self.start_cutoff or self.end_cutoff

    # returns a boolean to indicate whether there is lost time.
    def has_lost_time(self):
        return False

    # returns a string, the lost time
    def get_lost_time(self):
        return ''

    # returns a list of maintenance activities.
    def mas(self):
        return None

    # returns a list of receivers involved with this event
    def receiver_list(self):
        return ""

    def get_rcvr_ranges(self):
        return ""

######################################################################
# CalEventPeriod.  A CalEvent that wraps a DSS Period object.  Usually
# the periods are science periods, but this class deals with
# non-science periods as well, such as calibration, test, etc.
# Whatever the observing type, the code in this class assumes an
# underlying period.  (For maintenance, use either
# CalEventFixedMaintenance or CalEventFloatingMaintenance.)
######################################################################

class CalEventPeriod(CalEvent):
    """
    This calendar event handles periods.
    """

    def __init__(self, contained,  start_cutoff = False, end_cutoff = False,
                 moc_met = True, TZ = 'ET'):
        super(CalEventPeriod, self).__init__(start_cutoff, end_cutoff, moc_met, TZ)
        self.contained = contained


    def start(self):
        start = self.contained.start

        if self.TZ == 'ET':
            start = TimeAgent.utc2est(start)

        if self.start_cutoff:
            start = datetime(start.year, start.month, start.day) + timedelta(days = 1)

        return start

    def end(self):
        end = self.contained.end()
        end = TimeAgent.utc2est(end) if self.TZ == 'ET' else end
        end = datetime(end.year, end.month, end.day, 0, 0) + timedelta(days = 1)\
            if self.end_cutoff else end

        return end


    # returns a string (pcode)
    def pcode(self):
        return self.contained.session.project.pcode

    # returns a string (project notes)
    def project_notes(self):
        return self.contained.session.project.notes

    # returns a string (project title)
    def project_title(self):
        if self.is_science():
            return self.contained.session.project.name

        return self.contained.session.name

    # returns the name of the responsible person
    def principal_investigator(self):
        return self.contained.session.project.principal_investigator()

    def sanctioned_observers(self):
        return self.contained.session.project.get_sanctioned_observers()

    def friends(self):
        fs = [f for f in self.contained.session.project.friend_set.all()]
        return fs

    def moc_degraded(self):
        "Popups are issued when a period has started and if moc is False."
        now = datetime.utcnow()
        if not self.contained.moc_ack and \
           now > self.contained.start and now < self.contained.end():
            return not self.contained.moc_met()
        else:
            return False


    def moc_reschedule(self):
        "Popups are issued when start <= 30 minutes if moc is False."
        diff = self.contained.start - datetime.utcnow()
        if not self.contained.moc_ack and \
           diff >  timedelta(seconds = 0) and \
           diff <= timedelta(minutes = 30):
            return not self.contained.moc_met()
        else:
            return False


    def get_lost_time(self):
        lt = []
        if self.contained.accounting.lost_time_weather > 0:
            lt.append("weather = %2.2f hr" % self.contained.accounting.lost_time_weather)
        if self.contained.accounting.lost_time_rfi > 0:
            lt.append("RFI = %2.2f hr" % self.contained.accounting.lost_time_rfi)
        if self.contained.accounting.lost_time_other > 0:
            lt.append("other = %2.2f hr" % self.contained.accounting.lost_time_other)

        return ", ".join(lt)

    def has_lost_time(self):
        return self.contained.accounting.lost_time() > 0.


    # returns the project/observing type.  The types: 'A', 'C', 'K',
    # 'T', for astronomy, commissioning, calibration, and test
    def project_type(self):
        project = self.contained.session.project

        if project.project_type.type == 'science':
            p_type = 'A'
        else:
            if project.is_commissioning():
                p_type = 'C'
            elif project.is_calibration():
                p_type = 'K'
            elif project.is_shutdown():
                p_type = 'D'
            else:
                p_type = 'T'

        return p_type

    def receiver_list(self):
        return self.contained.receiver_list()


    def get_rcvr_ranges(self):
        return self.contained.get_rcvr_ranges()


######################################################################
# CalEventIncidental. A CalEvent that wraps a
# Maintenance_Activity, a list of Maintenance_Activity, or a QuerySet
# of Maintenance_Activity.  This allows Maintenance_Activity objects
# not associated with any periods to be displayed by the calnedar.
# The calendar doesn't care that there is no period behind this set.
######################################################################

class CalEventIncidental(CalEvent):
    """
    This calendar event handles one or more maintenance activities on
    their own. Maintenance_Activity objects are normally associated
    with maintenance periods, but sometimes it is desirable to use
    them independent of maintenance periods. 'contained' may be passed
    in as a single Maintenance_Activity, a list of
    Maintenance_Activities, or a QuerySet returning
    Maintenance_Activity.
    """

    def __init__(self, contained, start_cutoff = False, end_cutoff = False, moc_met = True, TZ = 'ET'):
        super(CalEventIncidental, self).__init__(start_cutoff, end_cutoff, moc_met, TZ)
        if type(contained).__name__ == 'list':
            self.contained = contained
        elif type(contained).__name__ == 'QuerySet':
            self.contained = [p for p in contained]
        else:
            self.contained = [contained]

        self.contained.sort(cmp = lambda x, y: cmp(x.get_start(), y.get_start()))

    def start(self):
        return self.contained[0].get_start(self.TZ)

    def end(self):
        return self.contained[-1].get_end(self.TZ)

    # returns a string (pcode)
    def pcode(self):
        return 'Maintenance'

    # returns a string (project title)
    def project_title(self):
        return 'Incidental non-observational activity'

    # returns the name of the responsible person.  In the case of
    # unattached maintenance activities, it is presumed to be the same
    # person as the one responsible for the "Maintenance" project.
    def principal_investigator(self):
        try:
            prj = Project.objects.get(pcode = "Maintenance")
            user = prj.principal_investigator()
        except ObjectDoesNotExist: # return something.
            user = User.objects.get(last_name__contains = "account")

        return user


    def sanctioned_observers(self):
        try:
            prj = Project.objects.get(pcode = "Maintenance")
            observers = prj.get_sanctioned_observers()
        except ObjectDoesNotExist: # return something.
            observers = []

        return observers


    def friends(self):
        prj = Project.objects.get(pcode = "Maintenance")
        fs = [f for f in prj.friend_set.all()]
        return fs

    # returns 'I', for Incidental activity concurrent with other
    # observations.  If this event (CalEventIncidental) is used, it is
    # used to denote Maintenance Activities that are not attached to a
    # Period.  This is always for an activity that is concurrent with
    # normal observations and not part of regularly scheduled
    # maintenance.
    def project_type(self):
        return 'I'


    def mas(self):
        return self.contained

######################################################################
# CalEventFloatingMaintenance.  A CalEvent that wraps a DSS floating
# maintenance event.  There is one of these for every maintenance
# Elective in a given week.  They are not attached to the Elective or
# to a Period, but stand alone, so some assumptions are made: that it
# is a maintenance event; that it is floating; that it starts on
# Monday of that week.
#
# Fixed maintenance events should be represented by
# CalEventFixedMaintenance.
######################################################################

class CalEventFloatingMaintenance(CalEvent):
    """
    This calendar event handles floating maintenance events.
    """

    def __init__(self, contained,  start_cutoff = False, end_cutoff = False,
                 moc_met = True, TZ = 'ET'):
        super(CalEventFloatingMaintenance, self).__init__(start_cutoff, end_cutoff, moc_met, TZ)
        self.contained = contained

    ######################################################################
    # Sorting rules:
    #
    # If this is being compared to another floating maintenance
    # activity group event, and they have the same start time
    # (i.e. they belong to the same week), then sort by rank: 'A' is
    # less than 'B' etc.  Otherwise sort by start time.
    ######################################################################

    def __lt__(self, other):
        if type(other).__name__ == 'CalEventFloatingMaintenance':
            if self.start() == other.start():  # same week
                return self.contained.rank < other.contained.rank
        else:
            return super(CalEventFloatingMaintenance, self).__lt__(other)


    def start(self):
        w = self.contained.get_week()
        # assume start time of 8:00 ET, to be converted to UT below,
        # if necessary.
        dt = datetime(w.year, w.month, w.day, 8)

        if self.TZ != 'ET':
            dt = TimeAgent.etc2utc(dt)
            
        return dt 

    def end(self):
        return self.start() + timedelta(seconds = (8.5 * 3600))

    # returns a string (pcode)
    def pcode(self):
        return "Maintenance"

    # returns a string (project title)
    def project_title(self):
        return "Maintenance Period %s" % (self.contained.rank)

    def principal_investigator(self):
        try:
            prj = Project.objects.get(pcode = "Maintenance")
            user = prj.principal_investigator()
        except ObjectDoesNotExist: # return something.
            user = User.objects.get(last_name__contains = "account")

        return user


    def sanctioned_observers(self):
        try:
            prj = Project.objects.get(pcode = "Maintenance")
            observers = prj.get_sanctioned_observers()
        except ObjectDoesNotExist: # return something.
            observers = []

        return observers


    def friends(self):
        prj = Project.objects.get(pcode = "Maintenance")
        fs = [f for f in prj.friend_set.all()]
        return fs

    # returns the project/observing type.
    # The types: 'A', 'M', 'C', 'K', 'T', for astronomy,
    # maintenance, commissioning, calibration, and test
    def project_type(self):
        return 'M'

    # returns a list of maintenance activities.  self._mas caches
    # results, thus the code used to obtain the maintenance activity
    # set is executed only on the first call of this function, whereas
    # the template may call this several times.
    def mas(self):
        if not self._mas:
            self._mas = self.contained.get_maintenance_activity_set()
        return self._mas

######################################################################
# CalEventFixedMaintenance.  A CalEvent that wraps a DSS fixed
# maintenance period.  The underlying object is a maintenance activity
# group.
######################################################################

class CalEventFixedMaintenance(CalEvent):
    """
    This calendar event handles fixed maintenance periods.
    """

    def __init__(self, contained,  start_cutoff = False, end_cutoff = False,
                 moc_met = True, TZ = 'ET'):
        super(CalEventFixedMaintenance, self).__init__(start_cutoff, end_cutoff, moc_met, TZ)
        self.contained = contained


    def start(self):
        start = self.contained.period.start

        if self.TZ == 'ET':
            start = TimeAgent.utc2est(start)

        if self.start_cutoff:
            start = datetime(start.year, start.month, start.day) + timedelta(days = 1)

        return start

    def end(self):
        end = self.contained.period.end()
        end = TimeAgent.utc2est(end) if self.TZ == 'ET' else end
        end = datetime(end.year, end.month, end.day, 0, 0) + timedelta(days = 1)\
            if self.end_cutoff else end

        return end


    # returns a string (pcode)
    def pcode(self):
        return self.contained.period.session.project.pcode

    # returns a string (project notes)
    def project_notes(self):
        return self.contained.period.session.project.notes

    # returns a string (project title)
    def project_title(self):
        return self.contained.period.session.name

    # returns the name of the responsible person
    def principal_investigator(self):
        return self.contained.period.session.project.principal_investigator()

    def sanctioned_observers(self):
        return self.contained.period.session.project.get_sanctioned_observers()

    def friends(self):
        fs = [f for f in self.contained.period.session.project.friend_set.all()]
        return fs

    # returns the project/observing type, which is 'M' for
    # maintenance or 'D' for shutdown.
    def project_type(self):
        if self.contained.period.session.project.is_shutdown():
            return 'D'
        return 'M'

    # returns a list of maintenance activities.  self._mas caches
    # results, thus the code used to obtain the maintenance activity
    # set is executed only on the first call of this function, whereas
    # the template may call this several times.
    def mas(self):
        if self.contained.period.session.observing_type.type == "maintenance" and not self._mas:
            self._mas = self.contained.get_maintenance_activity_set()
        return self._mas

    def receiver_list(self):
        return self.contained.period.receiver_list()


    def get_rcvr_ranges(self):
        return self.contained.get_rcvr_ranges()

