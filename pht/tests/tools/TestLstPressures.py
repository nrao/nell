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


    #def setUp(self):
        #self.lst = LstPressures()

    def test_getPressures(self):

        wtypes = ['Poor', 'Good', 'Excellent']
        grades = ['A', 'B', 'C']
        types = ["%s_%s" % (w, g) for w in wtypes for g in grades]
        # make sure we start off blank
        lst = LstPressures()
        ps = lst.getPressures()
        for i, p in enumerate(ps):
            self.assertEqual(float(i), p['ra'])
            self.assertEqual(0.0, p['total'])
            for t in types:
                self.assertEqual(0.0, p[t])

        # get the one proposal and it's one session
        proposal = Proposal.objects.all()[0]
        s = proposal.session_set.all()[0]

        # give it some values so it will show up in plot
        s.grade = SessionGrade.objects.get(grade = 'A')
        s.target.ra = hr2rad(12.5)
        s.target.dec = 0.0
        s.target.save()
        time = 6.5 # hrs
        s.allotment.allocated_time = time # hrs
        s.allotment.save()
        s.save()

        ps = lst.getPressures()

        # make sure this shows up as one non-zero entry 
        for i, p in enumerate(ps):
            if i != 12:
                self.assertEqual(float(i), p['ra'])
                self.assertEqual(0.0, p['total'])
                for t in types:
                    self.assertEqual(0.0, p[t])
            else:
                self.assertEqual(time, p['total'])
                for t in types:
                    if t != 'Poor_A':
                        self.assertEqual(0.0, p[t])
                    else:    
                        print p
                        self.assertEqual(time, p[t])
                
