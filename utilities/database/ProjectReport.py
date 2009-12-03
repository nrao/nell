#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *
from tools.TimeAccounting import TimeAccounting
from sets                 import Set
from datetime             import *

def get_type(project):
    return Set([s.session_type.type for s in project.sesshun_set.all()])

def get_sessions(project, typ, enabled = None, complete = False):
    if enabled is not None:
        return [s for s in project.sesshun_set.all() \
                 if s.session_type.type ==  typ and \
                    s.status.enabled == enabled and \
                    s.status.complete == complete]
    else:
        return [s for s in project.sesshun_set.all() \
                 if s.session_type.type ==  typ and \
                    s.status.complete == complete]

def get_rcvrs(project, typ):
    rcvr_dict = {
        "RRI" : "R"
      , "342" : "3"
      , "450" : "4"
      , "600" : "6"
      , "800" : "8"
      , "1070": "A"
      , "L"   : "L"
      , "S"   : "S"
      , "C"   : "C"
      , "X"   : "X"
      , "Ku"  : "U"
      , "K"   : "K"
      , "Ka"  : "B"
      , "Q"   : "Q"
      , "MBA" : "M"
      , "Z"   : "Z"
      , "Hol" : "H"
      , "KFPA": "P"
    }

    grps = list(Set([", ".join([rcvr_dict[r.abbreviation] \
                                for rg in s.receiver_group_set.all()
                                for r in rg.receivers.all()])
                     for s in get_sessions(project, typ)]))
    if grps and len(grps) == 1:
        return grps[0]
    else:
        return ", ".join(["(%s)" % g for g in grps])

def get_allotment_hours(project, typ):
    return sum([s.allotment.total_time for s in get_sessions(project, typ)])

def get_scheduled_session_hours(project,typ):
    return sum([s.allotment.total_time for s in get_sessions(project, typ)]) 

def get_obs_hours(project, typ):
    ta = TimeAccounting()
    return sum([ta.getTime("observed", s) for s in get_sessions(project, typ)])

def get_rem_hours(project, typ):
    ta = TimeAccounting()
    return sum([ta.getTimeLeft(s) for s in get_sessions(project, typ)])

def get_rem_schedulable_hours(project, typ):
    ta = TimeAccounting()
    return sum([ta.getTimeLeft(s) for s in get_sessions(project, typ) \
                if s.schedulable() and project.has_sanctioned_observers()])

def GenerateProjectReport():
    outfile = open("./DssProjectReport.txt", 'w')

    outfile.write("Project     |   Type   | Sessions | Not Enabled | Observers | Complete | Incomplete |  Avail / Rem Hrs | Obs Hrs | Blackout | Backup | Receivers\n")

    count           = 0
    open_projects   = sorted(Project.objects.filter(complete = False)
                           , lambda x, y: cmp(x.pcode, y.pcode))

    for p in open_projects: 
        for typ in get_type(p):
            if count % 5 == 0:
                outfile.write("-------------------------------------------------------------------------------------------------------------------------------------------\n")
            count += 1

            outfile.write(
                "%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s\n" % \
                (p.pcode.ljust(11)
               , typ.center(8)
               , str(len(p.sesshun_set.all())).center(8)
               , str(len(get_sessions(p, typ, False))).center(11)
               , str(len(p.get_observers())).center(9)
               , str(len([s for s in p.sesshun_set.all() \
                            if s.status.complete == True])).center(8)
               , str(len(get_sessions(p, typ))).center(10)
               , "".join([str(get_rem_schedulable_hours(p, typ)), " / ", str(get_rem_hours(p,typ))]).rjust(16)
               , str(get_obs_hours(p,typ)).center(7)
               , "Yes".center(8) if any([len(o.user.blackout_set.all()) == 0 for o in p.get_observers()]) else "        "
               , "Yes".center(6) if any([s.status.backup for s in p.sesshun_set.all()]) else "      "
               , get_rcvrs(p, typ)
                )
            )

    trimester          = Semester.getCurrentSemester()
    trimester_hrs_left = (trimester.end() - datetime.today()).days * 24.
    TRIMESTER_HOURS    = (trimester.end() - trimester.start()).days * 24.

    outfile.write("\nTotal hours in this trimester = %.1f\n"% TRIMESTER_HOURS)
    outfile.write("\nTotal hours left this trimester = %.1f\n" % \
                  trimester_hrs_left)


    # All open projects + 
    # All projects for this trimester +
    # All A grade projects that ran during this trimester
    projects = \
        [p for p in open_projects] + \
        [p for p in Project.objects.filter(complete = True).filter(semester = trimester)] + \
        [p for p in Project.objects.filter(complete = True) \
           if p.semester != trimester.semester and \
              any([s.allotment.grade == 4.0 for s in p.sesshun_set.all()]) and \
              any([pd.start > trimester.start() and \
                   pd.start < trimester.end() \
                   for pd in s.period_set.all()])]

    ta    = TimeAccounting()
    hours = sum([min(ta.getProjectTotalTime(p)
                   , ta.getProjSessionsTotalTime(p))
                 for p in projects])

    outfile.write("\nSum of all sessions' allotment time = %.1f\n" % hours)
    outfile.write("\nAllotment hours / Trimester Hours = %.1f%%\n" % 
                  (hours / TRIMESTER_HOURS * 100.))

    outfile.write("\nHours discharged / Trimester Hours = %.1f%%\n" % 
                  (sum([ta.getTime("observed", p) for p in projects]) / TRIMESTER_HOURS * 100.))

    hours = sum([ta.getTimeLeft(p) for p in projects if not p.complete])
    outfile.write("\nSum of all sessions' hours remaining = %.1f\n" % hours)
    outfile.write("\nHours remaining / Trimester Hours = %.1f%%\n" % 
                  (hours / TRIMESTER_HOURS * 100.))
    outfile.write("\nHours remaining / Trimester Hours Left = %.1f%%\n" % 
                  float(hours / trimester_hrs_left * 100.))

    hours = sum([s.allotment.total_time \
                 for p in projects \
                 for s in p.sesshun_set.all() \
                 if s.schedulable()])
    outfile.write("\nSum of all schedulable sessions' total time = %.1f\n" % \
                  hours)

    outfile.write("\nSum of all schedulable sessions' total time / total hours in a trimester = %.1f%%\n" % (hours / TRIMESTER_HOURS * 100.))  

    outfile.close()

if __name__ == '__main__':
    GenerateProjectReport()
