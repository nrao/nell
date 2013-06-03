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
from TypeObservingReport import TypeObservingReport

class ScienceObservingReport(TypeObservingReport):

    "Quick report for Jay Lockman"

    def getTypes(self):
        # get the scientific observing types
        nonScience = ['calibration'
                    , 'commissioning'
                    , 'testing'
                    , 'maintenance'
                     ]
        types = [t.type for t in Observing_Type.objects.all() if t.type not in nonScience]
        types.append('total')
        return types

    def computeForYear(self, year):

        ps = self.getPeriodsForYear(year)
        for p in ps:
            obsTime, type = self.getObsTime(p)
            # non-science types will be returned as None
            if type is not None:
                self.data[year][type] += obsTime 
                self.data[year]['total'] += obsTime 

    def getObsTime(self, period):
        if not period.session.project.is_science():
            return (None, None)
        return (period.accounting.observed(), period.session.observing_type.type)
       
if __name__ == '__main__':

    r = ScienceObservingReport()
    r.setYears([2010, 2011, 2012])
    r.report()
