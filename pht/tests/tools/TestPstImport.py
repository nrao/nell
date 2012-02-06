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

import unittest

from pht.tools.database import PstImport
from pht.models         import Proposal

class TestPstImport(unittest.TestCase):

    def setUp(self):
        self.pst = PstImport()

    def test_importProposal(self):
        proposal = self.pst.importProposal('GBT/12A-002')
        self.assertTrue(proposal is not None)
        self.assertTrue(len(proposal.sci_categories.all()) > 0)
        self.assertTrue(len(proposal.session_set.all()) > 0)
        s = proposal.session_set.all()[0]
        self.assertEquals("He_ELD_5G", s.name)
        self.assertTrue(len(proposal.source_set.all()) > 0)
        src = proposal.source_set.all()[0]
        self.assertAlmostEquals(4.79908, src.ra, 2)
        self.assertTrue(len(s.sources.all()) == 0)
        self.assertTrue(len(s.receivers.all()) > 0)
        self.assertTrue(len(s.receivers_granted.all()) > 0)
        self.assertEquals(s.receivers.all()[0].name
                        , s.receivers_granted.all()[0].name)
        self.assertTrue(len(s.backends.all()) > 0)
        self.assertTrue(s.allotment is not None)
        self.assertTrue(s.target is not None)
        proposal.delete()

    def test_importProposals(self):
        self.pst.importProposals('12A')
        self.assertTrue(len(Proposal.objects.all()) > 0)
        for p in Proposal.objects.all():
            self.assertTrue(len(p.session_set.all()) > 0)
            p.delete()

    def test_importProposals_12B(self):
        self.pst.importProposals('12B')
        self.assertTrue(len(Proposal.objects.all()) > 0)
        for p in Proposal.objects.all():
            self.assertTrue(len(p.session_set.all()) > 0)
            p.delete()
