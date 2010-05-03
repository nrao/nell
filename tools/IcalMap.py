from sesshuns.models import *
from icalendar       import Calendar, Event, UTC
from datetime        import datetime, timedelta

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
                IcalMap.createReservationEvent(user.username, count, start, end))
            count += 1

    def writeSchedule(self, filepath):
        f = open(filepath, 'wb')
        f.write(self.cal.as_string())
        f.close()

    def getSchedule(self):
        return self.cal.as_string()
