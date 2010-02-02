from sesshuns.models import *
from icalendar       import Calendar, Event
from datetime        import datetime, timedelta
from icalendar       import UTC # timezone

class IcalMap:

    """
    Extracts Periods from the database and produces a representative
    iCal in the specified file.
    """

    def __init__(self):
        self.cal = Calendar()
        self.cal.add('prodid', '-//My calendar product//mxm.dk//')
        self.cal.add('version', '2.0')
        self.cal.add('x-wr-calname;value=text', 'GBT Schedule')
        self.cal.add('summary', 'GBT Schedule')
        self.cal.add('calscale', 'GREGORIAN')

        # this calendar only displays Scheduled periods
        all = Period.objects.all()
        periods = [p for p in all if p.state.abbreviation == 'S']
        now = datetime.utcnow()
        for p in periods:
            event = Event()
            event['uid'] = str(p.id) + "periodofgbtdss"
            start = datetime(p.start.year, p.start.month, p.start.day,
                             p.start.hour, p.start.minute, p.start.second,
                             tzinfo = UTC)
            event.add('dtstart', start)
            event.add('dtend', start + timedelta(hours = p.duration))
            event.add('dtstamp', now)
            name = p.session.project.pcode in p.session.name and p.session.name or (p.session.name + ' of ' + p.session.project.pcode)
            event.add('summary', "%s at %.3f GHz (%s UTC)" %
                                 (name
                                , p.session.frequency
                                , start.strftime("%Y/%m/%d %H:%M")
                                 )
                     )
            event.add('description', "%s. This telescope period has a duration of %.2f hours. The receiver requirements for this telescope period are %s. The cover page containing all project details is at http://gbrescal.gb.nrao.edu/gbtobs/proposals.dbw?view=viewproposal&propcode=%s" %
                                      (p.session.project.name
                                     , p.duration
                                     , p.session.receiver_list()
                                     , p.session.project.pcode
                                      )
                     )
            event.add('priority', 9)
            self.cal.add_component(event)

    def writeSchedule(self, filepath):
        f = open(filepath, 'wb')
        f.write(self.cal.as_string())
        f.close()

    def getSchedule(self):
        return self.cal.as_string()
