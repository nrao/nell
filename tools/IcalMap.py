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

from icalendar       import Calendar, Event, UTC
from datetime        import datetime, timedelta
from scheduler.models import *

class IcalMap:

    """
    Extracts Periods from the database and produces a representative
    iCal in the specified file.
    """
    @staticmethod
    def createReservationEvent(username, id, start, end):
        event = Event()

        event['uid'] = username + str(id) + "reservationofgbtdss"

        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', datetime.utcnow())
        event.add('summary', 'NRAO Green Bank site reservation')
        event.add('priority', 9)

        return event

    @staticmethod
    def createPeriodEvent(period):
        event = Event()
        event['uid'] = str(period.id) + "periodofgbtdss"
        start = datetime(period.start.year, period.start.month, period.start.day,
                         period.start.hour, period.start.minute, period.start.second,
                         tzinfo = UTC)
        event.add('dtstart', start)
        event.add('dtend', start + timedelta(hours = period.duration))
        event.add('dtstamp', datetime.utcnow())
        name = period.session.project.pcode in period.session.name and period.session.name or (period.session.name + ' of ' + period.session.project.pcode)
        event.add('summary', "%s at %.3f GHz (%s UTC)" %
                             (name
                            , period.session.frequency
                            , start.strftime("%Y/%m/%d %H:%M")
                             )
                 )
        event.add('description', "%s. This telescope period has a duration of %.2f hours. The receiver requirements for this telescope period are %s. The cover page containing all project details is at http://gbrescal.gb.nrao.edu/gbtobs/proposals.dbw?view=viewproposal&propcode=%s" %
                                  (period.session.project.name
                                 , period.duration
                                 , period.session.receiver_list()
                                 , period.session.project.pcode
                                  )
                 )
        event.add('priority', 9)

        return event

    def __init__(self, user = None):
        self.cal = Calendar()
        self.cal.add('prodid', '-//My calendar product//mxm.dk//')
        self.cal.add('version', '2.0')
        self.cal.add('x-wr-calname;value=text', 'GBT Schedule')
        self.cal.add('summary', 'GBT Schedule')
        self.cal.add('calscale', 'GREGORIAN')

        # this calendar only displays Scheduled periods
        periods = [p for p in Period.objects.all() if p.isScheduled()]

        if user: # Personalize this calendar for somebody!
            periods = [p for p in periods \
                       if p.session.project.isInvestigator(user)]
            reservations = user.getReservations()
        else:
            reservations = []

        for p in periods:
            self.cal.add_component(IcalMap.createPeriodEvent(p))

        count = 1
        for start, end in reservations:
            self.cal.add_component(
                IcalMap.createReservationEvent(user.username(), count, start, end))
            count += 1

    def writeSchedule(self, filepath):
        f = open(filepath, 'wb')
        f.write(self.cal.as_string())
        f.close()

    def getSchedule(self):
        return self.cal.as_string()
