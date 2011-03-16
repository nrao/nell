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
from models                 import *
from datetime               import datetime, timedelta

import inspect

from utilities   import TimeAgent

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
        self.fmname = None
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
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # returns a string (project notes)
    def project_notes(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # returns a string (project title)
    def project_title(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

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
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # returns the project/observing type.  This one must be
    # implemented, as there is no reasonable default.
    def project_type(self):
        raise TypeError('Abstract method \'' + self.__class__.__name__ \
                            + '.' + inspect.stack()[0][3] + '\' called')

    # returns the contained period's database ID.  This is always
    # either the Period's ID, or 0 if the contained object is not a
    # period.
    def period_id(self):
        return 0

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
        self._mas

    # returns a list of receivers involved with this event
    def receiver_list(self):
        return []

    def get_rcvr_ranges(self):
        return ""

    def set_fm_name(self, fmname):
        """
        sets the floating maintenance event name: 'A' for the first,
        'B' for second, etc.
        """
        self.fmname = fmname

    def is_floating_maintenance(self):
        return False

######################################################################
# CalEventPeriod.  A CalEvent that wraps a DSS Period object.  Usually
# the periods are science periods, but this class deals with
# non-science periods as well, such as calibration, maintenance, test,
# etc.  Whatever the observing type, the code in this class assumes an
# underlying period.
######################################################################

class CalEventPeriod(CalEvent):
    """
    This calendar event handles periods.
    """

    def __init__(self, contained,  start_cutoff = False, end_cutoff = False,
                 moc_met = True, TZ = 'ETC'):
        super(CalEventPeriod, self).__init__(start_cutoff, end_cutoff, moc_met, TZ)
        self.contained = contained

    ######################################################################
    # Sorting rules:
    #
    #   All maintenance events are directly compared, regardless of
    #   whether they are floating or not (see 'start()' for floating
    #   case).  This is to keep the floating designations ('A', 'B',
    #   'C', etc.) correct even after 'A' gets scheduled.
    #
    #   Any floating maintenance event comes before any other kind of
    #   event for that day. (Usually Monday.  This is by convention,
    #   as the event really isn't really happening on that day)
    #
    #   Otherwise, compare events straight-up by start date/time.
    ######################################################################

    def __lt__(self, other):
        if self.project_type() == "M" and other.project_type() == "M":
            return self.contained.start < other.contained.start
        elif self.is_floating_maintenance() and not other.is_floating_maintenance() \
                and TimeAgent.truncateDt(self.start()) == TimeAgent.truncateDt(other.start()):
            return True
        else:
            return super(CalEventPeriod, self).__lt__(other)


    def start(self):
        if self.is_floating_maintenance():
            delta = timedelta(days = self.contained.start.weekday()) # Monday = 0, Tuesday = 1, etc.
            start = self.contained.start - delta
        else:
            start = self.contained.start

        if self.TZ == 'ET':
            start = TimeAgent.utc2est(start)

        if self.start_cutoff:
            start = datetime(start.year, start.month, start.day) + timedelta(days = 1)

        return start

    def end(self):
        if self.is_floating_maintenance():
            end = self.start() + timedelta(hours = self.contained.duration)
        else:
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
        if self.is_floating_maintenance():
            return "Maintenance Period %s" % (self.fmname)

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

    def period_id(self):
        return self.contained.id

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


    # returns the project/observing type.
    # The types: 'A', 'M', 'C', 'K', 'T', for astronomy,
    # maintenance, commissioning, calibration, and test
    def project_type(self):
        project = self.contained.session.project

        if project.project_type.type == 'science':
            p_type = 'A'
        else:
            if project.is_maintenance():
                p_type = 'M'
            elif project.is_commissioning():
                p_type = 'C'
            elif project.is_calibration():
                p_type = 'K'
            else:
                p_type = 'T'
        return p_type

    # returns a list of maintenance activities.  self._mas caches
    # results, thus the code used to obtain the maintenance activity
    # set is executed only on the first call of this function, whereas
    # the template may call this several times.
    def mas(self):
        if self.contained.session.observing_type.type == "maintenance" and not self._mas:
            self._mas = Maintenance_Activity.get_maintenance_activity_set(self.contained)
        return self._mas

    def receiver_list(self):
        return self.contained.receiver_list()


    def get_rcvr_ranges(self):
        return self.contained.get_rcvr_ranges()


    def is_floating_maintenance(self):
        return self.contained.session.observing_type.type == 'maintenance'\
            and self.contained.isPending()

######################################################################
# CalEventElective.  A CalEvent object that wraps an elective.
# Electives are a way to eventually elect a period from a list of many
# periods; thus this class derives from CalEventPeriod, and only
# contains code that is needed to deal with the elective itself.
######################################################################

class CalEventElective(CalEventPeriod):
    """
    This calendar event handles electives.  Nothing specifically about
    the elective needs to be known by the calendar, so this class
    inherits from the CalEventPeriod class, extracts the period from
    the elective and initializes its base class with the period.  Most
    of the functionality is thus provided by CalEventPeriod.
    """

    def __init__(self, contained,  start_cutoff = False, end_cutoff = False,
                 moc_met = True, TZ = 'ETC'):
        super(CalEventElective, self).__init__(
            self._get_period(contained), start_cutoff, end_cutoff, moc_met, TZ)


    ######################################################################
    # Returns maintenance activity set associated with this event, if
    # the event is a maintenance event.  If the elective has been
    # scheduled, or the pending period with maintenance activities has
    # been deleted, we want to reconcile the maintenance activity set
    # by detaching it (if necessary) from a deleted elective period
    # and reattaching it to the scheduled or next pending elective
    # period.
    ######################################################################
    def mas(self):
        el = self.contained.elective

        # self._mas caches results, thus this is done only once.
        if el.session.observing_type.type == "maintenance" and not self._mas:
            for ep in el.periods.all():
                if ep.maintenance_activity_set.exists():
                    mas = ep.maintenance_activity_set.all()

                    if ep.isDeleted():
                        if el.complete:
                            destination_period = el.scheduledPeriods()
                        else:
                            destination_period = el.pendingPeriods()

                        if destination_period:
                            for m in mas:
                                m.period = destination_period[0]
                                m.save()

        return super(CalEventElective, self).mas()

    def _get_period(self, elective):
        """
        Helper function for class CalEventElective retrieves a period
        from the elective.  If the elective is complete (scheduled),
        it returns the scheduled period.  If it is still pending, it
        returns the first pending period from the list of periods.  If
        deleted, the first deleted period.
        """
        pd = None
        pds = elective.scheduledPeriods()   # see if any scheduled periods first

        if not pds:
            pds = elective.pendingPeriods() # if not get pending periods

            if not pds:
                pds = elective.deletedPeriods()

        pd = pds[0] if pds else None

        return pd

######################################################################
# CalEventMaintenanceActivity. A CalEvent that wraps a
# Maintenance_Activity, a list of Maintenance_Activity, or a QuerySet
# of Maintenance_Activity.  This allows Maintenance_Activity objects
# not associated with any periods to be displayed by the calnedar.
# The calendar doesn't care that there is no period behind this set.
######################################################################

class CalEventMaintenanceActivity(CalEvent):
    """
    This calendar event handles one or more maintenance activities on
    their own. Maintenance_Activity objects are normally associated
    with maintenance periods, but sometimes it is desirable to use
    them independent of maintenance periods. 'contained' may be passed
    in as a single Maintenance_Activity, a list of
    Maintenance_Activities, or a QuerySet returning
    Maintenance_Activity.
    """

    def __init__(self, contained, start_cutoff = False, end_cutoff = False, moc_met = True, TZ = 'ETC'):
        super(CalEventMaintenanceActivity, self).__init__(start_cutoff, end_cutoff, moc_met, TZ)
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
        return 'Non-maintenance-period maintenance activity'

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
        try:
            prj = Project.objects.get(pcode = "Maintenance")
            f = [prj.friend]       # TBF will be friend_s_ soon
        except ObjectDoesNotExist: # return something.
            f = []

        return f


    # returns 'M', as maintenance is the only possibility.
    def project_type(self):
        return 'M'


    def mas(self):
        return self.contained

