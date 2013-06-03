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

from datetime           import datetime, date, timedelta
from pht.utilities      import *
from pht.models         import Proposal
from pht.models         import Semester
from pht.models         import Session
from pht.models         import SessionGrade
from pht.models         import SessionType
from pht.httpadapters   import SessionHttpAdapter
from scheduler.models   import Sesshun as DSSSesshun
from scheduler.models   import Period as DSSPeriod
from scheduler.models   import Project as DSSProject
from scheduler.models   import Semester as DSSSemester
from scheduler.models   import Status as DSSStatus
from utilities          import TimeAgent
from pht.tests.utils    import *
from scheduler.tests.utils        import create_sesshun
from pht.tools.LstPressures       import LstPressures
from pht.tools.LstPressures       import *
from pht.tools.LstPressureWeather import Pressures
import numpy
from pht.tools.PlotLstPressures import PlotLstPressures

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
        s.allotment.allocated_repeats = 1 
        s.allotment.save()
        s.save()
        self.session = s

        # too lazy to re create 'scheduler.json', so put in the
        # future semesters we need
        for i in range(13, 33):
            for sem in ['A', 'B']:
                semester = "%s%s" % (i, sem)
                s = DSSSemester(semester = semester)
                s.save()

        # again, too lazy to fix the fixture: add these observing types
        t = 'commissioning'
        ot, created = Observing_Type.objects.get_or_create(type = t)

        self.lst = LstPressures()


    def printSession(self, s):
        "For reporting"

        print "name: %s" % s.name
        print "allocatted hours: %5.2f" % s.allotment.allocated_time
        print "min/max LST (hrs): (%5.2f, %5.2f)" % (rad2hr(s.target.min_lst)
                                                   , rad2hr(s.target.max_lst)) 
        #print "LST range (bin): ", self.lst.getLstRange(s.target.min_lst, s.target.max_lst)
        if s.weather_type.type != 'Poor':
            print "Weather Type: ", s.weather_type.type
        if s.grade.grade != 'A':    
            print "Grade: ", s.grade.grade
        if s.session_type.type[:4] != 'Open':
            print "Session Type: ", s.session_type.type

        if len( s.get_lst_parameters()['LST Exclude'] ) > 0:
            print "LST Exclusion Range: ", s.get_lst_parameters()['LST Exclude']
        if s.flags.thermal_night or s.flags.optical_night or s.flags.rfi_night:
            print "Flags: thermal=%s, optical=%s, rfi=%s" % (s.flags.thermal_night, s.flags.optical_night, s.flags.rfi_night)
            
            
    def printLSTs(self):        
        "For reporting"
        label = "%7s" % "LST:"
        print label + " ".join(["%5d" % x for x in range(24)])

    def printPressures(self, ps, label = None):
        "For reporting"
        label = "     " if label is None else "%7s" % label
        print label + " ".join(["%5.2f" % x for x in ps])

    def createSession(self):
        "Create a new session for the tests"
        p = Proposal.objects.all()[0]
        return createSession(p)

    def test_getPressures(self):

        wtypes = ['Poor', 'Good', 'Excellent']
        grades = ['A', 'B', 'C']
        types = ["%s_%s" % (w, g) for w in wtypes for g in grades]
        # Make sure are session belongs to the next semester,
        # no matter when we are running this test.
        # This is a 12A session, that starts 2012-02-01.
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)

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

        # Make sure are session belongs to the next semester,
        # no matter when we are running this test.
        # This is a 12A session, that starts 2012-02-01.
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)

        # make sure are session belongs to a future semester, 
        # no matter when we are running this test
        #semName = lst.futureSemesters[0]
        #futureSem, _ = Semester.objects.get_or_create(semester = semName)
        #self.session.proposal.semester  = futureSem
        #self.session.proposal.save()

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

    def checkPressures(self, ps, expected):
        grades = ['A', 'B', 'C']
        wtypes = ['Poor', 'Good', 'Excellent']
        types = ["%s_%s" % (w, g) for w in wtypes for g in grades]

        # make sure it shows up in it's LST range
        for hr in range(6, 18):
            self.assertAlmostEqual(sum(expected), ps[hr]['Total'], 3)
            self.assertAlmostEqual(expected[0], ps[hr]['Poor_A'], 3)
            self.assertAlmostEqual(expected[1], ps[hr]['Good_A'], 3)
            self.assertAlmostEqual(expected[2], ps[hr]['Excellent_A'], 3)

        # make sure it doesn't show up out of it's range
        hrs = range(0, 6)
        hrs.extend(range(18, 24))
        for hr in hrs:
            self.assertEqual(float(hr), ps[hr]['LST'])
            self.assertEqual(0.0, ps[hr]['Total'])
            for t in types:
                self.assertEqual(0.0, ps[hr][t])

    def test_getPressuresFixed(self):
        """
        This test reflects use case 3.6.1.
        """

        # Make sure are session belongs to the next semester,
        # no matter when we are running this test.
        # This is a 12A session, that starts 2012-02-01.
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)


        # make this session a fixed session, and watch the hours 
        # get distributed across the weathers
        self.session.session_type = SessionType.objects.get(type = 'Fixed')
        self.session.allotment.allocated_time = 12
        self.session.allotment.save()
        self.session.target.min_lst = hr2rad(6)
        self.session.target.max_lst = hr2rad(18)
        self.session.target.save()
        self.session.save()

        # calc pressures
        ps = lst.getPressures()
        total = 1
        expected = (total * 0.50, total * 0.25, total * 0.25)
        self.checkPressures(ps, expected)
        
    def test_getPressuresWindowed(self):
        """
        This test reflects use case 3.6.2.
        """

        # Make sure are session belongs to the next semester,
        # no matter when we are running this test.
        # This is a 12A session, that starts 2012-02-01.
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)
        
        # make this session a fixed session, and watch the hours 
        # get distributed across the weathers
        self.session.session_type = SessionType.objects.get(type = 'Windowed')
        self.session.monitoring.window_size = 2
        self.session.monitoring.save()
        self.session.allotment.allocated_time = 12
        self.session.allotment.save()
        self.session.target.min_lst = hr2rad(6)
        self.session.target.max_lst = hr2rad(18)
        self.session.target.save()
        self.session.save()

        # calc pressures
        ps = lst.getPressures()

        total = 1
        expected = (total * 0.50, total * 0.25, total * 0.25)
        self.checkPressures(ps, expected)

        self.session.monitoring.window_size = 20
        self.session.monitoring.save()

        # calc pressures
        ps = lst.getPressures()
        expected = (total * 0.75, total * 0.125, total * 0.125)
        self.checkPressures(ps, expected)
        
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

        # Make sure are session belongs to the next semester,
        # no matter when we are running this test.
        # This is a 12A session, that starts 2012-02-01.
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)

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

    def test_calculatePressure(self):
        # Make sure we're in 12A
        today   = datetime(2012, 3, 1)
        lst = LstPressures(today = today)
        totaltime = 6.5
        #ps = lst.getPressuresForSessionOld(self.session)
        ps = lst.calculatePressure(self.session, totaltime)
        exp  = [0.54166]*12
        off = [0.0]*12
        exp.extend(off)
        for i in range(24):
            self.assertAlmostEqual(exp[i], ps[i], 3)
 
        # set night time flag
        self.session.flags.thermal_night = True
        #ps = lst.getPressuresForSessionOld(self.session)
        totaltime = 6.5
        ps = lst.calculatePressure(self.session, totaltime)
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

        today = datetime(2012, 1, 15)
        lst   = LstPressures(today = today)
        ws    = [1.0]*24

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
       
        exp = [1]*4
        exp.extend([0]*3)
        exp.extend([1]*14)
        exp.extend([0]*2)
        exp.extend([1])
        self.assertEqual(exp, ws3)

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

        # Testing use case 3.3.1
        start = datetime(2012, 8, 1)
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 1)
        exp = [1]
        exp.extend([0] * 14)
        exp.extend([1] * 9)
        self.assertEqual(exp, ex)

        start = datetime(2012, 8, 2)
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 1)
        self.assertEqual(exp, ex)

        start = datetime(2012, 8, 3)
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 1)
        exp[15] = 0
        self.assertEqual(exp, ex)

        start = datetime(2013, 1, 29)
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 1)
        exp = [0]
        exp.extend([1] * 14)
        exp.extend([0] * 9)
        self.assertEqual(exp, ex)

        start = datetime(2013, 1, 30)
        ws, ex = lst.computeOpticalNightWeights(start = start, numDays = 1)
        exp[1] = 0
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

    def test_getPressureWeights(self):
        today   = datetime(2012, 1, 1)
        lst     = LstPressures(today = today, initFlagWeights = False)
        cat     = 'RFI'
        weights, computed = lst.getPressureWeights(cat)
        self.assertTrue(computed)
        self.assertEqual(len(weights), 24)
        weights2, computed = lst.getPressureWeights(cat)
        self.assertTrue(not computed)
        for i in range(len(weights)):
            self.assertAlmostEqual(weights[i], weights2[i], 4)

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

        # Testing use case 3.3.3
        start = datetime(2012, 8, 1)
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1)
        exp = [1, 1, 1]
        exp.extend([0] * 12)
        exp.extend([1] * 9)
        self.assertEqual(exp, ex)

        start = datetime(2012, 8, 2)
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1)
        self.assertEqual(exp, ex)

        start = datetime(2012, 8, 3)
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1)
        self.assertEqual(exp, ex)

        start = datetime(2013, 1, 29)
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1)
        exp = [0, 0, 0, 0]
        exp.extend([1] * 12)
        exp.extend([0] * 8)
        self.assertEqual(exp, ex)

        start = datetime(2013, 1, 30)
        ws, ex = lst.computeRfiWeights(start = start, numDays = 1)
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
        self.assertAlmostEqual(sum(ps), 3.00, 1)


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
        self.assertAlmostEqual(sum(ps2), 12.00, 1)

        # combine the periods
        periods = [p, p2]
        ps3 = lst.getPressuresFromPeriods(periods)
        exp = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.65616762656011396, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.75337457147246312, 2.0, 2.0, 1.6315264423378473, 1.0]
        for i in range(len(exp)):
            self.assertAlmostEqual(exp[i], ps3[i], 3)

        # does this work for a 24 hour period?
        p3 = DSSPeriod(start = datetime(2012, 4, 5, 12)
                     , duration = 24.0
                      )
        ps3 = lst.getPressuresFromPeriod(p3)
        for i in range(len(ps3)):
            if i == 19:
                self.assertAlmostEqual(1.3766, ps3[i], 2)
            else:    
                self.assertEqual(1.0, ps3[i])

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

        # we need the availability to be that of 12A
        # 12A starts 2012, 2, 1
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)

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
        exp.poor = numpy.array([46.0]*lst.hrs)
        exp.good = numpy.array([28.5]*lst.hrs)
        exp.excellent = numpy.array([25.0]*lst.hrs)
        expC = Pressures() 
        expC.poor = numpy.array([13.5]*lst.hrs)
        expC.good = numpy.array([13.5]*lst.hrs)
        for w in ['poor', 'good', 'excellent']:
            for i in range(lst.hrs):
                self.assertEquals(exp.getType(w)[i]
                                , alloc.getType(w)[i])
                self.assertEquals(expC.getType(w)[i]
                                , chg.getType(w)[i])

    def test_adjustForOverfilledWeather_3(self):

        # we need the availability to be that of 12A
        # 12A starts 2012, 2, 1
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)

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
        exp.poor = numpy.array([46.0]*lst.hrs)
        exp.good = numpy.array([35.5]*lst.hrs)
        exp.excellent = numpy.array([38.0]*lst.hrs)
        expC = Pressures() 
        expC.poor = numpy.array([33.5]*lst.hrs)
        expC.good = numpy.array([20.5]*lst.hrs)
        expC.excellent = numpy.array([13.00]*lst.hrs)
        for w in ['poor', 'good', 'excellent']:
            for i in range(lst.hrs):
                self.assertEquals(exp.getType(w)[i]
                                , alloc.getType(w)[i])                                
                self.assertEquals(expC.getType(w)[i]
                                , chg.getType(w)[i])

    def test_adjustForOverfilledWeather_4(self):

        # we need the availability to be that of 12A
        # 12A starts 2012, 2, 1
        today = datetime(2012, 1, 15)
        lst = LstPressures(today = today)

        # WAY TOO MUCH TIME
        time = 100.0
        gradeA = Pressures()
        gradeA.poor = numpy.array([time]*lst.hrs)
        gradeA.good = numpy.array([time]*lst.hrs)
        gradeA.excellent = numpy.array([time]*lst.hrs)
        carryover = Pressures()
        carryover.poor = numpy.array([time]*lst.hrs)
        carryover.good = numpy.array([time]*lst.hrs)
        carryover.excellent = numpy.array([time]*lst.hrs)

        alloc, chg = lst.adjustForOverfilledWeather(gradeA
                                                  , carryover
                                                  , lst.weather.availability
                                                   )
        # here's the change we expect
        exp = Pressures() 
        exp.poor = numpy.array([0.0]*lst.hrs)
        exp.good = numpy.array([0.0]*lst.hrs)
        exp.excellent = numpy.array([300.0]*lst.hrs)
        expC = Pressures() 
        expC.poor = numpy.array([100.0]*lst.hrs)
        expC.good = numpy.array([-100.0]*lst.hrs)
        expC.excellent = numpy.array([200.0]*lst.hrs)
        for w in ['poor', 'good', 'excellent']:
            for i in range(lst.hrs):
                self.assertEquals(exp.getType(w)[i]
                                , alloc.getType(w)[i]) 
                self.assertEquals(expC.getType(w)[i]
                                , chg.getType(w)[i])

    def test_getSessionCategories(self):

        # our session is in 12A; for testing, do some time travel
        # today is long before that 
        dt = datetime(2009, 1, 1)
        lst = LstPressures(today = dt)
        cat, subcat = lst.getSessionCategories(self.session)
        self.assertEqual('ignored', cat)
        self.assertEqual('future', subcat)
        

        # today is one semester before that 
        dt = datetime(2012, 1, 1)
        lst = LstPressures(today = dt)
        cat, subcat = lst.getSessionCategories(self.session)
        self.assertEqual('allocated', cat)
        
        # today is in 12A - same semester! so now we're carryover
        # if we assign it a dss session
        s = DSSSesshun()
        self.session.dss_session = s
        dt = datetime(2012, 6, 1)
        lst = LstPressures(today = dt)
        cat, subcat = lst.getSessionCategories(self.session)
        self.assertEqual('carryover', cat)

        # today is in 12B - this session was in our past - it's still carryover
        dt = datetime(2012, 10, 1)
        lst = LstPressures(today = dt)
        cat, subcat = lst.getSessionCategories(self.session)
        self.assertEqual('carryover', cat)

    def test_getSessionTime(self):
        lst = LstPressures()
        self.assertEquals(0.0
                        , lst.getSessionTime(self.session, IGNORED, ''))
        self.assertEquals(21.0
                        , lst.getSessionTime(self.session, REQUESTED, ''))
        self.assertEquals(6.5
                        , lst.getSessionTime(self.session, ALLOCATED, ''))
        self.session.allotment.semester_time = 5.0                
        self.assertEquals(5.0
                        , lst.getSessionTime(self.session
                                           , ALLOCATED
                                           , SEMESTER))
        # carryover gets more complicated: first use the next_semester
        lst.carryOverUseNextSemester = True
        next_semester = SessionNextSemester(complete = False
                                          , time = 0.0
                                          , repeats = 0) 
        next_semester.save()
        self.session.next_semester = next_semester 
        self.session.save()
        self.assertEquals(0.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))
        self.session.next_semester.time = 5.0 
        self.assertEquals(5.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))
        self.session.next_semester.complete = True 
        self.assertEquals(0.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))
        # TBF: what about next_semester.repeats?                
        # now, get it from the time remaining in the DSS session:
        lst.carryOverUseNextSemester = False
        s = create_sesshun()
        self.session.dss_session = s
        self.assertEquals(3.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))
        # make it unscheduable two different ways
        self.session.dss_session.status.complete = True
        self.assertEquals(0.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))
        self.session.dss_session.status.complete = False
        self.session.dss_session.project.complete = True
        self.assertEquals(0.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))

        self.session.dss_session.project.complete = False
        self.session.dss_session.allotment.total_time = -1.0
        self.assertEquals(0.0
                        , lst.getSessionTime(self.session, CARRYOVER, ''))

    def createTestingSession(self, type, name, semester, time):
        p = Proposal.objects.all()[0]
        s = createSession(p)
        ot, created = Observing_Type.objects.get_or_create(type = type)
        s.observing_type = ot
        s.semester = Semester.objects.get(semester = semester) 
        s.name =  name 
        s.allotment.allocated_repeats = 1
        s.allotment.allocated_time = time
        s.allotment.save()
        s.save()
        return s

    def test_testingSessions(self):

        # currently we are in 12B
        s13A = DSSSemester.objects.get(semester = '13A')
        today = s13A.start() - timedelta(days = 7)
        lst = LstPressures(today = today)

        # create a testing session for 13A
        s = self.createTestingSession('commissioning'
                                    , 'new rx'
                                    , '13A'
                                    , 16.0
                                      )

        ps = lst.getPressures(sessions = [s])
        self.assertEqual(1, len(lst.testSessions))
        self.assertEqual(s, lst.testSessions[0])
        self.assertEqual(1, len(lst.pressuresBySession.items()))
        keys = lst.pressuresBySession.keys()
        cat, subcat, ps, time = lst.pressuresBySession[keys[0]]
        self.assertEqual('carryover', cat)
        self.assertEqual('', subcat)
        self.assertAlmostEqual(16.0, time, 3)
        exp = [0.]*10
        exp.extend([1.6]*10)
        exp.extend([0.]*4)
        self.assertEqual(exp, ps.tolist())

    def createCarryoverSession(self, name, sem, nextSemTime, remTime):
        # our carryover is from the previous semester
        sem = Semester.objects.get(semester = sem)
        s = self.createSession()
        s.name = name 
        s.semester = sem
        s.save()
        next_semester = SessionNextSemester(complete = False
                                          , time = nextSemTime)
        next_semester.save()              
        s.next_semester = next_semester
        dssSess = create_sesshun()
        dssSess.allotment.total_time  = remTime
        dssSess.allotment.save()
        s.dss_session = dssSess
        s.save()
        return s

    def test_carryover(self):

        # we're in the last days of 12B
        s13A = DSSSemester.objects.get(semester = '13A')
        today = s13A.start() - timedelta(days = 7)
        lst = LstPressures(today = today)

        nextSemTime = 75.0
        remainingTime = 110.0
        # our carryover is from the previous semester
        s = self.createCarryoverSession('carryover-1'
                                      , '12A'
                                      , nextSemTime
                                      , remainingTime
                                        )
   
        lst.getPressures(sessions = [s])
        self.assertEqual(1, len(lst.pressuresBySession.items()))
        keys = lst.pressuresBySession.keys()
        cat, subcat, ps, time = lst.pressuresBySession[keys[0]]
        self.assertEqual('carryover', cat)
        self.assertEqual('', subcat)
        self.assertAlmostEqual(nextSemTime, time, 3)
        exp = [0.]*10
        exp.extend([nextSemTime/10.]*10)
        exp.extend([0.]*4)
        self.assertEqual(exp, ps.tolist())

        # now use the time remaining
        lst.carryOverUseNextSemester = False
        lst.getPressures(sessions = [s])
        keys = lst.pressuresBySession.keys()
        cat, subcat, ps, time = lst.pressuresBySession[keys[0]]
        self.assertAlmostEqual(remainingTime, time, 3)

        # now set this as complete, and make sure we're ignored 
        s.dss_session.status.complete = True
        s.dss_session.status.save()
        lst.getPressures(sessions = [s])
        keys = lst.pressuresBySession.keys()
        cat, subcat, ps, time = lst.pressuresBySession[keys[0]]
        self.assertEqual('carryover', cat)
        self.assertEqual('', subcat)
        self.assertAlmostEqual(0.0, time, 3)

    def createMaintenanceSession(self):
        maintenance = 'Maintenance'

        # create a maint. proposal
        p = createProposal()
        p.pcode = maintenance 
        p.semester = Semester.objects.get(semester = '12A')
        p.save()

        # create a fixed type session
        s = createSession(p)
        s.session_type = SessionType.objects.get(type = 'Fixed')
        s.name =  maintenance
        s.save()

        # now creater a corresponding DSS project and session 
        dssSess = create_sesshun()
        s.dss_session = dssSess
        s.save()        
        return s

    def test_maintenancePressure(self):

        s = self.createMaintenanceSession()

        # the pressure for this session in 12B should be 
        # categorized as pre-assigned carrayover, but it should
        # have no pressure yet because there are no periods
        # We want to pretend it's right before 13A
        today = datetime(2013, 1, 15)
        lst = LstPressures(today = today)
        
        ps = lst.getPressures(sessions = [s])
        self.assertEqual(1, len(lst.pressuresBySession.items()))
        keys = lst.pressuresBySession.keys()
        cat, subcat, ps, time = lst.pressuresBySession[keys[0]]
        self.assertEqual('carryover', cat)
        self.assertEqual('periods', subcat)
        self.assertEqual(0.0, time)

        # create periods in the 'next semester'
        s13A = DSSSemester.objects.get(semester = '13A')
        periods = self.createMaintenanceDSSPeriods(s.dss_session, s13A)
        total = sum([p.duration for p in periods])

        ps = lst.getPressures(sessions = [s])
        self.assertEqual(1, len(lst.pressuresBySession.items()))
        keys = lst.pressuresBySession.keys()
        cat, subcat, ps, time = lst.pressuresBySession[keys[0]]
        self.assertTrue(abs(time - total) < 1.0)

        exp = [  0.
               , 0.
               , 0.
               , 0.03949657
               , 1.69908683
               , 3.85921174
               , 6.01933665
               , 8.17946156
               , 10.33958647
               , 12.55961392
               , 14.73989875
               , 16.88243036  
               , 17.40486829
               , 17.40486829
               , 17.40511433
               , 16.86434499
               , 14.70422008
               , 12.50609591
               , 10.3039078
               , 8.14378289
               , 5.98365798
               , 3.82353307
               , 1.66340816
               , 0.02165724
               ]

        self.assertArrayAlmostEqual(exp, ps)

    def assertArrayAlmostEqual(self, a1, a2):
        self.assertEqual(len(a1), len(a2))
        for i in range(len(a1)):
            self.assertAlmostEqual(a1[i], a2[i], 3)

    def createMaintenanceDSSPeriods(self, s, sem):

        # give a fixed maint. day for each week in the semester
        dt = sem.start() + timedelta(days = 1)
        numDays = sem.numDays()
        weeks = int(numDays/7)
        dur = 8.0 # hours
        ps = []
        for w in range(weeks):
            dt = dt + timedelta(days = 7)

            if dt < sem.end():
                p = DSSPeriod(session = s
                            , start = dt
                            , duration = dur
                             )
                p.save()             
                ps.append(p)
        return ps    

    def test_accumulatePressure(self):

        lst = LstPressures()
        error, msgs = lst.checkPressures()
        self.assertEquals(True, error)

        # accum something
        ps = lst.newHrs()
        ps[0] = 1.0
        ps[1] = 1.0
        lst.accumulatePressure(self.session, CARRYOVER, ps)
        error, msgs = lst.checkPressures()
        self.assertEquals(True, error)
        self.assertEquals(ps.tolist(), lst.totalPs.tolist())
        self.assertEquals(ps.tolist(), lst.carryoverTotalPs.tolist())
        self.assertEquals(ps.tolist(), lst.carryoverPs.poor.tolist())

        # accum something else in carryover
        ps[12] = 1.0
        ps[13] = 1.0
        lst.accumulatePressure(self.session, CARRYOVER, ps)
        error, msgs = lst.checkPressures()
        self.assertEquals(True, error)
        exp = lst.newHrs()
        exp[0] = 2.0
        exp[1] = 2.0
        exp[12] = 1.0
        exp[13] = 1.0
        self.assertEquals(exp.tolist(), lst.totalPs.tolist())
        self.assertEquals(exp.tolist(), lst.carryoverTotalPs.tolist())
        self.assertEquals(exp.tolist(), lst.carryoverPs.poor.tolist())

        # now add allocated
        ps = lst.newHrs()
        ps[5] = 1.0
        ps[6] = 1.0
        lst.accumulatePressure(self.session, ALLOCATED, ps)
        error, msgs = lst.checkPressures()
        self.assertEquals(True, error)
        # carryover shouldn't change
        self.assertEquals(exp.tolist(), lst.carryoverTotalPs.tolist())
        self.assertEquals(exp.tolist(), lst.carryoverPs.poor.tolist())
        # and allocated is simple
        self.assertEquals(ps.tolist()
                        , lst.newAstronomyGradeTotalPs.tolist())
        for grade in ['A', 'B', 'C']:
            for w in ['poor', 'good', 'excellent']:
                if grade != 'A' and w != 'poor':
                    self.assertEquals(lst.newHrs().tolist()
                                    , lst.gradePs[grade].getType(w).tolist())
        self.assertEquals(ps.tolist()
                          , lst.gradePs['A'].poor.tolist())
        # but the total has changed                
        exp2 = lst.newHrs()
        exp2[0] = 2.0
        exp2[1] = 2.0
        exp2[5] = 1.0
        exp2[6] = 1.0
        exp2[12] = 1.0
        exp2[13] = 1.0
        self.assertEquals(exp2.tolist(), lst.totalPs.tolist())
        
    def test_proposalLifeCycles(self):
        "Tests to match the use case 'Proposal Life Cycles & Cats.'"

        gradeA = SessionGrade.objects.get(grade = 'A')
        gradeD = SessionGrade.objects.get(grade = 'D')
        dss12A = DSSSemester.objects.get(semester = '12A')
        dss12B = DSSSemester.objects.get(semester = '12B')
        dss13A = DSSSemester.objects.get(semester = '13A')
        s12A   = Semester.objects.get(semester = '12A')
        s12B   = Semester.objects.get(semester = '12B')
        s13A, _ = Semester.objects.get_or_create(semester = '13A')
        s13A.save()
        s13B   = Semester(semester = '13B')
        s13B.save()

        # The first time we used the PHT and tried to calculate pressures was during 12A; our new proposals were for 12B. At first, all we had were these fresh 12B proposals, none of which had been assigned a grade or allocated time, and they all were for the 12B semester. Therefore, all our sessions fell into the same category: requested.
        today = dss12A.end() - timedelta(days = 60)
        lst = LstPressures(today = today
                         , carryOverUseNextSemester = False)

        # create 12B sessions
        # TBF: give these meaningfull names, like in 13A below
        times = [50.0, 45.0, 5.0, 40.0, 10.0]
        for i in range(len(times)):
            s = self.createSession()
            s.name = "test-%d" % i 
            s.semester = s12B
            s.save()
            s.allotment.requested_time = times[i]
            s.allotment.allocated_time = 0.0
            s.allotment.allocated_repeats = 1 
            s.grade = None
            s.allotment.repeats = 1.0
            s.allotment.save()
            s.save()

        # Then we had to start figuring out the carryover, so we pulled over from the DSS only those projects and sessions that were not complete and made corresponding legacy PHT proposals & sessions. These all fell into the carryover category, and we used time remaining for computing their pressure. 
        # Create one session to represent all this carryover
        s = self.createSession()
        s.name = "carryover-1"
        s.semester = s12A
        s.save()
        next_semester = SessionNextSemester(complete = False
                                          , time = 75.0)
        next_semester.save()              
        s.next_semester = next_semester
        dssSess = create_sesshun()
        dssSess.allotment.total_time  = 110
        dssSess.allotment.save()
        s.dss_session = dssSess
        s.save()

        # Here's a table showing their total time:
        # Category 	Hours 	Composition
        # requested 	150.0 	the new proposals for 12B
        # carryover 	110.0 	legacy projects from 12A and earlier 
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(110.0, lst.carryoverTotalPs.sum())
        self.assertEqual(150.0, lst.requestedTotalPs.sum())
        
        # Then we started editing these 12B proposals: some get assigned a passing grade and time, other's get a failing grade and no time, and a few exceptional sessions get assigned a semester past 12B. 

        # get's a failing grade
        s = Session.objects.get(name = 'test-0')
        s.grade = gradeD
        s.save()

        # get's a passing grade & time!
        s = Session.objects.get(name = 'test-3')
        s.grade = gradeA
        s.allotment.allocated_time = s.allotment.requested_time 
        s.allotment.save()
        s.save()

        # get's passing grade & time, but for future semester
        s = Session.objects.get(name = 'test-4')
        s.grade = gradeA
        s.allotment.allocated_time = s.allotment.requested_time 
        s.allotment.save()
        s.semester = s13B
        s.save()

        # That changes our table:   
        # Category 	Hours 	Composition
        # requested 	100.0 	the new proposals for 12B
        # allocated 	40.0 	the new proposal for 12B that will become DSS projects
        # ignored 	10.0 	right now, all that's contributing to this are the 'future' sessions
        # carryover 	110.0 	legacy projects from 12A and earlier 
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(110.0, lst.carryoverTotalPs.sum())
        self.assertEqual(100.0, lst.requestedTotalPs.sum())
        self.assertEqual(40.0, lst.newAstronomyTotalPs.sum())
        self.assertEqual(10.0, lst.getIgnoredRequestedTime())
        
        # now use time remaining
        lst = LstPressures(today = today
                         , carryOverUseNextSemester = True)
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(75.0, lst.carryoverTotalPs.sum())
        self.assertEqual(100.0, lst.requestedTotalPs.sum())
        self.assertEqual(40.0, lst.newAstronomyTotalPs.sum())
        self.assertEqual(10.0, lst.getIgnoredRequestedTime())
                         
        # TAC meeting is held: one more future semester (5 hrs), allocated goes up by 45, requested goes doesn by 50.`
        s = Session.objects.get(allotment__requested_time = 5.0)
        s.grade = gradeA
        s.semester = s13B
        s.save()
        s.allotment.allocated_time = s.allotment.requested_time
        s.allotment.save()

        s = Session.objects.get(allotment__requested_time = 45.0)
        s.grade = gradeA
        s.save()
        s.allotment.allocated_time = s.allotment.requested_time
        s.allotment.save()

        # Category 	Hours 	Composition
        # requested 	50.0 	the new proposals for 12B that won't become DSS projects
        # allocated 	85.0 	the new proposal for 12B that will become DSS projects
        # ignored 	15.0 	right now, all that's contributing to this are the 'future' sessions
        # carryover 	110.0 	legacy projects from 12A and earlier 
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(75.0, lst.carryoverTotalPs.sum())
        self.assertEqual(50.0, lst.requestedTotalPs.sum())
        self.assertEqual(85.0, lst.newAstronomyTotalPs.sum())
        self.assertEqual(15.0, lst.getIgnoredRequestedTime())
                         

        # Finally, 12B is about to start, so all the allocated sessions need to have equivalent sessions in the DSS. These are created, and it has no affect on our table above at all.
        for i in [1, 3]:
            s = Session.objects.get(name = "test-%d" % i)
            next_semester = SessionNextSemester(complete = False
                                              , time = times[i])
            next_semester.save()              
            s.next_semester = next_semester
            dssSess = create_sesshun()
            dssSess.allotment.total_time = times[i]
            dssSess.allotment.save()
            s.dss_session = dssSess
            s.save()
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(75.0, lst.carryoverTotalPs.sum())
        self.assertEqual(50.0, lst.requestedTotalPs.sum())
        self.assertEqual(85.0, lst.newAstronomyTotalPs.sum())
        self.assertEqual(15.0, lst.getIgnoredRequestedTime())
                         

        # Finally, 12B is about to start, so all the allocated sessions need to have equivalent sessions in the DSS. These are created, and it has no affect on our table above at all.

        # The Second Semester!

        # The first day of 12B arrives, but we have not yet imported any new proposals for 13A into the PHT. Our allocated category now moves into carryover, and the proposals in requested get moved to ignored, because the term 'current semester' has moved from 12B to 13A (see Note 1).

        today = dss12B.start() + timedelta(days = 3)
        # go back to using time remaining, since the new
        # carryover doesn't have next semester yet
        lst = LstPressures(today = today
                         , carryOverUseNextSemester = False)
        ps = lst.getPressures(sessions = sessions)                 
        # Category 	Hours 	Composition
        # ignored 	65.0 	Sessions for 12B with failing grade, and 'future' sessions (see Note 2)
        # carryover 	195.0 	legacy projects from 12B and earlier
        self.assertEqual(195.0, lst.carryoverTotalPs.sum())
        self.assertEqual(65.0, lst.getIgnoredRequestedTime())
        #remaining = 0.0
        #next = 0.0
        #for sname, data in lst.pressuresBySession.items():
        #    print sname, data[0], data[3]
        #    if data[0] == CARRYOVER:
        #        name = sname.split(' ')[0]
        #        print sname, " is CARRYOVER!"
        #        s = Session.objects.get(name = name)
        #        print s.dss_session.allotment.total_time
        #        remaining += s.dss_session.allotment.total_time
        #        print s.next_semester.time
        #        next += s.next_semester.time
        #        print s.next_semester.complete
        #print "remaining: ", remaining
        #print "next: ", next

        # Now we import new proposals for 13A (on the second day of 12B). This essentially adds a new row to our table:
        
        newSess2 = [('2bReq1', 30.0)
                  , ('2bAlloc1', 45.0)
                  , ('2bAlloc2', 20.0)
                  , ('2bFuture1', 5.0)
                   ]
        for name, time in newSess2:
            s = self.createSession()
            s.name = name 
            s.semester = s13A
            s.save()
            s.allotment.requested_time = time
            s.allotment.allocated_time = 0.0
            s.allotment.allocated_repeats = 1 
            s.grade = None
            s.allotment.repeats = 1.0
            s.allotment.save()
            s.save()

        # Category 	Hours 	Composition
        # requested 	100.0 	the new proposals for 13A
        # ignored 	65.0 	Sessions for 12B with failing grade, and 'future' sessions (see Note 2)
        # carryover 	195.0 	legacy projects from 12B and earlier
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(195.0, lst.carryoverTotalPs.sum())
        self.assertEqual(100.0, lst.requestedTotalPs.sum())
        self.assertEqual(65.0, lst.getIgnoredRequestedTime())
        
        # Then we start editing these 13A proposals: some get assigned a passing grade and time, other's get a failing grade and no time, and a few exceptional sessions get assigned a semester past 13A. 
        s = Session.objects.get(name = '2bAlloc1')
        s.allotment.allocated_time = s.allotment.requested_time
        s.allotment.save()
        s.grade = gradeA
        s.save()
       
        s = Session.objects.get(name = '2bFuture1')
        s.allotment.allocated_time = s.allotment.requested_time
        s.allotment.save()
        s.grade = gradeA
        s.semester = s13B
        s.save()
        
        s = Session.objects.get(name = '2bReq1')
        s.grade = gradeD
        s.save()

        # That changes our table:
        # Category 	Hours 	Composition
        # requested 	50.0 	the new proposals for 13A
        # allocated 	45.0 	the new 13A proposals that will get scheduled.
        # ignored 	70.0 	Sessions for 12B with failing grade, and 'future' sessions (see Note 2)
        # carryover 	195.0 	legacy projects from 12B and earlier
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(195.0, lst.carryoverTotalPs.sum())
        self.assertEqual(50.0, lst.requestedTotalPs.sum())
        self.assertEqual(70.0, lst.getIgnoredRequestedTime())
        self.assertEqual(45.0, lst.newAstronomyTotalPs.sum())
        
        # If we go back to using next semester, we should see the carryover go down:
        lst.carryOverUseNextSemester = True # change how carryover calc!
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(160.0, lst.carryoverTotalPs.sum())
        self.assertEqual(50.0, lst.requestedTotalPs.sum())
        self.assertEqual(70.0, lst.getIgnoredRequestedTime())
        self.assertEqual(45.0, lst.newAstronomyTotalPs.sum())

        
        # So, a DSS lookahead simulation is run, and this is used to enter in next semester values for some carryover sessions 
        s = Session.objects.get(name = 'test-1')
        s.next_semester.time = 35.0 # observed 10 hrs
        s.next_semester.save()
        
        # This changes the number in our table:
        # Category 	Hours 	Composition
        # requested 	50.0 	the new proposals for 13A
        # allocated 	45.0 	the new 13A proposals that will get scheduled.
        # ignored 	70.0 	Sessions for 12B with failing grade, and 'future' sessions
        # carryover 	150.0 	legacy projects from 12B and earlier
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        lst.carryOverUseNextSemester = True # change how carryover calc!
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(150.0, lst.carryoverTotalPs.sum())
        self.assertEqual(50.0, lst.requestedTotalPs.sum())
        self.assertEqual(70.0, lst.getIgnoredRequestedTime())
        self.assertEqual(45.0, lst.newAstronomyTotalPs.sum())
        
        # The editing process continues, and the TAC meeting is held. The final decisions for these new proposals are finally made.
        s = Session.objects.get(name = '2bAlloc2')
        s.allotment.allocated_time = s.allotment.requested_time
        s.allotment.save()
        s.grade = gradeA
        s.save()

        # Here's what our numbers look like now:
        # Category 	Hours 	Composition
        # requested 	30.0 	the new proposals for 13A
        # allocated 	65.0 	the new 13A proposals that will get scheduled.
        # ignored 	70.0 	Sessions for 12B with failing grade, and 'future' sessions
        # carryover 	150.0 	legacy projects from 12B and earlier                         
        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)
        self.assertEqual(150.0, lst.carryoverTotalPs.sum())
        self.assertEqual(30.0, lst.requestedTotalPs.sum())
        self.assertEqual(70.0, lst.getIgnoredRequestedTime())
        self.assertEqual(65.0, lst.newAstronomyTotalPs.sum())
                        

        # Now add a few more sessions to flesh this whole example 
        # out a bit more.  This matches Use Case 3.7.3
        # First, an old carryover that is complete:
        s = self.createCarryoverSession('carryover-2'
                                      , '12A'
                                      , 0.
                                      , 0.
                                       )
        s.dss_session.status.complete = True
        s.dss_session.status.save()
        s.next_semester.time = 0
        s.next_semester.save()
        # Second, a testing session
        s = self.createTestingSession('commissioning'
                                    , 'new rx'
                                    , '13A'
                                    , 16.0
                                      )
        # and make sure we know about it
        lst.testSessions = lst.getTestSessions()
        # Finally, the maintenance
        s = self.createMaintenanceSession()
        self.createMaintenanceDSSPeriods(s.dss_session, dss13A)


        sessions = Session.objects.all().exclude(name = 'He_ELD_5G').order_by('name')
        ps = lst.getPressures(sessions = sessions)


        self.assertAlmostEqual(150.0 + 200.54 + 16.0 
                             , lst.carryoverTotalPs.sum(), 1)
        self.assertEqual(30.0, lst.requestedTotalPs.sum())
        self.assertEqual(70.0, lst.getIgnoredRequestedTime())
        self.assertEqual(65.0, lst.newAstronomyTotalPs.sum())        
    
        # what are the final sessions used?
        #pbs = lst.pressuresBySession                
        #for key, value in pbs.items():
        #    print key, value[0], value[1], value[3]
        #ss = Session.objects.all().order_by('name')
        #print "xxx"
        #for s in ss:
        #    print s.name, s.grade.grade, s.semester.semester, s.allotment.allocated_time

        # print a plot of this
        #plot = PlotLstPressures()
        #plot.plot('total'
        #        , carryOverUseNextSemester = True
        #        , adjustWeatherBins = False)                
        #0plot.printPlot('total.png')        
