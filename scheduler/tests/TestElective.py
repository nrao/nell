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

from datetime                   import datetime, timedelta
from test_utils              import NellTestCase
from utils                   import create_sesshun, setupElectives, create_blackout
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestElective(NellTestCase):

    @setupElectives
    def setUp(self):
        super(TestElective, self).setUp()

    def test_publish(self):

        # test the inital state
        self.assertEqual(['P','P','P','D']
            , [p.state.abbreviation for p in self.elec.periods.all()])

        # publish the first one
        self.period1.publish()

        # retrieve objects fresh, and check states
        p1 = Period.objects.get(id = self.period1.id)
        p2 = Period.objects.get(id = self.period2.id)
        p3 = Period.objects.get(id = self.period3.id)
        self.assertEquals(self.scheduled, p1.state)
        self.assertEquals(self.deleted,   p2.state)
        self.assertEquals(self.deleted,   p3.state)

    def test_setComplete(self):

        # test the inital state
        self.assertEqual(['P','P','P','D']
            , [p.state.abbreviation for p in self.elec.periods.all()])

        # publish the first one
        self.period1.publish()

        # retrieve objects fresh, and check states
        p1 = Period.objects.get(id = self.period1.id)
        p2 = Period.objects.get(id = self.period2.id)
        p3 = Period.objects.get(id = self.period3.id)
        self.assertEquals(self.scheduled, p1.state)
        self.assertEquals(self.deleted,   p2.state)
        self.assertEquals(self.deleted,   p3.state)

        # now set it as complete - shouldn't do anything
        elec = Elective.objects.get(id = self.elec.id)
        elec.setComplete(True)
        self.assertEquals(True, elec.complete)

        # retrieve objects fresh, and check states
        p1 = Period.objects.get(id = self.period1.id)
        p2 = Period.objects.get(id = self.period2.id)
        p3 = Period.objects.get(id = self.period3.id)
        self.assertEquals(self.scheduled, p1.state)
        self.assertEquals(self.deleted,   p2.state)
        self.assertEquals(self.deleted,   p3.state)

        # now set it as false, and watch the periods come back
        elec.setComplete(False)
        
        # retrieve objects fresh, and check states
        p1 = Period.objects.get(id = self.period1.id)
        p2 = Period.objects.get(id = self.period2.id)
        p3 = Period.objects.get(id = self.period3.id)
        self.assertEquals(self.scheduled, p1.state)
        self.assertEquals(self.pending,   p2.state)
        self.assertEquals(self.pending,   p3.state)

    def test_update_from_post(self):
        e = Elective()
        adapter = ElectiveHttpAdapter(e)

        fdata = {"session":  1
               , "complete": "true" 
               }        
        adapter.init_from_post(fdata)

        self.assertEqual(adapter.elective.session, self.sesshun)
        self.assertEqual(adapter.elective.complete, True)
        self.assertEqual(len(adapter.elective.periods.all()), 0)

        fdata.update({"complete" : False})
        adapter.update_from_post(fdata)

        self.assertEqual(e.session, self.sesshun)
        self.assertEqual(e.complete, False)
        self.assertEqual(len(e.periods.all()), 0)

    def test_jsondict(self):

        adapter = ElectiveHttpAdapter(self.elec)

        jd = adapter.jsondict()

        self.assertEqual(jd["session"]["pcode"], "GBT09A-001")
        self.assertEqual(jd["complete"], False)
        self.assertEqual(len(jd["periods"]), 4)

    def test_hasPeriodAfter(self):
        before = datetime(2009, 5, 11, 12, 15)
        middle = datetime(2009, 6, 3, 12, 15)
        after  = datetime(2009, 6, 21, 12, 15)
        self.assertEqual(True, self.elec.hasPeriodsAfter(before))
        self.assertEqual(True, self.elec.hasPeriodsAfter(middle))
        self.assertEqual(False, self.elec.hasPeriodsAfter(after))

    def test_periodDateRange(self):
        self.assertEqual((datetime(2009, 6, 1, 12, 15)
                        , datetime(2009, 6, 15, 12, 15))
                       , self.elec.periodDateRange())

    def test_getBlackedOutSchedulablePeriods(self):
        now = datetime(2009, 6, 1, 12, 15)
        u = User(first_name = "Test"
               , last_name  = "User"
               , sanctioned = True
                      )
        u.save()
        blackout = create_blackout(user   = u,
                                   repeat = 'Once',
                                   start  = datetime(2009, 6,  8, 11),
                                   end    = datetime(2009, 6, 10, 8))
         
        project = self.elec.session.project
        investigator = Investigator(project = project
                                  , user = u
                                  , observer = True)
        investigator.save()

        # test observer black out
        self.assertEqual([self.period2]
                       , self.elec.getBlackedOutSchedulablePeriods(now))
        blackout = create_blackout(project  = project,
                                   timezone = 'UTC',
                                   start    = datetime(2009, 6, 14),
                                   end      = datetime(2009, 6, 16),
                                   repeat   = 'Once')

        # test project black out
        self.assertEqual([self.period2, self.period3]
                       , self.elec.getBlackedOutSchedulablePeriods(now))

