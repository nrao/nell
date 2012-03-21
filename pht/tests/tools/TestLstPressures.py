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

from pht.utilities import *
from pht.tools.LstPressures import LstPressures
from pht.models         import Proposal
from pht.models         import SessionGrade
#from pht.models         import ImportReport

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

    def test_getPressuresForSession(self):

        lst = LstPressures()
        ps = lst.getPressuresForSession(self.session)
        exp  = [0.54166]*12
        off = [0.0]*12
        exp.extend(off)
        for i in range(24):
            self.assertAlmostEqual(exp[i], ps[i], 3)
 
    def test_getLstWeightsForSession(self):
        lst = LstPressures()
        ws = lst.getLstWeightsForSession(self.session)
        exp = [1.0]*12
        off = [0.0]*12
        exp.extend(off)
        self.assertEqual(exp, ws)

    def test_modifyWeightsForLstExclusion(self):

        lst = LstPressures()
        ws = [1.0]*24

        # this session doesn't have lst exclusion
        ws2 = lst.modifyWeightsForLstExclusion(self.session, ws)

        # so the weights don't get modified
        self.assertEqual(ws, ws2)

    def test_getFlagWeightsForSession(self):

        lst = LstPressures()
        exp = [1.0]*24

        # this session doesn't have any flags set
        fs = lst.getFlagWeightsForSession(self.session)

        # so the weights are all 1.0 
        self.assertEqual(exp, fs)

