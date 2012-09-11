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

from nell.utilities.TimeAccounting import TimeAccounting
from scheduler.models           import Project
import sys
from datetime import datetime

def report(pcode, start, end):

    try:
        project = Project.objects.get(pcode = pcode)
    except Project.DoesNotExist:
        print "cannot find project: ", pcode
        return
    startDate = datetime.strptime(start, '%m-%d-%Y')
    e         = datetime.strptime(end, '%m-%d-%Y')
    endDate   = datetime(e.year, e.month, e.day, 23, 59, 59)
    ta = TimeAccounting()
    ta.reportDateRange(project, startDate, endDate)

if __name__ == '__main__':
    if len(sys.argv) > 3:
        pcode, start, end= sys.argv[1:]
        report(pcode, start, end)
    else:
        print "must provide project code"
