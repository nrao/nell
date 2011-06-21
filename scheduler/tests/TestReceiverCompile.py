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

from nell.utilities.receiver import ReceiverCompile
from test_utils              import NellTestCase
from scheduler.models         import *

class TestReceiverCompile(NellTestCase):

    def setUp(self):

        super(TestReceiverCompile, self).setUp()
        self.nn = Receiver.get_abbreviations()
        self.rc = ReceiverCompile(self.nn)

        # normalize:   values[0] -> values[1]
        # denormalize: values[1] -> values[0]
        self.values = [('Q', [['Q']])
                     , ('((L | X) | C)', [['L', 'X', 'C']])
                     , ('(K & (L | S))', [['K'], ['L', 'S']])
                     , ('((342 | K) & (342 | Ka))'
                      , [['342', 'K'], ['342', 'Ka']] )
                     , ('((((L | X) | C) | S) & 342)'
                      , [['L', 'X', 'C', 'S'], ['342']])
                     ]

    def test_pairValues(self):

        self.assertEquals('Q', self.rc.pairValues(['Q'], '|'))
        self.assertEquals('((L | X) | C)'
                         , self.rc.pairValues(['L', 'X', 'C'], '|'))
        self.assertEquals('(((((L | X) | C) | A) | B) | C)'
                    , self.rc.pairValues(['L', 'X', 'C', 'A', 'B', 'C'], '|'))

    def test_denormalize(self):

        for v in self.values:
            self.assertEquals(v[0], self.rc.denormalize(v[1]))

    def test_symmettry(self):

        for v in self.values:
            self.assertEquals(v[0]
                            , self.rc.denormalize(self.rc.normalize(v[0])))

    def test_normalize(self):

        nn = Receiver.get_abbreviations()
        rc = ReceiverCompile(nn)
        self.assertEquals(rc.normalize(u'Q'), [[u'Q']])
        self.assertEquals(rc.normalize('K & (L | S)'),
                                       [['K'], ['L', 'S']])
        self.assertEquals(rc.normalize('342 | (K & Ka)'),
                                       [['342', 'K'], ['342', 'Ka']])
        self.assertEquals(rc.normalize('(L ^ 342) v (K & Ka)'),
                                       [['L', 'K'],   ['L', 'Ka'],
                                        ['342', 'K'], ['342', 'Ka']])
        self.assertEquals(rc.normalize('K | (Ka | Q)'),
                                       [['K', 'Ka', 'Q']])
        try:
            self.assertEquals(rc.normalize('J'), [['J']])
        except ValueError:
            pass
        else:
            self.fail()
        try:
            self.assertEquals(rc.normalize('K | Ka | Q'),
                                           [['K', 'Ka', 'Q']])
            self.assertEquals(rc.normalize('J'), [['J']])
        except SyntaxError:
            pass
        else:
            self.fail()

