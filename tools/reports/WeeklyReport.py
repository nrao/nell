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

from datetime         import date,datetime,timedelta
from nell.utilities   import TimeAccounting
from scheduler.models import *
from utilities        import TimeAgent
from utilities        import AnalogSet

import calendar

class WeeklyReport:

    def print_values(self, file, values):
        if values == []:
            file.write("\tNone\n")
        else:
            for v in values:
                file.write("\t%s\n" % v)

    def get_observed_time(self, month, periods, condition):
        """
        Returns the total time that the given periods which
        match the given condition lie within the given month.
        """

        duration = 0
        for pd in [p for p in periods if eval(condition)]:
            pstart = pd.start 
            pend   = pd.end() 
            # check typical case - don't overlap the month
            if pstart.month == pend.month:
                if pstart.month == month:
                    duration += (pend - pstart).seconds / 3600.0
            else:
                # our period spans more then a month, see if any
                # of them cover our month
                if pstart.month == month:
                    _, lastday = calendar.monthrange(pstart.year, month)
                    monthEnd = datetime(pstart.year, month, lastday) + timedelta(days = 1)
                    duration += (monthEnd - pstart).seconds / 3600.0
                if pend.month == month:
                    monthStart = datetime(pend.year, pend.month, 1)
                    duration += (pend - monthStart).seconds / 3600.0
        return duration

    def get_obs_time_tuple(self, condition):
        past = self.get_observed_time(
                            self.last_month.month
                          , self.last_periods
                          , condition) 
        present = self.get_observed_time(
                            self.start.month
                          , self.this_periods
                          , condition)
        return (past, present)                  


    def __init__(self, start):

        self.start      = start
        self.outfile    = open("./DssWeeklyReport.txt", 'w')
        self.end        = start + timedelta(days = 7)
        self.next_start = self.end + timedelta(days = 1)
        self.next_end   = self.end + timedelta(days = 7)

        # all scheduled or completed periods
        self.periods    = [p for p in Period.objects.all() if p.state.abbreviation in ("S", "C")]

        self.ta         = TimeAccounting()

        # quantities to calculate
        self.lost_hours = {}
        self.scheduled_hours ={}
        self.backlog_hours = {}
        self.discharge_hours = {}

    def report(self):
        "Calculate all time accounting needed, then print it to report file."

        self.calculate()
        self.output()

    def calculate(self):
        "Calculate all the quantities needed for this report."

        self.currentSemester   = Semester.getCurrentSemester(self.start)
        self.previousSemesters = Semester.getPreviousSemesters(self.start)
        self.futureSemesters   = Semester.getFutureSemesters(self.start)

        # just those scheduled periods in the current week
        self.observed_periods = \
            sorted(set([p for p in self.periods \
                          if AnalogSet.overlaps((p.start, p.end()), (self.start, self.end))]))
        # just those scheduled periods in the upcoming week                  
        self.upcoming_periods = \
            sorted(set([p for p in self.periods \
                          if AnalogSet.overlaps((p.start, p.end())
                                    , (self.next_start, self.next_end))]))

        self.last_month   = self.start - timedelta(days = 31)
        # scheduled periods from last month
        self.last_periods = [p for p in self.periods \
                          if p.start.month == self.last_month.month and \
                             p.start.year  == self.last_month.year]
        # scheduled periods from this month                     
        self.this_periods = [p for p in self.periods \
                          if p.start.month == self.start.month and \
                             p.start.year  == self.start.year]  

        # how does the lost time break down for all the scheduled periods in the current week?
        self.lost_hours["total_time"] = sum([p.accounting.lost_time() for p in self.observed_periods])
        self.lost_hours["weather" ] = sum([p.accounting.lost_time_weather for p in self.observed_periods])
        self.lost_hours["RFI" ] = sum([p.accounting.lost_time_rfi for p in self.observed_periods])
        self.lost_hours["other" ] = sum([p.accounting.lost_time_other for p in self.observed_periods])
        self.lost_hours["billed_to_project" ] = sum([p.accounting.lost_time_bill_project for p in self.observed_periods])

        # how do the scheduled periods break down by type and this
        # and the previous month?
        self.scheduled_hours["astronomy"] = self.get_obs_time_tuple('p.session.project.project_type.type == "science"')
        self.scheduled_hours["maintenance"] = self.get_obs_time_tuple('p.session.project.pcode == "Maintenance"')
        # NOTE: is this the most robust way to determine if a project is a test or commisioning project?
        self.scheduled_hours["test_comm"] = self.get_obs_time_tuple('p.session.project.pcode[0] == "T"')
        self.scheduled_hours["shutdown"] = self.get_obs_time_tuple('p.session.project.pcode == "Shutdown"')

        # how do the incomplete projects breakdown?
        self.backlog    = [p for p in Project.objects.all() \
            if p.semester in self.previousSemesters \
            and not p.complete \
            and p.get_category() == "Astronomy"] 
                       
        self.backlog_hours["total_time"] = sum([self.ta.getTimeLeft(p) for p in self.backlog])
        self.backlog_hours["years"] = {}
        for y in sorted(list(set([s.start().year for s in self.previousSemesters]))):
            projs = [p for p in self.backlog if p.semester.start().year == y]
            self.backlog_hours["years"]["%d" % y] = (sum([self.ta.getTimeLeft(p) for p in projs]), len(projs))
        self.backlog_hours["monitoring"] = sum([self.ta.getTimeLeft(p) for p in self.backlog \
                           if any([s.session_type.type == "windowed" \
                                   for s in p.sesshun_set.all()])])
        self.backlog_hours["vlbi"] = sum([self.ta.getTimeLeft(p) for p in self.backlog \
                           if any([s.observing_type.type == "vlbi" \
                                   for s in p.sesshun_set.all()])])                           

        total_time = sum([self.ta.getTimeLeft(p) for p in Project.objects.all()])
        monitoring = sum([self.ta.getTimeLeft(p) for p in self.backlog \
                           if any([s.session_type.type == "windowed" \
                                   for s in p.sesshun_set.all()]) and \
                              self.ta.getProjectTotalTime(p) <= 200.])
        vlbi       = sum([self.ta.getTimeLeft(p) for p in self.backlog \
                           if any([s.observing_type.type == "vlbi" \
                                   for s in p.sesshun_set.all()])])
        large      = sum([self.ta.getTimeLeft(p) for p in self.backlog \
                          if self.ta.getProjectTotalTime(p) > 200.])
        self.discharge_hours['total_time'] = total_time                  
        self.discharge_hours['monitoring'] = monitoring                  
        self.discharge_hours['vlbi']       = vlbi                  
        self.discharge_hours['large']      = large                  
        self.discharge_hours['rest']       = total_time - monitoring - vlbi - large


        self.nextWeekReservations = Reservation.objects.filter(
                                          end_date__gte = self.next_start
                                                       ).filter(
                                          start_date__lte = self.next_end)

    def output(self):
        "Format all the calculated quantities and print to report file."

        self.outfile.write("Last 7 days (%s to %s)\n" % (self.start.strftime("%m/%d/%Y")
                                              , self.end.strftime("%m/%d/%Y")))
        self.outfile.write("======================================\n")
    

    
        self.outfile.write("Observations for proposals\n")
        self.print_values(self.outfile
                   , set([p.session.project.pcode for p in self.observed_periods]))
    
        self.outfile.write("\nCompleted proposals\n")
        self.print_values(self.outfile, set([p.session.project.pcode \
                                   for p in self.observed_periods \
                                   if p.session.project.complete]))
    
        self.outfile.write("\nTotal Lost Time was %2.2f hr\n" % self.lost_hours["total_time"]) 
        self.outfile.write("\tweather = %2.2f hr\n" % self.lost_hours["weather"]) 
        self.outfile.write("\tRFI     = %2.2f hr\n" % self.lost_hours["RFI"]) 
        self.outfile.write("\tother   = %2.2f hr\n" % self.lost_hours["other"]) 
        self.outfile.write("\tLost Time Billed to Project = %2.2f hr\n" % self.lost_hours["billed_to_project"]) 
    
        self.outfile.write("\nNext Week\n")
        self.outfile.write("=========\n")
        self.outfile.write("Observations scheduled for %s - %s (note this only includes pre-scheduled projects):\n" % (self.next_start.strftime("%m/%d/%Y"), self.next_end.strftime("%m/%d/%Y")))
        values = ["%s, [%s], PI: %s\n\t\t%s\n\t\t%s" % \
                  (p.session.project.pcode
                 , p.session.observing_type.type
                 , p.session.project.principal_investigator()
                 , p.session.project.name
                 , p.__str__())
                  for p in self.upcoming_periods]
        self.print_values(self.outfile, set(values))
    
        projects = set([p.session.project for p in self.upcoming_periods])
        self.outfile.write("\nContact Information for pre-scheduled projects for %s - %s\n" % (self.next_start.strftime("%m/%d/%Y"), self.next_end.strftime("%m/%d/%Y")))
        self.outfile.write("==========================================================================\n")
        self.outfile.write("\tProject     PI                 Bands Email [NRAO contact]\n")
        self.outfile.write("\t----------- ------------------ ----- --------------------\n")
        values = ["%s %s %s %s [%s]" % \
                      (p.pcode.ljust(11)
                     , str(p.principal_investigator())[:17].ljust(18)
                     , ",".join(p.rcvrs_specified())[:4].center(5)
                     , p.principal_investigator().getEmails()[0]
                     , ";".join([f.user.name() for f in p.friend_set.all()])
                     )
                  for p in projects]
        self.print_values(self.outfile, set(values))
    

    
        self.outfile.write("\nScheduled Hours [backup]\n")
        self.outfile.write("========================\n")
        self.outfile.write("Category/Month -> %s %s\n" % \
                      (self.last_month.strftime("%B").center(8)

                     , self.start.strftime("%B").center(8)))

        last, this = self.scheduled_hours['astronomy']             
        self.outfile.write("     Astronomy ~  %s %s\n" % \
                      (("%.1f" % last).center(8), ("%.1f" % this).center(8)))
        last, this = self.scheduled_hours['maintenance']             
        self.outfile.write("   Maintenance ~  %s %s\n" % \
                      (("%.1f" % last).center(8), ("%.1f" % this).center(8)))
        last, this = self.scheduled_hours['test_comm']             
        self.outfile.write("   Test & Comm ~  %s %s\n" % \
                      (("%.1f" % last).center(8), ("%.1f" % this).center(8)))
        last, this = self.scheduled_hours['shutdown']             
        self.outfile.write("      Shutdown ~  %s %s\n" % \
                      (("%.1f" % last).center(8), ("%.1f" % this).center(8)))

        self.outfile.write(
            "\nCurrent backlog of Reg & RSS proposals [hours prior to %s*] = %.1f\n" % \
                (self.currentSemester, self.backlog_hours["total_time"])) 
 
        self.outfile.write("\t[")
        years = sorted(self.backlog_hours["years"].keys())
        self.outfile.write(", ".join(["%s: %.1f (%d)" % \
            (y, self.backlog_hours["years"][y][0], self.backlog_hours["years"][y][1]) for y in years]))


        self.outfile.write("]\n")
        self.outfile.write("\tBacklog includes %.1f hours of monitoring projects\n" % \
                      self.backlog_hours["monitoring"])

        self.outfile.write("\t                 %.1f hours of vlbi projects\n" % \
                      self.backlog_hours["vlbi"])

    
        self.outfile.write("\nTotal time to discharge [hours] = %.1f\n" % self.discharge_hours['total_time'])
        self.outfile.write("\tIncludes %.1f hours of monitoring projects (not Large) after semester %s\n" % \
            (self.discharge_hours['monitoring'], self.currentSemester))
        self.outfile.write("\t         %.1f hours of Regular & RRS projects\n" % self.discharge_hours['rest'])
        self.outfile.write("\t         %.1f hours of Large projects\n" % self.discharge_hours['large'])
        self.outfile.write("\t         %.1f hours of VLBI projects\n" % self.discharge_hours['vlbi'])
        self.outfile.write("\n* Includes projects that are on hold for semester %s\n" % self.currentSemester)
    
        visitors = ["%s - %s - %s [%s] [%s]" % (r.start_date.strftime("%m/%d")
                                  , r.end_date.strftime("%m/%d")
                                  , r.user.name()
                                  , ', '.join(r.user.getProjects())
                                  , ', '.join(r.user.getFriendLastNames())) \
                    for r in self.nextWeekReservations]              
    
        self.outfile.write("\nVisitors coming for %s - %s:\n" % (self.next_start.strftime("%m/%d/%Y"), self.next_end.strftime("%m/%d/%Y")))
        self.print_values(self.outfile, visitors)

def show_help(program):
    print "\nThe arguments to", program, "are:"
    print "\t<integer day> <integer month> <integer year>"
    print "and represent the date on which you wish the report to start."
    print "\nAll arguments are optional.  You can choose to specify all, any, or none."
    print "Appropriate defaults are chosen (if necessary) based upon today's date."
    print "\nNote: Although all arguments are optional, order matters."
    print "I.e. You cannot specify the month without the day.\n\n"


if __name__=='__main__':
    import sys

    today = datetime.today()

    if len(sys.argv) <= 1:
        start = today

    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        show_help(sys.argv[0])
        sys.exit()

    if len(sys.argv) == 2:
        start = datetime(today.year, today.month, int(sys.argv[1]))

    if len(sys.argv) == 3:
        start = datetime(today.year, int(sys.argv[2]), int(sys.argv[1]))

    if len(sys.argv) >= 4:
        start = datetime(int(sys.argv[3]), int(sys.argv[2]), int(sys.argv[1]))

    #GenerateReport(start)
    r = WeeklyReport(start)
    r.report()
