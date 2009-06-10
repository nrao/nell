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

        periods = Period.objects.all()
        for p in periods:
            event = Event()
            event['uid'] = str(p.id)
            start = datetime(p.start.year, p.start.month, p.start.day,
                             p.start.hour, p.start.minute, p.start.second,
                             tzinfo = UTC)
            event.add('dtstart', start)
            event.add('dtend', start + timedelta(hours = p.duration))
            event.add('dtstamp', start)
            event.add('summary', "%s in %s (%s) %.3f GHz" %
                                 (p.session.name
                                , p.session.project.name
                                , p.session.project.pcode
                                , p.session.frequency
                                 )
                     )
            event.add('description', "%s:  This telescope period has a duration of %.2f hours. The receiver requirements for this telescope period are %s. The cover page containing all project details is at http://gbrescal.gb.nrao.edu/gbtobs/proposals.dbw?view=viewproposal&propcode=%s" %
                                      (p.session.name
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

#${item.allocation.project.get_title()}. This telescope period has a duration of ${item.duration / 60.0} hours.\nThe observer listed as first contact is ${item.allocation.project.getProjectFirstContact().lastName}.\nThe receiver in use for this telescope period is ${item.allocation.getReceiverNames()}.\nTo see the cover page for all project details, click ${"http://gbrescal.gb.nrao.edu/gbtobs/proposals.dbw?view=viewproposal&propcode=" + item.allocation.project.name}
