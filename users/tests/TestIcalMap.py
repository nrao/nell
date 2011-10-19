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

from datetime                import datetime, timedelta
from scheduler.models        import *
from test_utils              import NellTestCase
from tools.IcalMap           import IcalMap
from TestObserversBase      import TestObserversBase

class TestIcalMap(TestObserversBase):


    def setUp(self):
        super(TestIcalMap, self).setUp()
   
        # setup some periods for the first project
        self.ps = []
        dt = datetime(2011, 10, 20)
        self.create_periods(dt, 3, self.s)

        # create a different project
        self.p2 = self.create_project("proj2")
        self.p2.name = "Pauls horrible project"
        self.p2.save()

        # and a session for it
        self.s2 = self.create_session()
        self.s2.project = self.p2
        self.s2.name = "s2"
        self.s2.save()

        # and some periods for it
        self.create_periods(dt + timedelta(hours = 3), 4, self.s2)

    def create_periods(self, start, num, session):
        dur = 1.0
        scheduled = Period_State.get_state("S")

        for hour in range(0,num):
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            p = Period(session = session
                 , start = start + timedelta(hours = (hour*dur))
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
            p.save()
            self.ps.append(p)


    def test_GBTSchedule(self):

        ical = IcalMap()
        self.assertEquals(7, len(ical.cal.subcomponents))
        schd = ical.getSchedule()
        self.assertEquals(3, schd.count("mikes awesome project"))
        self.assertEquals(4, schd.count("Pauls horrible project"))
        
        # unschedule one of them
        self.ps[0].state = Period_State.get_state('P')
        self.ps[0].save()

        ical = IcalMap()
        self.assertEquals(6, len(ical.cal.subcomponents))
        schd = ical.getSchedule()
        self.assertEquals(2, schd.count("mikes awesome project"))
        self.assertEquals(4, schd.count("Pauls horrible project"))

    def test_UserSchedule(self):

        ical = IcalMap(self.u)
        self.assertEquals(3, len(ical.cal.subcomponents))
        schd = ical.getSchedule()
        self.assertEquals(3, schd.count("mikes awesome project"))
        self.assertEquals(0, schd.count("Pauls horrible project"))
        
