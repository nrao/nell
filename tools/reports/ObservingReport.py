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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime        import date, datetime, timedelta
from scheduler.models import *
from utilities       import TimeAgent

import calendar

ALL_PERIODS = [p for p in Period.objects.all() if p.session.project.is_science() and (p.isScheduled() or p.isCompleted())]

def getPeriods():
    return ALL_PERIODS

def normalizePeriodStartStop(period, dt):
    """
    Returns the start/stop time for a period ensuring it stays within the 
    given month.
    """
    start = TimeAgent.utc2est(period.start)
    if start.month != dt.month:
        start = datetime(dt.year, dt.month, 1, 0, 0, 0)

    stop = TimeAgent.utc2est(period.end())
    if stop.month != dt.month:
        _, day = calendar.monthrange(dt.year, dt.month)
        stop = datetime(dt.year, dt.month, day, 23, 59, 59)

    return start, stop

def filterPeriodsByDate(start):
    "Returns the periods within a given month and year."
    _, day = calendar.monthrange(start.year, start.month)
    stop   = datetime(start.year, start.month, day, 23, 59, 59)
    ustart = TimeAgent.est2utc(start)
    ustop  = TimeAgent.est2utc(stop)

    periods = []
    for p in ALL_PERIODS:
        if (p.start >= ustart or p.end() > ustart) and p.start < ustop:
            start, stop = normalizePeriodStartStop(p, start)
            periods.append([p, start, stop])

    return periods

def generateReport(label, periods):
    outfile = open("./GBTObservingReport.txt", 'w')

    outfile.write("GBT observing report for %s\n" % label)
    outfile.write("Project ID\tScheduled (hrs)\tObserved (hrs)\n")

    scheduled = {}
    observed  = {}
    for p in periods:
        period, start, stop = p
        pcode = period.session.project.pcode
        scheduled[pcode] = scheduled.get(pcode, 0) + (stop - start).seconds / 3600.
        observed[pcode] = observed.get(pcode, 0) + (stop - start).seconds / 3600. - period.accounting.lost_time()

    projectNames = scheduled.keys()
    projectNames.sort()
    for p in projectNames:
        s, o = scheduled[p], observed[p]
        outfile.write("%s\t%.2f\t%.2f\n" % (p, s, o))
    outfile.write("Total\t%.2f\t%.2f\n" % (sum([scheduled[p] for p in scheduled.keys()]), sum([observed[p] for p in observed.keys()])))

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

    periods = []
    for m in months:
        periods.extend(filterPeriodsByDate(datetime(year, m, 1)))

    generateReport('Q%d FY %d' % (quarter, fiscal_year), periods)
