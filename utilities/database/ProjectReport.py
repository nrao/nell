#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *
from tools.TimeAccounting import TimeAccounting
from sets                 import Set

# days in a trimester * hours
# (And, yes, I'm ignoring leap years. Get off my back!)
TRIMESTER_HOURS = (365. / 3.) * 24.

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
    sorted_projects = sorted(Project.objects.filter(complete = False)
                           , lambda x, y: cmp(x.pcode, y.pcode))
    observed_hours  = 0
    remaining_hours = 0

    for p in sorted_projects:
        for typ in get_type(p):
            ohours = get_obs_hours(p,typ)
            rhours = get_rem_hours(p,typ)

            observed_hours  += ohours
            remaining_hours += rhours

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
               , "".join([str(get_rem_schedulable_hours(p, typ)), " / ", str(rhours)]).rjust(16)
               , str(ohours).center(7)
               , "Yes".center(8) if any([len(o.user.blackout_set.all()) == 0 for o in p.get_observers()]) else "        "
               , "Yes".center(6) if any([s.status.backup for s in p.sesshun_set.all()]) else "      "
               , get_rcvrs(p, typ)
                )
            )

    outfile.write("\nAllotment hours / Available Trimester Hours = %.1f%%\n" % 
                  ((observed_hours + remaining_hours) / TRIMESTER_HOURS * 100.))

    outfile.write("\nObserved hours  / Available Trimester Hours = %.1f%%\n" % 
                  (observed_hours / TRIMESTER_HOURS * 100.))

    outfile.write("\nRemaining hours / Available Trimester Hours = %.1f%%\n" % 
                  (remaining_hours / TRIMESTER_HOURS * 100.))

    outfile.close()

if __name__ == '__main__':
    GenerateProjectReport()
