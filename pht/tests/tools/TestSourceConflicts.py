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

from pht.models import *
from pht.utilities import *
from pht.tools.SourceConflicts import SourceConflicts

class TestSourceConflicts(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']


    def setUp(self):

        # get the one proposal and it's one session
        proposal = Proposal.objects.all()[0]
        self.proposal = proposal
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

    def createSrc(self, proposal, ra = 0.0, dec = 0.0):
        src = Source(proposal = proposal
                  , ra = ra
                  , dec = dec
                     )
        src.save()
        return src

    def test_calcAnglularDistance(self):

        src1 = Source(ra = 0.0
                    , dec = 0.0)
        src2 = Source(ra = 0.0
                    , dec = 0.0)

        sc = SourceConflicts()
        d = sc.calcAngularDistance(src1, src2)
        self.assertAlmostEqual(0.0, d, 3)
   
        # from Carl's report For GBT12B-364:
        # source NGC 1266
        src1.ra = 0.85526951111895499
        src1.dec = -0.042364958710075701
        # source NGC1266, GBT10A-014
        src2.ra = 0.85526223891373798 #sexHrs2rad('03:16:00.0')
        src2.dec = -0.0423630194553513 #sexDeg2rad('-02:25:37.0')
        d = sc.calcAngularDistance(src1, src2)
        self.assertAlmostEqual(0.0258519896867, rad2arcMin(d), 5)
        #print "deltaRa: ", rad2arcMin(abs(src2.ra - src1.ra))
        #print "deltaDec: ", rad2arcMin(abs(src2.dec - src1.dec))

        # source NGC 3665
        src1.ra = 2.9876837023847602
        src1.dec = 0.67653858425479396
        # source SDSS J112346 ...; GBT08A-033
        src2.ra = 2.9835247282213602 #sexHrs2rad('11:23:46')
        src2.dec = 0.67338971939598802 #sexDeg2rad('38:34:56')
        d = sc.calcAngularDistance(src1, src2)
        self.assertAlmostEqual(15.549314042, rad2arcMin(d), 5)
        #print "deltaRa: ", rad2arcMin(abs(src2.ra - src1.ra))
        #print "deltaDec: ", rad2arcMin(abs(src2.dec - src1.dec))


    def test_getAnglularDistance(self):
        src1 = self.createSrc(self.proposal)
        src2 = self.createSrc(self.proposal)

        sc = SourceConflicts()

        self.assertEqual(0, len(sc.distances))

        # calculate it and stick it in the cache!
        d = sc.getAngularDistance(src1, src2)
        self.assertAlmostEqual(0.0, d, 3)

        self.assertEqual(1, len(sc.distances))
        key = (src1.id, src2.id)
        self.assertAlmostEqual(0.0, sc.distances[key], 3)
      
        # make sure we use the cache when switching sources around
        d = sc.getAngularDistance(src2, src1)
        self.assertAlmostEqual(0.0, d, 3)

        self.assertEqual(1, len(sc.distances))
        key = (src1.id, src2.id)
        self.assertAlmostEqual(0.0, sc.distances[key], 3)
      

    def test_getLowestRcvr(self):
        sc = SourceConflicts()
        lr = sc.getLowestRcvr(self.proposal)
        r  = self.session.receivers.all()[0]
        self.assertEqual(r, lr)

    def test_calcSearchRadiusForRcvr(self):
        sc = SourceConflicts()
        r  = Receiver.objects.get(name = 'Rcvr4_6') 
        rad = sc.calcSearchRadiusForRcvr('C')
        self.assertAlmostEquals(0.0014544, rad, 7)

        
      
