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

def GenerateProjectTimeAccountingReport(pcode):

    project = Project.objects.get(pcode = pcode)
    if project is None:
        print "cannot find project: ", pcode
        return
    ta = TimeAccounting()
    ta.report(project, "%sTimeAccounting.txt" % pcode)

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        pcode = sys.argv[1]
        print pcode
        GenerateProjectTimeAccountingReport(pcode)
    else:
        print "must provide project code"
