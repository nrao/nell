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

from datetime import datetime, timedelta
import copy

from pht       import models as pht
from scheduler import models as scheduler
#from scheduler.tests.utils    import create_sesshun
from pht.tools.ProposalTimeline import ProposalTimeline

class TestProposalTimeline(TestCase):

    fixtures = ['proposal_GBT12A-002.json']
     
    def setUp(self):

        tl = [(datetime(2013, 1, 1), 10.)
            , (datetime(2013, 1, 5), 15.)
            , (datetime(2013, 1, 6), 17.)
            , (datetime(2013, 1, 8), 18.)
            , (datetime(2013, 1, 11), 19.)
            , (datetime(2013, 1, 15), 21.)
             ]
        self.tl = tl

    def test_sliceTimeline(self):

        today = datetime(2013, 1, 30)   
        pt = ProposalTimeline(now = today)

        # 1: no times, no time range
        etl = pt.sliceTimeline([])
        self.assertEqual([(today - timedelta(days = 7), 0.)
                        , (today, 0.)], etl)

        # 2: no times, a time range
        begin = datetime(2013, 2, 1)
        end = datetime(2013, 2, 5)
        etl = pt.sliceTimeline([], (begin, end))
        self.assertEqual([(begin, 0.), (end, 0.)], etl)

        # 3: times, time range w/ no overlap
        etl = pt.sliceTimeline(self.tl, (begin, end))
        self.assertEqual([(begin, 21.), (end, 21.)], etl)

        # 4: times, a time range w/ no overlap
        begin = datetime(2012, 2, 1)
        end = datetime(2012, 2, 5)
        etl = pt.sliceTimeline(self.tl, (begin, end))
        self.assertEqual([(begin, 0.), (end, 0.)], etl)

        # 5: times, NO time range
        etl = pt.sliceTimeline(self.tl)
        exp = copy.copy(self.tl)
        exp.append((today, 21.))
        self.assertEqual(exp, etl)
 
        # 6: times, overlap
        begin = datetime(2012, 12, 30)
        end = datetime(2013, 1, 3)
        etl = pt.sliceTimeline(self.tl, (begin, end))
        exp = [(begin, 0.)
             , self.tl[0]
             , (end, 10.)]
        self.assertEqual(exp, etl)     
        
        # 7: times, overlap
        begin = datetime(2013, 1, 12)
        end = datetime(2013, 1, 25)
        etl = pt.sliceTimeline(self.tl, (begin, end))
        exp = [(begin, 19.)
             , self.tl[-1]
             , (end, 21.)]
        self.assertEqual(exp, etl)     
 
        # 8: special case
        begin = datetime(2013, 1, 11)
        end = datetime(2013, 1, 25)
        etl = pt.sliceTimeline(self.tl, (begin, end))
        exp = [self.tl[-2]
             , self.tl[-1]
             , (end, 21.)]
        self.assertEqual(exp, etl)     

        # 9: special case
        begin = datetime(2013, 1, 11)
        end = datetime(2013, 1, 15)
        etl = pt.sliceTimeline(self.tl, (begin, end))
        exp = [self.tl[-2]
             , self.tl[-1]]
        self.assertEqual(exp, etl)     

        # 10: special case
        etl = pt.sliceTimeline([self.tl[1]]) 
        exp = [self.tl[1], (today, 15.)]
        self.assertEqual(exp, etl)     

        # 11: timerange inside periods
        begin = datetime(2013, 1, 9)
        end = datetime(2013, 1, 10)
        etl = pt.sliceTimeline(self.tl, (begin, end))
        exp = [(begin, 18.), (end, 18.)]
        self.assertEqual(exp, etl)     

    def test_extendTimeline(self):

        pt = ProposalTimeline()

        upTo = datetime(2013, 1, 20)     
        etl = pt.extendTimeline(self.tl, upTo = upTo) 
        self.assertEqual(19, len(etl))
        start = datetime(2013, 1, 1)
        for i, e in enumerate(etl):
            dt, t = e
            self.assertEqual(start + timedelta(days = i), dt)

        beginAt = datetime(2012, 12, 28)     
        etl = pt.extendTimeline(self.tl, beginAt = beginAt, upTo = upTo)
        self.assertEqual(23, len(etl))
        start = datetime(2012, 12, 28)
        for i, e in enumerate(etl):
            dt, t = e
            self.assertEqual(start + timedelta(days = i), dt)
        
    def test_getTimeline(self):

        p = pht.Proposal.objects.all().order_by('pcode')[0]
        pt = ProposalTimeline(proposal = p.pcode)
        # no-op test, since this proposal has no dss project
        tl = pt.getTimeline()

