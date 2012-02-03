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

import simplejson as json
from django.test        import TestCase
from pht.models         import *

class TestSession(TestCase):
    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json']

    def setUp(self):
        # load the single proposal from the fixture
        self.proposal = Proposal.objects.get(pcode = "GBT12A-002")
        self.session = self.proposal.session_set.all().order_by('id')[0]

    def test_lsts(self):
        
        ex = {'LST Include': [], 'LST Exclude': []}
        self.assertEqual(ex, self.session.get_lst_parameters())

        # now create an LST Exclusion range
        pName = "Exclude"
        lowParam = Parameter.objects.get(name="LST %s Low" % pName)
        hiParam  = Parameter.objects.get(name="LST %s Hi" % pName)

        spLow = SessionParameter(session = self.session
                               , parameter = lowParam
                               , float_value = 2.0
                                )
        spLow.save()                       
        spHi  = SessionParameter(session = self.session
                               , parameter = hiParam
                               , float_value = 4.0
                                 )
        spHi.save()                       

        # and make sure it shows up correctly
        ex = {'LST Include': [], 'LST Exclude': [(2.0, 4.0)]}
        self.assertEqual(ex, self.session.get_lst_parameters())

        include, exclude = self.session.get_lst_string()
        self.assertEqual('', include)
        self.assertEqual('2.00-4.00', exclude)

