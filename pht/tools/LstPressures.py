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

#from django.core.management import setup_environ
#import settings
#setup_environ(settings)

#from datetime         import datetime

from pht.utilities    import *
from pht.models       import *
from scheduler.models import Observing_Type

class LstPressures(object):

    def __init__(self):

        self.bins = [0.0]*24

        self.pressures = [{'ra':float(i), 'total':0.0} for i in range(24)]

        # for reporting
        self.badRas = []
        self.noRas = []

    def getPressures(self):
        """
        Returns a dictionary of pressures by LST for different 
        categories.  This format is specified to easily convert
        to the format expected by the web browser client (Ext store).
        For example:
        [
         {'ra': 0.0, 'total': 2.0, 'A': 1.0, 'B': 1.0},
         {'ra': 1.0, 'total': 3.0, 'A': 2.0, 'B': 1.0},
        ]
        """

        # carry over
        ss = [s for s in Session.objects.all() \
            if s.dss_session is not None]
        self.getPressuresByType(ss, "carryover")

        # TBF: maintenance and test time

        # new stuff, by all grade and weather type
        for weather in ['Poor', 'Good', 'Excellent']:
            for grade in ['A', 'B', 'C']:
                ss = Session.objects.filter(weather_type__type = weather
                                          , grade__grade = grade
                                          , dss_session = None
                                            )
                type = "%s_%s" % (weather, grade)
                self.getPressuresByType(ss, type)
       
        return self.pressures

    def getPressuresByType(self, sessions, type):
        "Get the pressures for the given sessions"

        # initilize this type's dictionary
        if not self.pressures[0].has_key(type):
            for p in self.pressures:
                p[type] = 0.0

        for s in sessions:
            hr = rad2hr(s.target.ra)
            if hr is not None:
                bin = int(math.floor(hr))
                if bin < 24:
                    if s.dss_session:
                        pressure = s.remainingTime()
                    else:
                        pressure = s.allotment.allocated_time
                    self.pressures[bin]['total'] += pressure
                    self.pressures[bin][type] += pressure
                else:
                    self.badRas.append(s)
            else:
                self.noRas.append(s)
            




