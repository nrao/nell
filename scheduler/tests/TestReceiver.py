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

from test_utils              import BenchTestCase, timeIt
from scheduler.models         import Sesshun, Receiver
from scheduler.httpadapters   import SessionHttpAdapter

class TestReceiver(BenchTestCase):

    def setUp(self):
        super(TestReceiver, self).setUp()
        s = Sesshun()
        adapter = SessionHttpAdapter(s)
        adapter.init_from_post({})
        s.save()

    @timeIt
    def test_get_abbreviations(self):
        nn = Receiver.get_abbreviations()
        self.assertTrue(len(nn) > 17)
        self.assertEquals([n for n in nn if n == 'Ka'], ['Ka'])

    @timeIt
    def test_save_receivers(self):
        s = Sesshun.objects.all()[0]
        rcvr = ''
        adapter = SessionHttpAdapter(s)
        adapter.save_receivers(rcvr)
        rgs = s.receiver_group_set.all()
        self.assertEqual(0, len(rgs))
        rcvr = 'L'
        adapter.save_receivers(rcvr)
        rgs = s.receiver_group_set.all()
        self.assertEqual(1, len(rgs))
        self.assertEqual(rcvr, rgs[0].receivers.all()[0].abbreviation)

        s.receiver_group_set.all().delete()
        adapter.save_receivers('L | (X & S)')
        rgs = s.receiver_group_set.all().order_by('id')
        #print rgs[0].receivers.all()[1].abbreviation
        self.assertEqual(2, len(rgs))
        #print rgs[0].receivers.all()[0].abbreviation
        #print rgs[0].receivers.all()[1].abbreviation
        #print rgs[1].receivers.all()[0].abbreviation
        #print rgs[1].receivers.all()[1].abbreviation
        rs = rgs[0].receivers.all().order_by('id')
        self.assertEqual('L', rs[0].abbreviation)
        self.assertEqual('X', rs[1].abbreviation)
        rs = rgs[1].receivers.all().order_by('id')
        self.assertEqual('L', rs[0].abbreviation)
        self.assertEqual('S', rs[1].abbreviation)

