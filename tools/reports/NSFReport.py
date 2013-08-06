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
from scheduler.models import Period
from utilities       import TimeAgent

import calendar


def getPeriods():
    return [p for p in Period.objects.all().order_by('start') if p.isScheduled() or p.isCompleted()]

def filterPeriods(periods, condition):
    "Filters periods according to some critia, e.g. is science?"
    return [p for p in periods if eval(condition)]
    

def filterPeriodsByDate(start):
    "Returns the periods within a given month and year."
    _, day = calendar.monthrange(start.year, start.month)
    stop  = datetime(start.year, start.month, day, 23, 59, 59)
    ustart = TimeAgent.est2utc(start)
    ustop  = TimeAgent.est2utc(stop)
    return [p for p in getPeriods() \
            if (p.start >= ustart or p.end() > ustart) and p.start < ustop]

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

def getTime(periods, month):
    periods.sort(key = lambda x: x.start)
    return sum([TimeAgent.timedelta2frachours(stop - start) \
                 for start, stop in [normalizePeriodStartStop(p, month) \
                                     for p in periods]])

def getScheduledTime(periods, month):
    "Returns scheduled astronomy time for this month."
    return getTime(filterPeriods(periods, 'p.session.project.is_science()')
                 , month)

def getDowntime(periods, month):
    "This does not use getTime because lost time must be handled carefully"
                                     
    ps =  filterPeriods(periods, 'p.session.project.is_science()')
    ps.sort(key = lambda x: x.start)
    total = 0.0
    for p in ps:
        start, stop = normalizePeriodStartStop(p, month)
        hrs = TimeAgent.timedelta2frachours(stop - start)
        # We must normalize the lost time as well
        lostTime = (hrs/p.duration) * p.accounting.lost_time()
        total += lostTime
    return total 


def getMaintenance(periods, month):
    return getTime(filterPeriods(periods, 'p.session.project.is_maintenance() and not p.session.project.is_shutdown()')
                 , month)

def getTesting(periods, month):
    return getTime(filterPeriods(periods
                              , 'p.session.project.is_test() or p.session.project.is_commissioning() or p.session.project.is_calibration()')
                 , month)

def getShutdown(periods, month):
    return getTime(filterPeriods(periods, 'p.session.project.is_shutdown()')
                 , month)

def printSummary(outfile, label, items):
    outfile.write("%s %s %s %s %s\n" % \
                  (label
                 , ("%.2f" % sum(items)).center(8)
                 , ("%.2f" % items[0]).center(8)
                 , ("%.2f" % items[1]).center(8)
                 , ("%.2f" % items[2]).center(8)))

def GenerateReport(label, months):
    assert len(months) == 3, "Are we still doing quarters?"

    outfile = open("./NSFReport.txt", 'w')

    outfile.write("GBT %s   %s %s %s %s\n" % \
                  (label
                 , 'Total'
                 , months[0].strftime("%B").center(8)
                 , months[1].strftime("%B").center(8)
                 , months[2].strftime("%B").center(8)))

    scheduled   = []
    downtime    = []
    astronomy   = []
    maintenance = []
    testing     = []
    shutdown    = []

    for m in months:
        ps = filterPeriodsByDate(m)
        scheduled.append(getScheduledTime(ps, m))
        downtime.append(getDowntime(ps, m))
        astronomy.append(scheduled[-1] - downtime[-1])
        maintenance.append(getMaintenance(ps, m))
        testing.append(getTesting(ps, m))
        shutdown.append(getShutdown(ps, m))

    printSummary(outfile, "Scheduled   ", scheduled)
    printSummary(outfile, "   Astronomy", astronomy)
    printSummary(outfile, "   Downtime ", downtime)
    printSummary(outfile, "Maintenance ", maintenance)
    printSummary(outfile, "Test        ", testing)
    printSummary(outfile, "Shutdown    ", shutdown)

    total = zip(scheduled, maintenance, testing, shutdown)
    totalHrs = sum([sum(t) for t in total])
    outfile.write("%s %s %s %s %s\n" % \
                  ('Total Hours '
                 , ("%.2f" % totalHrs).center(8)
                 , ("%.2f" % sum(total[0])).center(8)
                 , ("%.2f" % sum(total[1])).center(8)
                 , ("%.2f" % sum(total[2])).center(8)))

    # basic error checking             
    now = datetime.now()
    thisMonth = datetime(now.year, now.month, 1)
    for i, m in enumerate(months):
        _, monthNumDays = calendar.monthrange(year, m.month)             
        monthHrs = monthNumDays * 24.0              
        monthTotal = sum(total[i])
        if abs(monthTotal - monthHrs) > 1e-3 and m < thisMonth:
            outfile.write("WARNING: Total number of hours for %s does not equal expected calendar hours of %d\n" % (m.strftime("%B"), monthHrs))
        
    outfile.close()

def show_help():
    print "\nThe arguments to NSFReport are:"
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

    GenerateReport('Q%dFY%d' % (quarter, fiscal_year)
                 , [datetime(year, m, 1) for m in months])
