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

from datetime import datetime, date, timedelta

from pht.utilities import *
from pht.tools.LstPressures import LstPressures
from pht.models         import Proposal
from pht.models         import Semester
from pht.models         import Session
from pht.models         import SessionGrade
from pht.models         import SessionType
from pht.httpadapters   import SessionHttpAdapter
from scheduler.models   import Period as DSSPeriod
from utilities          import TimeAgent
from pht.tools.LstPressureWeather import Pressures
from pht.tests.utils    import *
import numpy

class TestLstPressures(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']


    def setUp(self):

        # get the one proposal and it's one session
        proposal = Proposal.objects.all()[0]
        s = proposal.session_set.all()[0]

        # give it some values so it will show up in plot
        s.grade = SessionGrade.objects.get(grade = 'A')
        s.target.min_lst = 0.0
        s.target.max_lst = hr2rad(12.5)
        s.target.save()
        time = 6.5 # hrs
        s.allotment.allocated_time = time # hrs
        s.allotment.save()
        s.save()
        self.session = s

    def createSession(self):
        "Create a new session for the tests"
        p = Proposal.objects.all()[0]
        return createSession(p)

    def test_getPressures(self):

        wtypes = ['Poor', 'Good', 'Excellent']
        grades = ['A', 'B', 'C']
        types = ["%s_%s" % (w, g) for w in wtypes for g in grades]

        # make sure are session belongs to a future semester, 
        # no matter when we are running this test
        lst = LstPressures()
        semName = lst.futureSemesters[0]
        futureSem, _ = Semester.objects.get_or_create(semester = semName)
        self.session.proposal.semester  = futureSem
        self.session.proposal.save()

        # make sure we start off blank, by adjusting the session
        time = self.session.allotment.allocated_time 
        req  = self.session.allotment.requested_time 
        self.session.allotment.allocated_time = None
        self.session.allotment.requested_time = 0.0
        self.session.allotment.save()

        ps = lst.getPressures()
        for i, p in enumerate(ps):
            self.assertEqual(float(i), p['LST'])
            self.assertEqual(0.0, p['Total'])
            for t in types:
                self.assertEqual(0.0, p[t])

        # partially restore this session
        self.session.allotment.requested_time = req
        self.session.allotment.save()

        # calc pressures
        ps = lst.getPressures()

        # make sure it shows up in it's LST range, but as requested
        for hr in range(12):
            self.assertAlmostEqual(1.75, ps[hr]['Total'], 3)
            self.assertAlmostEqual(1.75, ps[hr]['Requested'], 3)
            self.assertAlmostEqual(1.75, ps[hr]['Requested_Poor'], 3)
            self.assertAlmostEqual(0.0,  ps[hr]['Requested_Good'], 3)

        # make sure it doesn't show up out of it's range
        for hr in range(12, 24):
            self.assertEqual(float(hr), ps[hr]['LST'])
            self.assertEqual(0.0, ps[hr]['Total'])

        # restore this session
        self.session.allotment.allocated_time = time
        self.session.allotment.requested_time = req
        self.session.allotment.save()

        # calc pressures
        ps = lst.getPressures()

        # make sure it shows up in it's LST range
        for hr in range(12):
            self.assertAlmostEqual(0.5416666, ps[hr]['Total'], 3)
            self.assertAlmostEqual(0.5416666, ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(0.0,       ps[hr]['Requested'], 3)
            for t in types:
                if t != 'Poor_A':
                    self.assertEqual(0.0, ps[hr][t])

        # make sure it doesn't show up out of it's range
        for hr in range(12, 24):
            self.assertEqual(float(hr), ps[hr]['LST'])
            self.assertEqual(0.0, ps[hr]['Total'])
            for t in types:
                self.assertEqual(0.0, ps[hr][t])

    def test_getPressures2(self):

        lst = LstPressures()

        # make sure are session belongs to a future semester, 
        # no matter when we are running this test
        semName = lst.futureSemesters[0]
        futureSem, _ = Semester.objects.get_or_create(semester = semName)
        self.session.proposal.semester  = futureSem
        self.session.proposal.save()

        wtypes = ['Poor', 'Good', 'Excellent']
        grades = ['A', 'B', 'C']
        types = ["%s_%s" % (w, g) for w in wtypes for g in grades]

        # make this session a fixed session, and watch the hours 
        # get distributed across the weathers
        self.session.session_type = SessionType.objects.get(type = 'Fixed')
        self.session.save()

        # calc pressures
        ps = lst.getPressures()

        # make sure it shows up in it's LST range
        s1total = 0.5416
        for hr in range(12):
            self.assertAlmostEqual(s1total, ps[hr]['Total'], 3)
            self.assertAlmostEqual(s1total * 0.50, ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Good_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Excellent_A'], 3)

        # make sure it doesn't show up out of it's range
        for hr in range(12, 24):
            self.assertEqual(float(hr), ps[hr]['LST'])
            self.assertEqual(0.0, ps[hr]['Total'])
            for t in types:
                self.assertEqual(0.0, ps[hr][t])

        # add a new session and make sure it shows up
        s = self.createSession()
        # covers this LST range:
        # [ 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  1.  1.  1.  1.  1.  1.  1.  1.  1.  1.  0.  0.  0.  0.]
        # compared to the original:
        # [ 1.  1.  1.  1.  1.  1.  1.  1.  1.  1.  1.  1.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.]

        # calc pressures
        ps = lst.getPressures()
        s2total = 0.35 #0.318181818182    

        # the first 10 hours are just the first session
        for hr in range(10):
            self.assertAlmostEqual(s1total, ps[hr]['Total'], 3)
            self.assertAlmostEqual(s1total * 0.50, ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Good_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Excellent_A'], 3)
        
        # the next two are combined 
        for hr in range(10, 12):
            self.assertAlmostEqual(s1total + s2total, ps[hr]['Total'], 3)
            self.assertAlmostEqual((s1total * 0.50) + s2total, ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Good_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Excellent_A'], 3)

        # up to 20 it's just the second session    
        for hr in range(12, 20):
            self.assertAlmostEqual(s2total, ps[hr]['Total'], 3)
            self.assertAlmostEqual(s2total, ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(0.0, ps[hr]['Good_A'], 3)
            self.assertAlmostEqual(0.0, ps[hr]['Excellent_A'], 3)

        # make sure there's nothing at the end 
        for hr in range(21, 24):
            self.assertEqual(float(hr), ps[hr]['LST'])
            self.assertEqual(0.0, ps[hr]['Total'])
            for t in types:
                self.assertEqual(0.0, ps[hr][t])

    def test_getPressures3(self):
        """it's a trilogy.
        Here are the examples I'll be using in my unit tests:
        # MIN   MAX    BINS
        
        1 00:00 01:00  0
        2 00:00 10:00  0,1,2,3,4,5,6,7,8,9 ([0,9])
        3 00:30 01:30  0
        4 10:00 10:59  10
        5 00:30 10:59  [0-9]
        6 22:30 08:59  22,23,[0-7]
        """

        lst = LstPressures()

        # make sure are session belongs to a future semester, 
        # no matter when we are running this test
        semName = lst.futureSemesters[0]
        futureSem, _ = Semester.objects.get_or_create(semester = semName)
        self.session.proposal.semester  = futureSem
        self.session.proposal.save()

        # 1
        self.session.target.min_lst = hr2rad(0.0)
        self.session.target.max_lst = hr2rad(1.0)
        self.session.target.save()
        ps = lst.getPressures()
        exp = [1.0]
        off = [0.0]*23
        exp.extend(off)
        self.assertEqual(exp, self.nonZeroResults(ps))

        # 2
        self.session.target.min_lst = hr2rad(0.0)
        self.session.target.max_lst = hr2rad(10.0)
        self.session.target.save()
        ps = lst.getPressures()
        exp = [1.0]*10
        off = [0.0]*14
        exp.extend(off)
        self.assertEqual(exp, self.nonZeroResults(ps))
       
        # 3
        self.session.target.min_lst = hr2rad(0.5)
        self.session.target.max_lst = hr2rad(1.5)
        self.session.target.save()
        ps = lst.getPressures()
        exp = [1.0]
        exp.extend([0.0]*23)
        self.assertEqual(exp, self.nonZeroResults(ps))

        # 4
        self.session.target.min_lst = hr2rad(10.0)
        self.session.target.max_lst = hr2rad(10.9)
        self.session.target.save()
        ps = lst.getPressures()
        exp = [0.0]*10
        exp.append(1.0)
        exp.extend([0.0]*13)
        self.assertEqual(exp, self.nonZeroResults(ps))

        # 5
        self.session.target.min_lst = hr2rad(0.5)
        self.session.target.max_lst = hr2rad(10.9)
        self.session.target.save()
        ps = lst.getPressures()
        exp = [1.0]*10
        exp.extend([0.0]*14)
        self.assertEqual(exp, self.nonZeroResults(ps))

        # 6
        self.session.target.min_lst = hr2rad(22.5)
        self.session.target.max_lst = hr2rad(8.9)
        self.session.target.save()
        ps = lst.getPressures()
        exp = [1.0]*8
        exp.extend([0.0]*14)
        exp.extend([1.0]*2)
        self.assertEqual(exp, self.nonZeroResults(ps))
            
    def nonZeroResults(self, pressureDict, key = 'Total'):
        xs = [0.0]*24
        for hr in range(24):
            if pressureDict[hr][key] > 0.0:
                xs[hr] = 1.0
        return xs

    def test_getPressuresForSession(self):

        lst = LstPressures()
        ps = lst.getPressuresForSession(self.session)
        exp  = [0.54166]*12
        off = [0.0]*12
        exp.extend(off)
        for i in range(24):
            self.assertAlmostEqual(exp[i], ps[i], 3)
 
        # set night time flag
        self.session.flags.thermal_night = True
        ps = lst.getPressuresForSession(self.session)
        # changes non-zero ones 
        exp = [0.63214550853749085, 0.68040089086859701, 0.68522642910170761, 0.68040089086859701, 0.68040089086859701, 0.62249443207126953, 0.56458797327394228, 0.50668151447661469, 0.44877505567928738, 0.39086859688195996, 0.33296213808463254, 0.27505567928730518]
        exp.extend([0.0]*12)
        for i in range(len(exp)):
            self.assertAlmostEqual(exp[i], ps[i], 3)

    def test_getLstWeightsForSession(self):

        lst = LstPressures()

        # this is easy when min = 0, max = 12 LST
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*12
        off = [0.0]*12
        exp.extend(off)
        self.assertEqual(exp, ws.tolist())

        # change min/max lst and see what happens
        self.session.target.min_lst = hr2rad(20.0)
        self.session.target.max_lst = hr2rad(4.0)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*4
        off = [0.0]*16
        exp.extend(off)
        exp.extend([1.0]*4)
        self.assertEqual(exp, ws.tolist())

        # catch an edge case
        self.session.target.min_lst = hr2rad(23.5)
        self.session.target.max_lst = hr2rad(1.2)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]
        exp.extend([0.0]*22)
        exp.append(1.0)
        self.assertEqual(exp, ws.tolist())

    def test_getLstWeightsForSession_2(self):
        """the sequal
        Here are the examples I'll be using in my unit tests:
        # MIN   MAX    BINS
        
        1 00:00 01:00  0
        2 00:00 10:00  0,1,2,3,4,5,6,7,8,9 ([0,9])
        3 00:30 01:30  0
        4 10:00 10:59  10
        5 00:30 10:59  [0-9]
        6 22:30 08:59  22,23,[0-7]
        """

        lst = LstPressures()

        # 1
        self.session.target.min_lst = hr2rad(0.0)
        self.session.target.max_lst = hr2rad(1.0)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]
        off = [0.0]*23
        exp.extend(off)
        self.assertEqual(exp, ws.tolist())

        # 2
        self.session.target.min_lst = hr2rad(0.0)
        self.session.target.max_lst = hr2rad(10.0)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*10
        off = [0.0]*14
        exp.extend(off)
        self.assertEqual(exp, ws.tolist())
       
        # 3
        self.session.target.min_lst = hr2rad(0.5)
        self.session.target.max_lst = hr2rad(1.5)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]
        exp.extend([0.0]*23)
        self.assertEqual(exp, ws.tolist())

        # 4
        self.session.target.min_lst = hr2rad(10.0)
        self.session.target.max_lst = hr2rad(10.9)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [0.0]*10
        exp.append(1.0)
        exp.extend([0.0]*13)
        self.assertEqual(exp, ws.tolist())

        # 5
        self.session.target.min_lst = hr2rad(0.5)
        self.session.target.max_lst = hr2rad(10.9)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*10
        exp.extend([0.0]*14)
        self.assertEqual(exp, ws.tolist())

        # 6
        self.session.target.min_lst = hr2rad(22.5)
        self.session.target.max_lst = hr2rad(8.9)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*8
        exp.extend([0.0]*14)
        exp.extend([1.0]*2)
        self.assertEqual(exp, ws.tolist())

        # one more ...
        self.session.target.min_lst = hr2rad(15.91) #1.73)
        self.session.target.max_lst = hr2rad(1.73) #15.91)
        ws = lst.getLstWeightsForSession(self.session)
        exp =  [1]
        exp.extend([0]*14)
        exp.extend([1]*9)
        self.assertEqual(exp, ws.tolist())


    def test_modifyWeightsForLstExclusion(self):

        lst = LstPressures()
        ws = [1.0]*24

        # this session doesn't have lst exclusion
        ws2 = lst.modifyWeightsForLstExclusion(self.session, ws)

        # so the weights don't get modified
        self.assertEqual(ws, ws2)

        # now introduce some exclusions
        adapter = SessionHttpAdapter(self.session)
        adapter.update_lst_parameters('lst_ex', '4.5-7.2,21.2-23.0')
        # get the refreshed session
        s = Session.objects.get(id = self.session.id)
        ws3 = lst.modifyWeightsForLstExclusion(s, ws)
        
    def test_getFlagWeightsForSession(self):

        lst = LstPressures()
        exp = [1.0]*24

        # this session doesn't have any flags set
        fs = lst.getFlagWeightsForSession(self.session)

        # so the weights are all 1.0 
        self.assertEqual(exp, fs)

        # now set the PTCS night time flag
        self.session.flags.thermal_night = True
        fs = lst.getFlagWeightsForSession(self.session)
        self.assertEqual(lst.thermalNightWeights.tolist(), fs.tolist())
        
    def test_computeThermalNightWeights(self):

        lst = LstPressures()
        # time range: Jan 1 - 30, 2012
        start = datetime(2012, 1, 1)
        ws, ex = lst.computeThermalNightWeights(start = start, numDays = 30)
        exp = [0, 0, 6, 18, 30, 30, 30, 30, 30, 30, 30, 30, 30, 29, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEquals(exp, ex)
        # time range: June 1 - 30, 2012
        start2 = datetime(2012, 6, 1)
        ws, ex = lst.computeThermalNightWeights(start = start2, numDays = 30)
        exp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 28, 30, 30, 30, 30, 18, 4, 0]
        self.assertEquals(exp, ex)
        # time range: Jan 1 - Dec 31, 2012
        ws, ex = lst.computeThermalNightWeights(start = start, numDays = 365)
        exp = [140, 141, 142, 141, 141, 140, 139, 140, 140, 140, 140, 141, 140, 138, 136, 130, 123, 115, 109, 109, 116, 124, 132, 137]
        self.assertEquals(exp, ex)
        self.assertEqual(ex[0]/365., ws[0])
        self.assertEqual(ex[12]/365., ws[12])

    def test_computeOpticalNightWeights(self):

        lst = LstPressures()

        # Note that the exclusion zone here is smaller than that 
        # for PTCS night time
        # time range: Jan 1 - 30, 2012
        start = datetime(2012, 1, 1)
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 30)
        exp = [18, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 29, 14, 0, 0, 0, 0, 0, 0, 0, 0, 6]
        self.assertEqual(exp, ex)
        # time range: Jan 1 - Dec 31, 2012
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 365)
        exp = [179, 178, 178, 177, 177, 176, 176, 176, 177, 177, 177, 178, 178, 179, 180, 180, 181, 182, 182, 182, 182, 181, 180, 179]
        self.assertEqual(exp, ex)
       
    def test_getRfiRiseSet(self):

        lst = LstPressures()

        dt = date(2012, 1, 1)
        rs = lst.getRfiRiseSet(dt)
        exp = (datetime(2012, 1, 1, 13), datetime(2012, 1, 2, 1))
        self.assertEqual(exp, rs)

        # note change in DST
        dt = date(2012, 6, 1)
        rs = lst.getRfiRiseSet(dt)
        exp = (datetime(2012, 6, 1, 12), datetime(2012, 6, 2, 0))
        self.assertEqual(exp, rs)

    def test_computeRfiWeights(self):

        lst = LstPressures()
        # Jan 1, 2012
        start = datetime(2012, 1, 1)
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1) #numDays = 1, month = 1)
        exp = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(exp, ex)
        # Jan 1 - 30, 2012
        ws, ex = lst.computeRfiWeights(start = start, numDays = 30)
        exp = [0, 0, 9, 25, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 20, 5, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(exp, ex)
        # Jan 1 - Dec 31, 2012
        ws, ex = lst.computeRfiWeights(start = start, numDays = 365)
        exp = [167, 166, 166, 167, 167, 167, 182, 182, 182, 188, 197, 198, 197, 197, 197, 197, 198, 196, 182, 182, 183, 176, 167, 167]
        self.assertEqual(exp, ex)

    def test_getPressuresFromPeriod(self):

        lst = LstPressures()

        # make period
        p = DSSPeriod(start = datetime(2012, 4, 5, 12)
                    , duration = 3.0
                     )
        
        ps = lst.getPressuresFromPeriod(p)
        exp1 = [0.0] * 19
        self.assertEqual(exp1, ps[:19])
        self.assertAlmostEqual(0.37668728573623156, ps[19], 3)
        self.assertEqual(1.0, ps[20])
        self.assertEqual(1.0, ps[21])
        self.assertAlmostEqual(0.63152644233784727, ps[22], 3)
        self.assertEqual(0.0, ps[23])


        # make one that wraps around
        p2 = DSSPeriod(start = datetime(2012, 4, 5, 12)
                     , duration = 12.0
                      )
        ps2 = lst.getPressuresFromPeriod(p2)
        self.assertEqual([1.0]*7, ps2[:7])
        self.assertEqual([0.0]*11, ps2[8:19])
        self.assertEqual([1.0]*4, ps2[20:])
        self.assertAlmostEqual(0.65616762656011396,ps2[7],3)
        self.assertAlmostEqual(0.37668728573623156,ps2[19],3)

        # combine the periods
        periods = [p, p2]
        ps3 = lst.getPressuresFromPeriods(periods)
        exp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.65616762656011396, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75337457147246312, 2.0, 2.0, 1.6315264423378473, 1.0]
        for i in range(len(exp)):
            self.assertAlmostEqual(exp[i], ps3[i], 3)

    def test_use_case_1(self):

        lst = LstPressures()

        # Consider a 24 hour long session that is circumpolar.
        # Date: September 21, 2012
        # Sunrise: approximately 7:14 EDT
        # Sunset: approximately 19:14 EDT
        start = datetime(2012, 9, 21) 
        rise, set =  lst.sun.getRiseSet(start)
        rise = TimeAgent.utc2est(rise)
        set = TimeAgent.utc2est(set)
        self.assertEqual(rise, datetime(2012, 9, 21, 7, 6, 21))
        self.assertEqual(set,  datetime(2012, 9, 21, 19, 17, 25))

        # Optical Nighttime flag should be 1 from 00:00 EDT to 07:00 EDT
        # and 20:00 EDT to 24:00 EDT.  This corresponds to
        #roughly 18:00-05:00 LST.
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 1)
        # 1 from 0 - 4, and 18 - 23:
        exp = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
        self.assertEquals(exp, ex) 

        # Thermal Nighttime flag would then be 21:00-05:00 LST
        ws, ex = lst.computeThermalNightWeights(start = start, numDays = 1)
        exp = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
        self.assertEquals(exp, ex) 
        
        # RFI is between 8 AM and 8 PM EST.
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1)
        exp = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
        self.assertEquals(exp, ex)

    def test_adjustForOverfilledWeather_1(self):

        lst = LstPressures()

        # setup to be like use case 3.4.1
        gradeA = Pressures()
        gradeA.poor = numpy.array([28.0]*lst.hrs)
        gradeA.good = numpy.array([35.0]*lst.hrs)
        gradeA.excellent = numpy.array([25.0]*lst.hrs)
        carryover = Pressures()
        carryover.poor = numpy.array([22.0]*lst.hrs)

        alloc, chg = lst.adjustForOverfilledWeather(gradeA
                                                  , carryover
                                                  , lst.weather.availability
                                                   )
        expC = Pressures()
        # assert that there was no change
        for w in ['poor', 'good', 'excellent']:
            for i in range(lst.hrs):
                self.assertEquals(gradeA.getType(w)[i]
                                , alloc.getType(w)[i])
                self.assertEquals(0.0, expC.getType(w)[i])

    def test_adjustForOverfilledWeather_2(self):

        lst = LstPressures()

        # setup to be like use case 3.4.2
        gradeA = Pressures()
        gradeA.poor = numpy.array([59.5]*lst.hrs)
        gradeA.good = numpy.array([15.0]*lst.hrs)
        gradeA.excellent = numpy.array([25.0]*lst.hrs)
        carryover = Pressures()
        carryover.poor = numpy.array([45.0]*lst.hrs)
        carryover.good = numpy.array([10.0]*lst.hrs)
        carryover.excellent = numpy.array([0.0]*lst.hrs)

        alloc, chg = lst.adjustForOverfilledWeather(gradeA
                                                  , carryover
                                                  , lst.weather.availability
                                                   )

        # here's the change we expect
        exp = Pressures() 
        exp.poor = numpy.array([45.5]*lst.hrs)
        exp.good = numpy.array([29.0]*lst.hrs)
        exp.excellent = numpy.array([25.0]*lst.hrs)
        expC = Pressures() 
        expC.poor = numpy.array([14.]*lst.hrs)
        expC.good = numpy.array([14.]*lst.hrs)
        for w in ['poor', 'good', 'excellent']:
            for i in range(lst.hrs):
                self.assertEquals(exp.getType(w)[i]
                                , alloc.getType(w)[i])
                self.assertEquals(expC.getType(w)[i]
                                , chg.getType(w)[i])

    def test_adjustForOverfilledWeather_3(self):

        lst = LstPressures()

        # setup to be like use case 3.4.3
        gradeA = Pressures()
        gradeA.poor = numpy.array([79.5]*lst.hrs)
        gradeA.good = numpy.array([15.0]*lst.hrs)
        gradeA.excellent = numpy.array([25.0]*lst.hrs)
        carryover = Pressures()
        carryover.poor = numpy.array([45.0]*lst.hrs)
        carryover.good = numpy.array([10.0]*lst.hrs)
        carryover.excellent = numpy.array([0.0]*lst.hrs)

        alloc, chg = lst.adjustForOverfilledWeather(gradeA
                                                  , carryover
                                                  , lst.weather.availability
                                                   )

        # here's the change we expect
        exp = Pressures() 
        exp.poor = numpy.array([45.5]*lst.hrs)
        exp.good = numpy.array([35.25]*lst.hrs)
        exp.excellent = numpy.array([38.75]*lst.hrs)
        expC = Pressures() 
        expC.poor = numpy.array([34.]*lst.hrs)
        expC.good = numpy.array([20.25]*lst.hrs)
        expC.excellent = numpy.array([13.75]*lst.hrs)
        for w in ['poor', 'good', 'excellent']:
            for i in range(lst.hrs):
                self.assertEquals(exp.getType(w)[i]
                                , alloc.getType(w)[i])                                
                self.assertEquals(expC.getType(w)[i]
                                , chg.getType(w)[i])

    def test_isCarryover(self):

        lst = LstPressures()

        # our session is in 12A; for testing, do some time travel

        # today is long before that - of course our session is new!
        dt = datetime(2009, 10, 1)
        carryover = lst.isCarryover(self.session, today = dt)
        self.assertEqual(False, carryover)

        # today is in 12A - same semester! so now we're carryover
        dt = datetime(2012, 6, 1)
        carryover = lst.isCarryover(self.session, today = dt)
        self.assertEqual(True, carryover)

        # today is in 12B - this session was in our past - it's carryover
        dt = datetime(2012, 10, 1)
        carryover = lst.isCarryover(self.session, today = dt)
        self.assertEqual(True, carryover)

