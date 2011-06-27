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

import datetime
import sys

from django.core.management import setup_environ
import settings
setup_environ(settings)

from nell.utilities.TimeAccounting import TimeAccounting
from scheduler.models           import Project

def delta_to_hours(delta):
    return delta.days * 24 + delta.seconds / 3600.0

def get_period_end(p):
    return p.start + datetime.timedelta(hours=p.accounting.scheduled)

def sanity(p, start):
    x = p.accounting.time_billed() - delta_to_hours(start - p.start)
    return max(x, 0)

class StartEndAccounting(TimeAccounting):
    def getTime(self, obj, start, end):
        """
        Generic method for bubbling up all period accting up to the sess/proj.
          obj : either a project or session object
          start: get periods after or on this start datetime
          end: get periods before (not on) this end datetime
        """
        if obj.__class__.__name__ == "Project":
            ss = obj.sesshun_set.all()
            t = sum([self.getTime(s, start, end) for s in ss])
        else:
            ps = obj.period_set.all()
            t = self.getCompletedTime(ps, start, end)
        return t

    def getCompletedTime(self, ps, start, end):
        "Add up the billed time for those periods in time range."
        for p in [pp for pp in ps if pp.start >= start and pp.start < end]:
            print p
            print "\t", p.accounting.time_billed(), delta_to_hours(end - p.start)
        for p in [pp for pp in ps if get_period_end(pp) > start and pp.start < start]:
            print p
            print "\t", p.accounting.time_billed(), sanity(p, start)
        return sum([min(p.accounting.time_billed(), delta_to_hours(end - p.start))
                    for p in ps if p.start >= start and p.start < end] +
                   [min(p.accounting.time_billed(), sanity(p, start))
                    for p in ps if get_period_end(p) > start and p.start < start]
                   )

    def getStartEndProjects(self, projects, start, end):
        projects_with_hours = []
        for project in projects:
            t = self.getTime(project, start, end)
            if t > 0:
                projects_with_hours.append((project.pcode, t))
        return sorted(projects_with_hours)

def get_projects_between_start_end(start, end):
    "Get list of project,hour pairs for observations after start, before end."
    projects = Project.objects.all()
    acct = StartEndAccounting()
    return acct.getStartEndProjects(projects, start, end)

# We are not actually generating a report in the DSS sense.

if __name__ == '__main__':
    if len(sys.argv) > 2:
        start = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
        print >>sys.stderr, 'start:', start
        end = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
        print >>sys.stderr, 'end:', end
        total_hours = 0.0
        # print get_projects_between_start_end(start, end)
        # sys.exit()
        for project,hours in get_projects_between_start_end(start, end):
            print project,hours
            total_hours += hours
        print
        print 'Total hours:', total_hours
    else:
        print >>sys.stderr, "usage:", sys.argv[0], "start-date end-date"
        print >>sys.stderr, "example:", sys.argv[0], "2009-10-01 2010-01-01"
