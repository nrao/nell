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

from django.test        import TestCase
from pht.tools.database import PstInterface
from pht.models         import Author

class TestPstInterface(TestCase):
    fixtures = ['proposal_GBT12A-002.json']

    def setUp(self):
        self.pst = PstInterface()

    def test_getUsers(self):
        pst   = PstInterface()
        users = pst.getUsers()
        self.assertTrue(len(users) > 0)

    def test_getAuthor(self):
        author = Author.objects.all()[0]
        pst    = PstInterface()
        results = pst.getAuthor(author.pst_author_id)
        expected = {'FIRST_NAME': 'Raju', 'LAST_NAME': 'Baddi'}
        self.assertEqual(expected['FIRST_NAME'], results['FIRST_NAME'])
        self.assertEqual(expected['LAST_NAME'], results['LAST_NAME'])

    def test_getProposalTechnicalReviews(self):
        pst = PstInterface()
        reviews = pst.getProposalTechnicalReviews('GBT12B-018')
        for forAuthors, forTac, _, _ in reviews:
            self.assertTrue(forAuthors is not None)
            self.assertTrue(forTac is not None)

        reviews = pst.getProposalTechnicalReviews('foo')
        self.assertEqual(len(reviews), 0)
