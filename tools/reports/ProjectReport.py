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

#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime                  import *
from nell.utilities.TimeAccounting import TimeAccounting
from scheduler.models           import *

def get_type(project):
    return set([s.session_type.type for s in project.sesshun_set.all()])

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

    grps = list(set([", ".join([rcvr_dict[r.abbreviation] \
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

    semester          = Semester.getCurrentSemester()
    semester_hrs_left = (semester.end() - datetime.today()).days * 24.
    SEMESTER_HOURS    = (semester.end() - semester.start()).days * 24.

    outfile.write("\nTotal hours in this semester   = %.1f"% SEMESTER_HOURS)
    outfile.write("\nTotal hours left this semester = %.1f\n" % \
                  semester_hrs_left)

    ta    = TimeAccounting()
    hours = sum([ta.getTimeLeft(p) for p in open_projects])

    outfile.write("\nSum of all incomplete projects' hours remaining = %.1f" % hours)
    outfile.write("\nHours remaining / Trimester Hours               = %.1f%%" % 
                  (hours / SEMESTER_HOURS * 100.))
    outfile.write("\nHours remaining / Trimester Hours Left          = %.1f%%\n" % 
                  float(hours / semester_hrs_left * 100.))

    hours = sum([ta.getProjectSchedulableTotalTime(p) for p in open_projects])
    outfile.write("\nSum of all schedulable time             = %.1f" % \
                  hours)

    outfile.write("\nSchedulable time / Trimester Hours      = %.1f%%" % (hours / SEMESTER_HOURS * 100.))  
    outfile.write("\nSchedulable time / Trimester Hours Left = %.1f%%\n" % (hours / semester_hrs_left * 100.))  

    outfile.close()

if __name__ == '__main__':
    GenerateProjectReport()
