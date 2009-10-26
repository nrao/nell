#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *
from sets            import Set

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

    return ", ".join(Set([
        "(%s)" % ", ".join([
            rcvr_dict[r.abbreviation] \
            for rg in s.receiver_group_set.all() \
            for r in rg.receivers.all()
        ]) for s in get_sessions(project, typ)
    ]))

def get_allotment_hours(project, typ):
    return sum([s.allotment.total_time for s in get_sessions(project, typ)])

def get_obs_hours(project, typ):
    return sum([
        p.accounting.scheduled - \
        p.accounting.not_billable - \
        p.accounting.other_session_weather - \
        p.accounting.other_session_rfi - \
        p.accounting.other_session_other - \
        p.accounting.lost_time_weather - \
        p.accounting.lost_time_rfi - \
        p.accounting.lost_time_other
    for s in get_sessions(project, typ) for p in s.period_set.all()])

def get_rem_hours(project,typ):
    return get_allotment_hours(project, typ) - get_obs_hours(project, typ)

def GenerateProjectReport():
    outfile = open("./DssProjectReport.txt", 'w')

    outfile.write("  Project   |   Type   | Sessions | Not Enabled | Observers | Complete | Incomplete | Obs Hrs | Rem Hrs | Blackout | Backup | Receivers\n")

    count           = 0
    sorted_projects = sorted(Project.objects.filter(complete = False)
                           , lambda x, y: cmp(x.pcode, y.pcode))
    for p in sorted_projects:
        for typ in get_type(p):
            if count % 10 == 0:
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
               , str(get_obs_hours(p,typ)).center(7)
               , str(get_rem_hours(p,typ)).center(7)
               , str(any([len(o.user.blackout_set.all()) == 0 \
                          for o in p.get_observers()])).center(8)
               , str(any([s.status.backup for s in p.sesshun_set.all()])).center(6)
               , get_rcvrs(p, typ)
                )
            )

    outfile.close()

if __name__ == '__main__':
    GenerateProjectReport()
