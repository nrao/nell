from sesshuns.models import *
from reversion.models import Version
from revisionReport import RevisionReport

class PeriodRevReport(RevisionReport):

    def reportPeriod(self, id, time = None, field = None):
        p = first(Period.objects.filter(id = id))
        self.reportObject(p, time, field)
        print "Diffs: "
        self.reportPeriodDiffs(id)
    
    def reportPeriodDiffs(self, id):
        diffs = []
        p = first(Period.objects.filter(id = id))
        diffs.extend(self.getObjectDiffs(p)) 
        diffs.extend(self.getObjectDiffs(p.accounting)) 
        rps = Period_Receiver.objects.filter(period = p)
        for r in rps:
        #for r in p.receivers.all():
            diffs.extend(self.getObjectDiffs(r))
        for d in diffs:
            print "(%s) field %s: %s -> %s" % (d[0], d[1], d[2], d[3])

