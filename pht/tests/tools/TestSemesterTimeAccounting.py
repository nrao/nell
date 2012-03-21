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

from django.test         import TestCase


from pht.tools.SemesterTimeAccounting import SemesterTimeAccounting
from pht.tools.SemesterTimeAccounting import SemesterTimes, Times

from scheduler.models import Period as DSSPeriod
from scheduler.models import Semester as DSSSemester
from scheduler.models import Project
from scheduler.tests.utils import * 
from pht.models import *
from pht.utilities import *

class TestSemesterTimeAccounting(TestCase):
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):
        """
        Setup periods to look like this:

        UTC:   |12345678901234567890123|12345678901234567890123|
        GC:    |   <--------->         |  <---------->         |
        Day:   |          <------------|-->       <------------|
        Maint: |                xxxx   |        xxxxxxxx       |
        """
        self.semester = '12A'
        self.ta = SemesterTimeAccounting(self.semester)

        # make some maintenance periods
        self.maintProj = create_maintenance_project()
        # daytime period:
        dt1 = datetime(2012, 3, 20, 13) # EST
        mp1 = create_maintenance_period(dt1, 4.0)
        # TBF: bug?
        mp1.session.project = self.maintProj
        mp1.session.save()
        # day & night period
        dt2 = datetime(2012, 3, 21, 5) # EST
        mp2 = create_maintenance_period(dt2, 8.0)
        # TBF: bug?
        mp2.session.project = self.maintProj
        mp2.session.save()
        self.maintPeriods = [mp1, mp2]

        # BUG: this observing type missing in scheduler.json fixture
        o = Observing_Type(type = 'commissioning')
        o.save()

    def tearDown(self):

        # clean up
        for p in self.maintPeriods:
            s = p.session
            p.remove()
            s.delete()

        self.maintProj.delete()

    def createTestingSessions(self):
        """
        Create a PHT Session that will be one of the 'testing' 
        types, for this semester, and that does not overlap
        with the Galactic Center.
        """
     
        # I'm lazy; let's just change the session we've already got
        p = Proposal.objects.all()[0]
        s = p.session_set.all()[0]
        s.observing_type = Observing_Type.objects.get(type = 'testing')
        semester = Semester.objects.get(semester = self.semester)
        s.semester = semester
        s.target.min_lst = 0.0
        s.target.max_lst = hr2rad(5.0)
        s.target.save()
        s.allotment.allocated_time = 2.5
        s.allotment.save()
        s.save()
        return [s]


    def test_getSemesterDays(self):
        self.assertEqual(181, self.ta.getSemesterDays())
        self.assertEqual(183, self.ta.getSemesterDays(semester = '12B'))
    
    def test_getGCHrs(self):
        self.assertEqual(6.0, self.ta.getGCHrs(24.0))

    def test_getMaintenancePeriods(self):

        ps = self.ta.getMaintenancePeriods()
        self.assertEqual(2, len(ps))
        self.assertEqual(self.maintPeriods[0].start
                       , ps[0].start)

    def test_getTestSessions(self):

        ss = self.ta.getTestSessions()
        self.assertEqual(0, len(ss))
        self.createTestingSessions()
        ss = self.ta.getTestSessions()
        self.assertEqual(1, len(ss))

    def test_getSessionHours(self):

        
        s = self.createTestingSessions()[0]
        ts = self.ta.getSessionHours(s)
        exp = Times(total = 2.5
                  , lowFreq = 2.5)
        self.assertEqual(exp, ts.total)          
        self.assertEqual(Times(), ts.gc)          

        # now change it's lst range to intersect
        # with the GC
        s.target.min_lst = hr2rad(10.0)
        s.target.max_lst = hr2rad(20.0)
        s.target.save()
        ts = self.ta.getSessionHours(s)
        self.assertEqual(exp, ts.total)          
        exp = Times(total = 1.25 
                  , lowFreq = 1.25)
        self.assertEqual(exp, ts.gc)          

    def test_getPeriodHours(self):

        # day time only period
        mp1 = self.maintPeriods[0]
        hrs = self.ta.getPeriodHours(mp1)
        exp = Times(total = 4.0
             , lowFreq = 2.0
             , hiFreq1 = 1.0
             , hiFreq2 = 1.0
             )
        self.assertEqual(exp, hrs.total)     

        # a little night AND day period
        mp2 = self.maintPeriods[1]
        hrs = self.ta.getPeriodHours(mp2)
        self.assertEqual(8.0, hrs.total.total) 
        self.assertEqual(4.0, hrs.total.lowFreq) 
        self.assertAlmostEqual(2.0, hrs.total.hiFreq1, 3) 
        self.assertAlmostEqual(2.0, hrs.total.hiFreq2, 3) 

        self.assertAlmostEqual(5.3558844564835955, hrs.gc.total, 3) 

    def test_getHrsInGC(self):

        # LST of 17.5 - 18.5 is entirely in GC
        dur = 1.0
        dt1 = datetime(2012, 3, 19, 11)
        dt2 = dt1 + timedelta(hours = dur)
        self.assertEqual((dur, 0.0), self.ta.getHrsInGC(dt1, dt2))

        # LST of 12.5 - 13.5 is entirely NOT in GC
        dur = 1.0
        dt1 = datetime(2012, 3, 19, 6)
        dt2 = dt1 + timedelta(hours = dur)
        self.assertEqual((0.0, dur), self.ta.getHrsInGC(dt1, dt2))

        # LST of 12.5 - 17.5 overlaps with GC by about 2.5 hrs
        dur = 5.0
        dt1 = datetime(2012, 3, 19, 6)
        dt2 = dt1 + timedelta(hours = dur)
        gc, nonGc = self.ta.getHrsInGC(dt1, dt2)
        self.assertAlmostEquals(gc + nonGc, dur, 3)
        self.assertAlmostEquals(2.50350778689, nonGc, 3)
        self.assertAlmostEquals(2.49649221311, gc, 3)

        # LST of 12.5 - 23.5 encompasses all of GC - 6 hours
        dur = 11.0
        dt1 = datetime(2012, 3, 19, 6)
        dt2 = dt1 + timedelta(hours = dur)
        gc, nonGc = self.ta.getHrsInGC(dt1, dt2)
        self.assertAlmostEquals(gc + nonGc, dur, 3)
        self.assertAlmostEquals(5.9836173979, gc, 3)
        self.assertAlmostEquals(5.0163826021, nonGc, 3)

        # make sure LST wrap around is OK: 18.5 to 2.5
        dur = 12
        dt1 = datetime(2012, 3, 19, 12)
        dt2 = dt1 + timedelta(hours = dur)
        gc, nonGc = self.ta.getHrsInGC(dt1, dt2)
        self.assertAlmostEquals(gc + nonGc, dur, 3)
        self.assertAlmostEquals(2.48694527307, gc, 3)
        self.assertAlmostEquals(9.51305472693, nonGc, 3)

    def test_getHrsInDayTime(self):

        # all night time
        dur = 1.0
        dt1 = datetime(2012, 3, 19, 1)
        dt2 = dt1 + timedelta(hours = dur)
        day, night = self.ta.getHrsInDayTime(dt1, dt2)
        self.assertEquals(day, 0.0)
        self.assertEquals(night, dur)

        # all day time
        dur = 1.0
        dt1 = datetime(2012, 3, 19, 13)
        dt2 = dt1 + timedelta(hours = dur)
        day, night = self.ta.getHrsInDayTime(dt1, dt2)
        self.assertEquals(day, dur)
        self.assertEquals(night, 0.0)

        # small overlap
        dur = 6.0
        dt1 = datetime(2012, 3, 19, 9)
        dt2 = dt1 + timedelta(hours = dur)
        day, night = self.ta.getHrsInDayTime(dt1, dt2)
        self.assertEquals(dur, day + night) 
        self.assertEquals(day, 3.61)
        self.assertEquals(night, 2.39)

        # multi-day time range - like a long shutdown
        dur = (24*2.0) + 11.0
        dt1 = datetime(2012, 3, 19, 12)
        dt2 = dt1 + timedelta(hours = dur)
        day, night = self.ta.getHrsInDayTime(dt1, dt2)
        self.assertEquals(dur, day + night) 
        self.assertAlmostEquals(41.348888888888887, day, 3)
        self.assertAlmostEquals(17.6511111111, night, 3)

    def test_calculateTimeAccounting(self):
        """
        Here's where we tie it all together:
        """

        # calculate everything
        self.ta.calculateTimeAccounting()

        # check the buckets
        totalAv = self.ta.totalAvailableHrs
        self.assertEqual(181*24, totalAv.total.total)
        self.assertEqual((181*24)*(6/24.), totalAv.gc.total)
        # TBF: other totalAv.total fields?

        hrs = self.ta.maintHrs
        expMntT = Times(total = 12.0
                  , lowFreq = 6.0
                  , hiFreq1 = 3.0
                  , hiFreq2 = 3.0
                    )
        self.assertEqual(expMntT, hrs.total)            
        expMntGC = Times(total =  5.355884) # TBF other fields?
        self.assertAlmostEqual(expMntGC.total, hrs.gc.total, 3)

        # no shutdown or testing
        hrs = self.ta.shutdownHrs
        self.assertEqual(Times(), hrs.total)     
        hrs = self.ta.testHrs
        self.assertEqual(Times(), hrs.total)     

        self.ta.checkTimes()

        expAvT = Times(total = 4332.
                  , lowFreq = 2166.0
                  , hiFreq1 = 1083.0
                  , hiFreq2 = 1083.0
                   )
        self.assertEqual(expAvT, self.ta.astronomyAvailableHrs.total)           
        expAvGC = Times(total = 1080.6441)
        self.assertAlmostEqual(expAvGC.total
                             , self.ta.astronomyAvailableHrs.gc.total, 3)

        # now introduce some 12A testing time 
        ss = self.createTestingSessions()

        # and recalculate everything
        self.ta.calculateTimeAccounting()

        # these should not have changed
        totalAv = self.ta.totalAvailableHrs
        self.assertEqual(181*24, totalAv.total.total)
        self.assertEqual((181*24)*(6/24.), totalAv.gc.total)

        # but now we have testing
        exp = Times(total = 2.5
                  , lowFreq = 2.5)
        self.assertEqual(exp, self.ta.testHrs.total)

        # which lowers our overall available time
        expAvT = expAvT - exp
        self.assertEqual(expAvT
                       , self.ta.astronomyAvailableHrs.total)           

        #self.ta.report()




