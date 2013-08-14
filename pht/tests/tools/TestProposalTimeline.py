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

from pht       import models as pht
from scheduler import models as scheduler
#from scheduler.tests.utils    import create_sesshun
from pht.tools.ProposalTimeline import ProposalTimeline

class TestProposalTimeline(TestCase):

    fixtures = ['proposal_GBT12A-002.json']
     
    def test_extendTimeline(self):

        pt = ProposalTimeline()

        tl = [(datetime(2013, 1, 1), 10.)
            , (datetime(2013, 1, 5), 15.)
            , (datetime(2013, 1, 6), 17.)
            , (datetime(2013, 1, 8), 18.)
            , (datetime(2013, 1, 11), 19.)
            , (datetime(2013, 1, 15), 21.)
             ]
        etl = pt.extendTimeline(tl, upTo = datetime(2013, 1, 20))     
        self.assertEqual(19, len(etl))
        start = datetime(2013, 1, 1)
        for i, e in enumerate(etl):
            dt, t = e
            self.assertEqual(start + timedelta(days = i), dt)

        etl = pt.extendTimeline(tl
                              , beginAt = datetime(2012, 12, 28)     
                              , upTo = datetime(2013, 1, 20))     
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

