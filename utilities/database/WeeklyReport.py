from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *
from sets            import Set
from datetime        import date,datetime,timedelta

def print_values(file, values):
    if values == []:
        file.write("\tNone\n")
    else:
        for v in values:
            file.write("\t%s\n" % v)

def GenerateReport(start):
    outfile = open("./WeeklyReport.txt", 'w')
    end     = start + timedelta(days = 7)
    periods = [p for p in Period.objects.all()]

    outfile.write("Last 7 days (%s to %s)\n" % (start.strftime("%m/%d/%Y")
                                              , end.strftime("%m/%d/%Y")))
    outfile.write("=======================================\n")

    observed_periods = \
        sorted(Set([p for p in periods \
                      if overlaps((p.start, p.end()), (start, end))]))
    upcoming_periods = \
        sorted(Set([p for p in periods \
                      if overlaps((p.start, p.end())
                                , (end, end + timedelta(days = 7)))]))

    outfile.write("Observations for proposals\n")
    print_values(outfile, [p.session.project.pcode for p in observed_periods])

    outfile.write("\nCompleted proposals\n")
    print_values(outfile, [p.session.project.pcode \
                           for p in observed_periods \
                           if p.session.project.complete])

    outfile.write("\nNext Week\n")
    outfile.write("=========\n")
    outfile.write("Observations scheduled for %s - %s\n" % (start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")))
    values = ["%s, [%s], PI: %s\n\t\t%s" % \
              (p.session.project.pcode
             , p.session.observing_type.type
             , p.session.project.principal_investigator()
             , p.session.project.name)
              for p in upcoming_periods]
    print_values(outfile, Set(values))

    outfile.write("\nContact Information for %s - %s\n" % (start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")))
    outfile.write("===============================================\n")
    outfile.write("\tProject     PI                 Bands Email [NRAO contact]\n")
    outfile.write("\t----------- ------------------ ----- --------------------\n")
    values = ["%s %s %s %s [%s]" % \
                  (p.session.project.pcode.ljust(11)
                 , str(p.session.project.principal_investigator())[:17].ljust(18)
                 , ",".join(p.session.rcvrs_specified())[:4].center(5)
                 , p.session.project.principal_investigator().getStaticContactInfo()['emails'][0]
                 , p.session.project.friend)
              for p in upcoming_periods]
    print_values(outfile, Set(values))

    last_month   = start - timedelta(days = 31)
    last_periods = [p for p in periods \
                      if p.start.month == last_month.month and \
                         p.start.year  == last_month.year]
    this_periods = [p for p in periods \
                      if p.start.month == start.month and \
                         p.start.year  == start.year]

    outfile.write("\nScheduled Hours [backup]\n")
    outfile.write("============================\n")
    outfile.write("Category/Month -> %s %s\n" % \
                  (last_month.strftime("%B").center(8)
                 , start.strftime("%B").center(8)))
    outfile.write("     Astronomy ~  %s %s\n" % \
                  ("%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in last_periods \
                        if p.session.project.project_type.type == "science"])
                 , "%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in this_periods \
                        if p.session.project.project_type.type == "science"])))
    outfile.write("   Maintenance ~  %s %s\n" % \
                  ("%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in last_periods \
                        if p.session.project.pcode == "Maintenance"])
                ,  "%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in this_periods \
                        if p.session.project.pcode == "Maintenance"])))
    outfile.write("   Test & Comm ~  %s %s\n" % \
                  ("%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in last_periods \
                        if p.session.project.pcode[0] == "T"])
                 , "%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in this_periods \
                        if p.session.project.pcode[0] == "T"])))
    outfile.write("      Shutdown ~  %s %s\n" % \
                  ("%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in last_periods \
                        if p.session.project.pcode == "Shutdown"])
                 , "%.1f".center(8) % \
                   sum([p.accounting.scheduled for p in this_periods \
                        if p.session.project.pcode == "Shutdown"])))

    ta         = TimeAccounting()
    pSemesters = Semester.getPreviousSemesters(start)
    backlog    = [p for p in Project.objects.all() if p.semester in pSemesters]
    outfile.write(
        "\nCurrent backlog of Reg & RSS proposals [hours prior to %s*] = %.1f\n" % \
            (Semester.getCurrentSemester(start)
           , sum([ta.getTimeLeft(p) for p in backlog])))
    outfile.write("\t[")
    outfile.write(", ".join(["%s: %.1f (%d)" % \
       (y 
      , sum([ta.getTimeLeft(p) for p in backlog if p.semester.start().year == y])
      , len([p for p in backlog if p.semester.start().year == y]))
        for y in sorted(list(Set([s.start().year for s in Semester.getPreviousSemesters(start)])))]))
    outfile.write("]\n")
    outfile.write("\tBacklog includes %.1f hours of monitoring projects\n" % \
                  sum([ta.getTimeLeft(p) for p in backlog \
                       if any([s.session_type.type == "windowed" \
                               for s in p.sesshun_set.all()])]))
    outfile.write("\t                 %.1f hours of vlbi projects\n" % \
                  sum([ta.getTimeLeft(p) for p in backlog \
                       if any([s.observing_type.type == "vlbi" \
                               for s in p.sesshun_set.all()])]))

    cSemester  = Semester.getCurrentSemester(start)
    fSemesters = Semester.getFutureSemesters(start)
    total_time = sum([ta.getTimeLeft(p) for p in Project.objects.all()])
    monitoring = sum([ta.getTimeLeft(p) for p in backlog \
                       if any([s.session_type.type == "windowed" \
                               for s in p.sesshun_set.all()]) and \
                          ta.getProjectTotalTime(p) <= 200.])
    vlbi       = sum([ta.getTimeLeft(p) for p in backlog \
                       if any([s.observing_type.type == "vlbi" \
                               for s in p.sesshun_set.all()])])
    large      = sum([ta.getTimeLeft(p) for p in backlog \
                      if ta.getProjectTotalTime(p) > 200.])
    rest       = total_time - monitoring - vlbi - large

    outfile.write("\nTotal time to discharge [hours] = %.1f\n" % total_time)
    outfile.write("\tIncludes %.1f hours of monitoring projects (not Large) after trimester %s\n" % (monitoring, cSemester))
    outfile.write("\t         %.1f hours of Regular & RRS projects\n" % rest)
    outfile.write("\t         %.1f hours of Large projects\n" % large)
    outfile.write("\t         %.1f hours of VLBI projects\n" % vlbi)
    outfile.write("\n* Includes projects that are on hold for trimester %s" % cSemester)

if __name__=='__main__':
    start = datetime.today()
    GenerateReport(start)
