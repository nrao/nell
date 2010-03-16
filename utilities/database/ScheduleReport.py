#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *


class ScheduleReport():

    def __init__(self, filename = None):

        self.reportLines = []
        self.quietReport = False
        self.filename = filename

    def add(self, lines):
        "For use with printing reports"
        if not self.quietReport:
            print lines
        self.reportLines += lines

#    def printData(self, data, cols, header = False):
#        "For use with printing reports."
#        self.add(" ".join([h[0:c].rjust(c) for h, c in zip(data, cols)]) + "\n")
#        if header:
#            self.add(("-" * (sum(cols) + len(cols))) + "\n")

    def getSessionTable(self, periods):
        table  = "Start (ET)   |      UT      |  LST  |  (hr) | T | S |    PI     | Rx        | Session\n"
        table += "--------------------------------------------------------------------------------------\n"
        for p in periods:
            if p.session.project.pcode == "Maintenance":
                pi = ""
            else:
                pi = p.session.project.principal_investigator().last_name[:9] if p.session.project.principal_investigator() else "Unknown"

            table += "%s | %s | %s | %5s | %s | %s | %-9s | %-9s | %s\n" % (
                TimeAgent.utc2est(p.start).strftime('%b %d %H:%M') # start (ET)
              , p.start.strftime('%b %d %H:%M') # start (UT)
              , TimeAgent.dt2tlst(p.start).strftime('%H:%M') # LST
              , "%2.2f" % p.duration # dur (Hrs)
              , p.session.session_type.type[0].upper() # sess type
              , p.state.abbreviation # state
              , pi
              , p.session.receiver_list_simple()[:9]
              , p.session.name
            )
        return table

    def report(self, start, days):

        # get the periods from the time range
        duration = days * 24 * 60
        ps = Period.get_periods(start, duration)

        # produce the report
        self.add("Scheduling Report starting at %s for %d days.\n\n" % (start
                                                                      , days))
        table = self.getSessionTable(ps)
        self.add(table)

        # write it out
        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)

def show_help(program):
    print "\nThe arguments to", program, "are:"
    print "\t<integer day> <integer month> <integer year> <integer days>"
    print "and represent the date on which you wish the report to start,"
    print "and for how many days it should continue"
    print "\nAll arguments are required.  Anything else simply won't do."

if __name__ == '__main__':

    #if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
    if len(sys.argv) != 5:
        show_help(sys.argv[0])
        sys.exit()
    else:    
        start = datetime(int(sys.argv[3]), int(sys.argv[2]), int(sys.argv[1]))
        days = int(sys.argv[4])
        ScheduleReport(filename = "ScheduleReport.txt").report(start, days)            
