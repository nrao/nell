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

from   django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime                  import *
from nell.utilities.TimeAccounting import TimeAccounting
from scheduler.models           import *

def ljust(value, width):
    if type(value) == type(3.14): # watch out for floats
        return str("%5.2f" % value)[:width].ljust(width)
    else:    
        return str(value)[:width].ljust(width)

def rjust(value, width):
    if type(value) == type(3.14): # watch out for floats
        return str("%5.2f" % value)[:width].rjust(width)
    else:    
        return str(value)[:width].rjust(width)

def center(value, width):
    if type(value) == type(3.14): # watch out for floats
        return str("%5.2f" % value)[:width].center(width)
    else:    
        return str(value)[:width].center(width)

def bl(value):
    return "X" if value else ""

def scheduable(sess):
    if sess.status.enabled and sess.status.authorized:
        return "S"
    else:
        return ""

def GenerateReport(start):
    outfile   = open("./DssSessionReport.txt", 'w')
    scs       = [1, 13, 5, 3, 6, 4, 10, 11, 6, 6, 6, 6, 5, 15]
    scss      = " %s" * len(scs)
    hdrFormat = "\n\n\t " + scss
    dataFormat = "\n\t " + scss
    semesters = sorted(Semester.objects.all()
                     , lambda x,y:cmp(x.semester,y.semester))
    ta        = TimeAccounting()

    for s in semesters:
        projects = sorted([p for p in s.project_set.all() if not p.complete]
                        , lambda x,y:cmp(x.pcode, y.pcode))
        if projects:
            outfile.write("\n\n")
            outfile.write("=" * 100)   
            outfile.write("\n\nTrimester: %s\n" %s.semester)
            outfile.write("-" * 14)   

        for p in projects:
            outfile.write("\n\n\t%s, %s, PI: %s, Rem/Tot: %.1f/%.1f" % \
                        (p.pcode
                       , p.name[:50]
                       , p.principal_investigator().last_name if p.principal_investigator() else "None"
                       , ta.getTimeLeft(p)
                       , ta.getProjectTotalTime(p)))

            outfile.write(hdrFormat % \
                   (ljust("",         scs[0])
                  , ljust("name",     scs[1])
                  , center("orgID",   scs[2])
                  , center("sch",     scs[3])
                  , center("obs",     scs[4])
                  , ljust("type",     scs[5])
                  , center("RA",      scs[6])
                  , center("Dec",     scs[7])
                  , center("rem",     scs[8])
                  , center("tot",     scs[9])
                  , rjust("min",      scs[10])
                  , rjust("max",      scs[11])
                  , rjust("btwn",     scs[12])
                  , ljust("rcvrs",    scs[13])))

            sessions = sorted(p.sesshun_set.all()
                            , lambda x,y:cmp(x.name, y.name))
            for s in sessions:

                target = s.getTarget()

                outfile.write(dataFormat % \
                    (ljust(bl(s.status.complete),        scs[0])
                   , ljust(s.name,                       scs[1])
                   , rjust(s.original_id,                scs[2])
                   , center(scheduable(s),               scs[3])
                   , center(s.observing_type.type[:6],   scs[4])
                   , center(s.session_type.type[0],      scs[5])
                   , ljust(target.get_horizontal(),      scs[6])
                   , ljust(target.get_vertical(),        scs[7])
                   , rjust(ta.getTimeLeft(s),            scs[8])
                   , rjust(s.allotment.total_time,       scs[9])
                   , rjust(s.min_duration,               scs[10])
                   , rjust(s.max_duration,               scs[11])
                   , rjust(s.time_between,               scs[12])
                   , ljust("".join(s.rcvrs_specified()), scs[13])
                   ))

            if p != projects[-1]:
                outfile.write("\n\t" + ("-" * 96))                 

if __name__=='__main__':
    GenerateReport(datetime.today())
