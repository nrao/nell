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

from django.test   import TestCase
from pht.models    import Target
from pht.utilities import *

class TestTarget(TestCase):

    fixtures = ['proposal_GBT12A-002.json']

    def setUp(self):

        self.targets = Target.objects.all().order_by('id')
        self.t1 = self.targets[0]

    def test_calcLSTrange(self):
        self.assertEqual((None, None), self.t1.calcLSTrange())

        self.t1.ra  = deg2rad(20.0)
        self.t1.dec = deg2rad(20.0)
        self.t1.save()

        rise, set = self.t1.calcLSTrange() 
        self.assertAlmostEqual(4.89215, rise, 3)  
        self.assertAlmostEqual(2.08915,  set, 3)  

        # min elevation changes things
        self.t1.elevation_min = deg2rad(20.0)
        self.t1.save()

        rise, set = self.t1.calcLSTrange() 
        self.assertAlmostEqual(5.237131, rise, 3)  
        self.assertAlmostEqual(1.744185,  set, 3)  

        # circumpolar
        self.t1.dec = deg2rad(80.0)
        self.t1.save()
        rise, set = self.t1.calcLSTrange()
        self.assertAlmostEqual(0.0, rise, 3)
        self.assertAlmostEqual(hr2rad(24.0), set, 3)

        # circumcise
        self.t1.dec = deg2rad(-80.0)
        self.t1.save()
        rise, set = self.t1.calcLSTrange()
        self.assertAlmostEqual(0.0, rise, 3)
        self.assertAlmostEqual(0.0, set, 3)

    def test_calcCenterWidthLST(self):

        minLst = hr2rad(12.0) # rise
        maxLst = hr2rad(18.0) # set
        center, width = self.t1.calcCenterWidthLST(minLst = minLst
                                                 , maxLst = maxLst)
        self.assertAlmostEquals(15.0, rad2hr(center), 1)
        self.assertAlmostEquals( 6.0, rad2hr(width), 1)


        minLst = hr2rad(18.0) # rise
        maxLst = hr2rad(12.0) # set
        center, width = self.t1.calcCenterWidthLST(minLst = minLst
                                                 , maxLst = maxLst)
        self.assertAlmostEquals( 3.0, rad2hr(center), 1)
        self.assertAlmostEquals(18.0, rad2hr(width), 1)

        minLst = hr2rad(0.0) # rise
        maxLst = hr2rad(24.0) # set
        center, width = self.t1.calcCenterWidthLST(minLst = minLst
                                                 , maxLst = maxLst)
        self.assertAlmostEquals(12.0, rad2hr(center), 1)
        self.assertAlmostEquals(24.0, rad2hr(width), 1)

        # this target has 0 - 24 set for min/max LST
        center, width = self.t1.calcCenterWidthLST()
        self.assertAlmostEquals(12.0, rad2hr(center), 1)
        self.assertAlmostEquals(24.0, rad2hr(width), 1)
