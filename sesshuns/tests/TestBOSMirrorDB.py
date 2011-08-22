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

from test_utils                                   import NellTestCase
from nell.utilities.database.external.BOSMirrorDB import BOSMirrorDB
from datetime                                     import datetime, date

class TestBOSMirrorDB(NellTestCase):

    def setUp(self):

        self.bos = BOSMirrorDB()

    # this really isn't a 'unit test' since I'm interacting with PST's
    # Database, but a test is better then no test
    def test_getReservationsByUserAuthId(self):

        # Here we're assuming that reservations from the past 
        # don't get changed - so we'll use this fact to test.
        # Dana comes to GB all the time.
        danasId = 20 # remember - this IS NOT his global id
        since = datetime(2011, 8, 1)
        res = self.bos.getReservationsByUserAuthId(danasId, since)
        self.assertTrue(len(res) > 0)
        r = res[0]
        exp = (date(2011, 8, 11), date(2011, 8, 13))
        self.assertEquals(exp, r)

    def test_getReservationsByDateRange(self):

        start = datetime(2011, 8, 1)
        end   = datetime(2011, 8, 3)
        res = self.bos.getReservationsByDateRange(start, end)
        exp = [(1440
              , 'Charles Figura'
              , date(2011, 7, 29)
              , date(2011, 8, 9))
              ]
        self.assertEquals(exp, res)             
