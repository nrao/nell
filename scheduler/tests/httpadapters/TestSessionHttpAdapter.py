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

from test_utils import NellTestCase
from scheduler.models import *
from scheduler.httpadapters import SessionHttpAdapter
from scheduler.tests.utils  import create_sesshun

class TestSessionHttpAdapter(NellTestCase):

    def setUp(self):
        super(TestSessionHttpAdapter, self).setUp()
        self.s       = create_sesshun()
        self.adapter = SessionHttpAdapter(self.s)

    def test_update_lst_parameters(self):
        error = False
        try:
            self.adapter.update_lst_parameters('lst_ex', '14.0-10')
        except NameError:
            error = True
        self.assertTrue(error)

        try:
            self.adapter.update_lst_parameters('lst_ex', '2.0 - 8.0, 4.0 - 10.0')
        except NameError:
            error = True
        self.assertTrue(error)

        self.adapter.update_lst_parameters('lst_ex', '4.0-10')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [], 'LST Exclude': [[4.0, 10.0]]}, results)

        self.adapter.update_lst_parameters('lst_ex', '2.0 - 8.5, 22.0 - 24.0')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [], 'LST Exclude': [[2.0, 8.5], [22.0, 24.0]]}, results)

        self.adapter.update_lst_parameters('lst_in', '0.0 - 2.0')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [[0.0, 2.0]], 'LST Exclude': [[2.0, 8.5], [22.0, 24.0]]}
                       , results)

        self.adapter.update_lst_parameters('lst_in', '4.0 - 8.0, 12.0 - 18.0')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [[4.0, 8.0], [12.0, 18.0]]
                        , 'LST Exclude': [[2.0, 8.5], [22.0, 24.0]]}
                       , results)

        self.adapter.update_lst_parameters('lst_ex', '')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [[4.0, 8.0], [12.0, 18.0]]
                        , 'LST Exclude': []}
                       , results)
        
        self.adapter.update_lst_parameters('lst_in', '')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [], 'LST Exclude': []}, results)
