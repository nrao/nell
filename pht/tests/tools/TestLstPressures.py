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
        sem = Semester.objects.get(semester = '12A')
        data  = {
            'name' : 'nextSemesterSession'
          , 'pcode' : p.pcode
          , 'grade' : 'A'  
          , 'semester' : sem
          , 'requested_time' : 3.5  
          , 'allocated_time' : 3.5  
          , 'session_type' : 'Open - Low Freq'
          , 'observing_type' : 'continuum' 
          , 'weather_type' : 'Poor'
          , 'repeats' : 2 
          , 'min_lst' : '10:00:00.0' 
          , 'max_lst' : '20:00:00.0' 
          , 'elevation_min' : '00:00:00.0' 
          , 'next_sem_complete' : False
          , 'next_sem_time' : 1.0
          , 'receivers' : 'L'
        }

        adapter = SessionHttpAdapter()
        adapter.initFromPost(data)
        # just so that is HAS a DSS session.
        #adapter.session.dss_session = self.maintProj.sesshun_set.all()[0]
        adapter.session.save()
        return adapter.session

    def test_getPressures(self):

        wtypes = ['Poor', 'Good', 'Excellent']
        grades = ['A', 'B', 'C']
        types = ["%s_%s" % (w, g) for w in wtypes for g in grades]

        # make sure we start off blank, by adjusting the session
        time = self.session.allotment.allocated_time 
        self.session.allotment.allocated_time = None
        self.session.allotment.save()

        lst = LstPressures()
        ps = lst.getPressures()
        for i, p in enumerate(ps):
            self.assertEqual(float(i), p['LST'])
            self.assertEqual(0.0, p['Total'])
            for t in types:
                self.assertEqual(0.0, p[t])

        # restore this session
        self.session.allotment.allocated_time = time
        self.session.allotment.save()

        # calc pressures
        ps = lst.getPressures()

        # make sure it shows up in it's LST range
        for hr in range(12):
            self.assertAlmostEqual(0.5416666, ps[hr]['Total'], 3)
            self.assertAlmostEqual(0.5416666, ps[hr]['Poor_A'], 3)
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

        # calc pressures
        ps = lst.getPressures()
        s2total = 0.318181818182    

        # the first 10 hours are just the first session
        for hr in range(9):
            self.assertAlmostEqual(s1total, ps[hr]['Total'], 3)
            self.assertAlmostEqual(s1total * 0.50, ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Good_A'], 3)
            self.assertAlmostEqual(s1total * 0.25, ps[hr]['Excellent_A'], 3)
        
        # the next two are combined 
        for hr in range(9, 12):
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
        # changes non-zero ones by a little bit.
        exp = [0.54267161410018538, 0.54025974025974011, 0.53784786641929494, 0.54025974025974011, 0.54025974025974011, 0.54267161410018538, 0.54508348794063066, 0.54267161410018538, 0.54267161410018538, 0.54267161410018538, 0.54267161410018538, 0.54025974025974011]
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
        self.assertEqual(exp, ws)

        # change min/max lst and see what happens
        self.session.target.min_lst = hr2rad(20.0)
        self.session.target.max_lst = hr2rad(4.0)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*4
        off = [0.0]*16
        exp.extend(off)
        exp.extend([1.0]*4)
        self.assertEqual(exp, ws)

        # catch an edge case
        self.session.target.min_lst = hr2rad(23.5)
        self.session.target.max_lst = hr2rad(1.2)
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]
        exp.extend([0.0]*22)
        exp.append(1.0)
        self.assertEqual(exp, ws)

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
        self.assertEqual(lst.thermalNightWeights, fs)
        
    def test_computeThermalNightWeights(self):

        lst = LstPressures()
        ws, ex = lst.computeThermalNightWeights(month = 1, numDays = 30)
        exp = [30, 30, 24, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 16, 30, 30, 30, 30, 30, 30, 30, 30, 30]
        self.assertEquals(exp, ex)
        ws, ex = lst.computeThermalNightWeights(month = 6, numDays = 30)
        exp = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 17, 2, 0, 0, 0, 0, 12, 26, 30]
        self.assertEquals(exp, ex)
        ws, ex = lst.computeThermalNightWeights()
        exp = [225, 224, 223, 224, 224, 225, 226, 225, 225, 225, 225, 224, 225, 227, 229, 235, 242, 250, 256, 256, 249, 241, 233, 228]
        self.assertEquals(exp, ex)
        self.assertEqual(ex[0]/365., ws[0])
        self.assertEqual(ex[12]/365., ws[12])

    def test_computeOpticalNightWeights(self):

        lst = LstPressures()

        # Note that the exclusion zone here is smaller than that 
        # for PTCS night time
        ws, ex = lst.computeOpticalNightWeights(month = 1, numDays = 30)
        exp = [12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 16, 30, 30, 30, 30, 30, 30, 30, 30, 24]
        self.assertEqual(exp, ex)
        ws, ex = lst.computeOpticalNightWeights()
        exp = [186, 187, 187, 188, 188, 189, 189, 189, 188, 188, 188, 187, 187, 186, 185, 185, 184, 183, 183, 183, 183, 184, 185, 186]
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
        ws, ex = lst.computeRfiWeights(numDays = 1, month = 1)
        exp = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.assertEqual(exp, ex)
        ws, ex = lst.computeRfiWeights(numDays = 30, month = 1)
        exp = [30, 30, 21, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 25, 30, 30, 30, 30, 30, 30, 30, 30] 
        self.assertEqual(exp, ex)
        ws, ex = lst.computeRfiWeights()
        exp =[198, 199, 199, 198, 198, 198, 183, 183, 183, 177, 168, 167, 168, 168, 168, 168, 167, 169, 183, 183, 182, 189, 198, 198]
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
