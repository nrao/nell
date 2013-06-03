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

class ReceiverObservingReport(TypeObservingReport):

    "Reports how observing went per receiver per year."

    def __init__(self, years=[]):
        TypeObservingReport.__init__(self, years=years)

        self.hiFreqs = ['MBA', 'MBA1.5', 'W', 'Q', 'Ka', 'K', 'KFPA', 'Ku'] #, 'KFPA']
        #self.initTypes(self.getTypes())

    def getTypes(self):
        types = [r.abbreviation for r in Receiver.objects.all().order_by('freq_low')]
        types.append('total')
        types.append('hiFreqs')
        return types

    def computeForYear(self, year):
        #self.data['year']['hiFreqs'] = 0.0
        ps = self.getPeriodsForYear(year)
        for p in ps:
            # count only science
            if not p.session.project.is_science():
                continue
            obsTime, types = self.getObsTime(p)
            for type in types:
                # if there are multiple rxs used, split up 
                # the time evenly
                t = obsTime/len(types)
                self.data[year][type] += t 
                self.data[year]['total'] += t 
                if type in self.hiFreqs:
                    self.data[year]['hiFreqs'] += t


    def getObsTime(self, period):
        """
        Returns (observered time, receivers used)
        The historical record of which receiver a period uses may actually
        span more then one receiver.
        """
        return (period.accounting.observed(), [r.abbreviation for r in period.receivers.all()])
                       
       
if __name__ == '__main__':

    r = ReceiverObservingReport()
    r.setYears([2010, 2011, 2012])
    r.report()
