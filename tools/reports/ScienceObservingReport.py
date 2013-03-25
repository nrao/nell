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

from scheduler.models import *
from datetime import datetime

class ScienceObservingReport:

    "Quick report for Jay Lockman"

    def __init__(self, years=[]):

        self.setYears(years)
    
    def setYears(self, years):
        self.years = years #[2010, 2011, 2012]
        # get the scientific observing types
        nonScience = ['calibration'
                    , 'commissioning'
                    , 'testing'
                    , 'maintenance'
                     ]
        self.types = [t.type for t in Observing_Type.objects.all() if t.type not in nonScience]
        self.types.append('total')
        # init data structure
        self.data = {}
        for y in years:
            self.data[y] = {} 
            #self.data[y]['total'] = 0
            for t in self.types:
                self.data[y][t] = 0

    def compute(self):

        for y in self.years:
            self.computeForYear(y)

    def computeForYear(self, year):

        ps = self.getPeriodsForYear(year)
        for p in ps:
            obsTime, type = self.getScienceObsTime(p)
            # non-science types will be returned as None
            if type is not None:
                self.data[year][type] += obsTime 
                self.data[year]['total'] += obsTime 

    def getPeriodsForYear(self, year):
        "Rough cut - does not take into account overlap at end points"
        start = datetime(year, 1, 1)
        end   = datetime(year, 12, 31, 23, 59, 59)
        ps = Period.objects.filter(start__gt = start, start__lt = end).order_by('start')
        return ps

    def getScienceObsTime(self, period):
        if not period.session.project.is_science():
            return (None, None)
        return (period.accounting.observed(), period.session.observing_type.type)
 
    def report(self):
        self.compute()
        for t in self.types:
            print t
            for y in self.years:
                print "%d: %5.2f" % (y, self.data[y][t])
        
                       
       
if __name__ == '__main__':

    r = ScienceObservingReport()
    r.setYears([2010, 2011, 2012])
    r.report()
