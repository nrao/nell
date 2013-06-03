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

class TypeObservingReport:

    "Abstract class for family of simple reports on observed time."

    def __init__(self, years=[]):
        self.setYears(years)
        

    def setYears(self, years):
        self.years = years #[2010, 2011, 2012]
        self.initTypes(self.getTypes())

    def initTypes(self, types):
        # init data structure
        self.types = types
        self.data = {}
        for y in self.years:
            self.data[y] = {} 
            for t in self.types:
                self.data[y][t] = 0        

    def getTypes(self):
        return []

    def compute(self):
        for y in self.years:
            self.computeForYear(y)
        
    def computeForYear(self, year):
        pass

    def getPeriodsForYear(self, year):
        "Rough cut - does not take into account overlap at end points"
        start = datetime(year, 1, 1)
        end   = datetime(year, 12, 31, 23, 59, 59)
        ps = Period.objects.filter(start__gt = start, start__lt = end).order_by('start')
        return ps

    def report(self):
        self.compute()
        for t in self.types:
            print t
            for y in self.years:
                print "  %d: %5.2f" % (y, self.data[y][t])

