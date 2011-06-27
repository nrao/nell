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

from datetime        import datetime, timedelta
from scheduler.models import *
from nell.utilities  import TimeAgent

def GenerateBlackoutReport():
    outfile = open("./DssBlackoutReport.txt", 'w')
    now     = datetime.utcnow()
    later   = now + timedelta(days = 7)

    outfile.write("Project     | Start (UTC) |  End (UTC)  |  Start (ET) |  End (ET)\n")
    outfile.write("-------------------------------------------------------------------\n")

    sorted_projects = sorted(Project.objects.filter(complete = False)
                           , lambda x, y: cmp(x.pcode, y.pcode))
    for p in sorted_projects:
        blackouts = p.get_blackout_times(now, later)
        if blackouts:
            for start, end in blackouts:
                outfile.write("%s | %s | %s | %s | %s\n" % \
                    (p.pcode.ljust(11)
                   , start.strftime("%m-%d %H:%M")
                   , end.strftime("%m-%d %H:%M")
                   , TimeAgent.utc2est(start).strftime("%m-%d %H:%M")
                   , TimeAgent.utc2est(end).strftime("%m-%d %H:%M")))

    outfile.close()

if __name__ == '__main__':
    GenerateBlackoutReport()
