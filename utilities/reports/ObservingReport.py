from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime        import datetime
from sesshuns.models import Period
from sets            import Set

import calendar

def getScienceObservations(start, end, projects):
    "Returns observing between two given dates."
    periods  = [p for p in Period.in_time_range(start, end) \
                  if p.session.isScience()]
    for p in periods:
        project = p.session.project.pcode
        if not projects.has_key(project):
            scheduled = 0
            observed  = 0
        else:
            scheduled, observed = projects[project]

        scheduled += p.accounting.scheduled
        observed  += p.accounting.observed()

        projects[project] = (scheduled, observed)

    return projects

def generateReport(quarter, fiscal_year, projects):
    outfile = open("./GBTObservingReport.txt", 'w')

    outfile.write("GBT observing report for Q%d FY%d\n" % (quarter, fiscal_year))
    outfile.write("Project ID\tScheduled (hrs)\tObserved (hrs)\n")

    projectNames = projects.keys()
    projectNames.sort()
    for p in projectNames:
        s, o = projects[p]
        outfile.write("%s\t%f\t%f\n" % (p, s, o))

    outfile.close()

def show_help():
    print "\nThe arguments to ObservingReport are:"
    print "\t<integer quarter> <integer fiscal year>\n\n"

if __name__=='__main__':
    import sys

    if len(sys.argv) != 3:
        show_help()
        sys.exit()

    quarters = {
        1: [10, 11, 12]
      , 2: [1, 2, 3]
      , 3: [4, 5, 6]
      , 4: [7, 8, 9]
    }

    quarter     = int(sys.argv[1])
    fiscal_year = int(sys.argv[2])

    months = quarters[quarter]
    year   = fiscal_year if quarter != 1 else fiscal_year - 1

    projects = {}
    for m in months:
        start  = datetime(year, m, 1) 
        _, day = calendar.monthrange(start.year, start.month)
        end    = datetime(start.year, start.month, day, 23, 59, 59)
        getScienceObservations(start, end, projects)

    generateReport(quarter, fiscal_year, projects)
