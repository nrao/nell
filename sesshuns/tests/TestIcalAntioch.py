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

from test_utils              import NellTestCase
from nell.utilities          import IcalAntioch

class TestIcalAntioch(NellTestCase):

    def testWriteSchedule(self):
        #ic = IcalAntioch.IcalAntioch(None, None)
        ic = IcalAntioch(None, None)
        pStr = "Period: 18 (0)  at 2006-02-01 00:00:00 for 420 (420) with score of 3.669943 from 2006-02-01 00:00:00 Scheduled  band: X  RA: 4.674547 grade: 4.0"
        dct = ic.parsePeriod(pStr)
        self.assertEquals('18', dct["sName"])
        self.assertEquals('X',  dct["band"])
        dct['id'] = 34
        event = ic.createEvent(dct)
        self.assertTrue(event is not None)

