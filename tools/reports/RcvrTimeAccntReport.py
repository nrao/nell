#! /usr/bin/env python

from datetime import datetime
from django.core.management import setup_environ
import settings, sys
setup_environ(settings)

from scheduler.models              import *

# From Story:
# https://www.pivotaltracker.com/story/show/9267975
#
#We need to report, over a given time range, the time accounting for receivers. Details:
#   * Use the receivers associated with a period. If more then one receivers is associated, split the time evenly (ex: if 'L, X', L gets 1/2 the time, X gets the other 1/2).
#   * Times to report: Time Billed, Lost Time of that Period.
#
#Example: if Period A has a time billed of 2 hrs, and lost time of 1 hr, and used rcvrs 'L, X', then:
#L time billed: 1 hr
#X time billed: 1 hr
#L lost time: 0.5 hr
#X lost time: 0.5 hr
#
#Anything more complicated then this and we'll need a PR.

class RcvrTimeAccntReport():

    def __init__(self, filename = None):

        self.reportLines = []
        self.quietReport = False
        self.filename = filename

    def add(self, lines):
        "For use with printing reports"
        if not self.quietReport:
            print lines
        self.reportLines += lines

    def printData(self, data, cols, header = False):
        "For use with printing reports."
        self.add(" ".join([h[0:c].rjust(c) for h, c in zip(data, cols)]) + "\n")
        if header:
            self.add(("-" * (sum(cols) + len(cols))) + "\n")

    def writeReport(self):
        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)

    # Note: this does the logic AND the reporting.  It would be nice 
    # seperate out the logic so that we can unit test it easier
    def report(self, start, end):

        self.add("Receiver Time Accounting Report (in Hours)\n")
        self.add("For time range %s - %s\n\n" % (start, end))

        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")
        deleted   = Period_State.get_state("D")

        # get all the periods that overlap this time range
        duration = ((end-start).days * 24.0 * 60.0) + ((end - start).seconds / 60.0) # minutes
        periods = Period.get_periods(start, duration, ignore_deleted = True)
        # filter out the pending
        ps = [p for p in periods if p.state == scheduled]

        # for testing
        #for p in ps:
        #    print "Period (%s): %s-%s, %5.2f hrs, Rcvrs: %s" % (p.state, p.start, p.end(), p.duration, p.receiver_list())
        #    print p.accounting

        rx = Receiver.objects.all()

        glossary = {
            "SC" : "Scheduled"
          , "TB" : "Time Billed (OT - NB)"
          , "NB" : "Not Billed"
          , "OT" : "Observed (SC - OS - LT)"
          , "LT" : "Lost Time"
          , "OS" : "Other Session"
                   }

        self.add("Key:\n")
        for k, v in glossary.items():
            self.add("    %s : %s\n" % (k, v))
        self.add("\n")

        cols = [5, 9, 9, 9, 9, 9, 9]
        data = ["Rcvr", "SC", "TB", "NB", "OT", "LT", "OS"]
        self.printData(data, cols, True)

        # report per receiver
        for r in rx:
            tb = lt = sc = nb = ot = os = 0.0
            for p in ps:
                if r in p.receivers.all():
                    shareFactor = len(p.receivers.all())
                    sc += (p.accounting.scheduled/shareFactor)
                    tb += (p.accounting.time_billed()/shareFactor)
                    nb += (p.accounting.not_billable/shareFactor)
                    ot += (p.accounting.observed()/shareFactor)
                    lt += (p.accounting.lost_time()/shareFactor)
                    os += (p.accounting.other_session()/shareFactor)
            data = [r.abbreviation
                  , self.str(sc)
                  , self.str(tb)
                  , self.str(nb)
                  , self.str(ot)
                  , self.str(lt)
                  , self.str(os)
                   ]
            self.printData(data, cols)

        self.writeReport()

    def str(self, flt):
        return "%7.2f" % flt

if __name__ == '__main__':
   
    help = """
Default time range is the last week, or supply time range:
   -start="YYYY-MM-DD"
   -end="YYYY-MM-DD"
    """
    
    if len(sys.argv) not in [1, 3]:
        print "Supply no args, or just -start and -end"
        print help
        sys.exit(0)

    if len(sys.argv) == 1:
        # default time range
        end = datetime.now()
        start = end - timedelta(days = 7)
    else:
        # parse the keywords
        for arg in sys.argv[1:]:
            parts = arg.split("=")
            if len(parts) != 2:
                print "argument invalid: %s" % arg
                print help
                sys.exit(0)
            key = parts[0][1:]
            if key not in ["start", "end"]:
                print "argument invalid: %s" % arg
                print help
                sys.exit(0)
            dt = datetime.strptime(parts[1].strip(), "%Y-%m-%d")
            if key == "start":
                start = dt
            else:
                end = dt
  
    # now produce the report
    RcvrTimeAccntReport(filename = "RcvrTimeAccntReport.txt").report(start, end)            
