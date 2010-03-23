from sesshuns.models import *
from reversion.models import Version
from RevisionReport import RevisionReport

class PeriodRevReport(RevisionReport):
    def __init__(self, filename = None):
        super(PeriodRevReport, self).__init__(filename)
       
        self.relatedClasses = ['Period_Accounting'
                              ]

    def reportSessionPeriods(self
                           , sesshun
                           , time = None
                           , field = None
                           , deleted = False
                             ):
        "Reports all periods for a given session"

        # get the periods for this session
        ps = sesshun.period_set.all()
        # include deleted?
        if not deleted:
            ps = [p for p in ps if p.state.abbreviation != "D"]
        for p in ps:
            self.reportPeriod(p.id, time, field)
            
    def reportPeriods(self, start, time = None, field = None, deleted = False):
        "Reports all periods that have given start time"

        # in practice, just one non-deleted period per start time, if any.
        ps = self.getPeriods(start, deleted)
        for p in ps:
            self.reportPeriod(p.id, time, field)

    def getPeriods(self, start, deleted = False):

        ps = Period.objects.filter(start = start)
        if not deleted:
            ps = [p for p in ps if p.state.abbreviation != "D"]
        return ps

    def reportPeriod(self, id, time = None, field = None):
        p = first(Period.objects.filter(id = id))
        self.add("Revision Report for Period: %s\n\n" % p)
        self.reportObject(p, time, field)
        self.add("\nDiffs:\n ")
        self.reportPeriodDiffs(id)
        self.write()
    
    def reportPeriodDiffs(self, id):
        diffs = []
        p = first(Period.objects.filter(id = id))
        self.add("Differences for Period: %s\n\n" % p)
        diffs.extend(self.getObjectDiffs(p)) 
        diffs.extend(self.getObjectDiffs(p.accounting)) 
        rps = Period_Receiver.objects.filter(period = p)
        for r in rps:
        #for r in p.receivers.all():
            diffs.extend(self.getObjectDiffs(r))
        for d in diffs:
            self.add("%s\n" % d)
        self.write()    

    def reportPeriodForTime(self, id, timeStr):
        p = first(Period.objects.filter(id = id))
        self.add("Period: %s at %s\n\n" % (p, timeStr))
        self.reportObjectForTime(p, timeStr)
        self.write() 
