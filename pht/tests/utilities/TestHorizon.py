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
import math
from mx                    import DateTime
from pht.utilities         import * 
from pht.utilities.Horizon import Horizon 

class TestHorizon(unittest.TestCase):

    def test_hourAngleIntersection(self):
        h = Horizon()
        # doesn't rise
        self.assertEquals(0.0, h.hourAngleIntersection(-80.0))
        # never sets
        self.assertEquals(12.0, h.hourAngleIntersection(90.0))
        # in between
        self.assertAlmostEquals(5.567149, h.hourAngleIntersection(0.0), 3)
        self.assertAlmostEquals(8.62116, h.hourAngleIntersection(45.0), 3)

    def test_riseSet2centerWidth(self):

        h = Horizon()

        rise = DateTime.DateTimeDelta(0, 12, 0, 0)
        set  = DateTime.DateTimeDelta(0, 18, 0, 0)

        center, width = h.riseSet2centerWidth(rise, set)
        self.assertEqual(15.0, center.hours)
        self.assertEqual(6.0, width.hours)

        # make sure wrap around works
        rise = DateTime.DateTimeDelta(0, 22, 0, 0)
        set  = DateTime.DateTimeDelta(0,  4, 0, 0)

        center, width = h.riseSet2centerWidth(rise, set)
        self.assertEqual(1.0, center.hours)
        self.assertEqual(6.0, width.hours)

        rise = DateTime.DateTimeDelta(0, 18, 0, 0)
        set  = DateTime.DateTimeDelta(0, 12, 0, 0)

        center, width = h.riseSet2centerWidth(rise, set)
        self.assertEqual(18.0, width.hours)
        self.assertEqual(3.0, center.hours)

        # 0 - 24 is a popular range
        rise = DateTime.DateTimeDelta(0, 0, 0, 0)
        set  = DateTime.DateTimeDelta(0, 24, 0, 0)

        center, width = h.riseSet2centerWidth(rise, set)
        self.assertEqual(24.0, width.hours)
        self.assertEqual(12.0, center.hours)

    def test_getRiseSet(self):

        now = DateTime.DateTime(2006, 5, 31, 18, 6, 4)

        # default elevation limit
        h = Horizon()
        rise, set = h.riseSetLSTs(20.0, 20.0, now)
        self.assertEqual('18:41:12.03', str(rise))
        self.assertEqual('07:58:47.97', str(set))

        # raise the el. limit and watch things rise later 
        # and set earlier
        h = Horizon(20.0)
        rise, set = h.riseSetLSTs(20.0, 20.0, now)
        self.assertEqual('20:00:15.72', str(rise))
        self.assertEqual('06:39:44.28', str(set))

        # a lower dec should mean less time up  
        h = Horizon(20.0)
        rise, set = h.riseSetLSTs(20.0, 0.0, now)
        self.assertEqual('21:03:18.21', str(rise))
        self.assertEqual('05:36:41.79', str(set))

        # demonstrates that we need to normalize results
        h = Horizon()
        ra = rad2deg(hr2rad(22.0))
        rise, set = h.riseSetLSTs(ra, 10.0, now)
        self.assertEqual('15:54:14.83', str(rise))
        # watch for > 24 hours
        self.assertEqual('1:04:05:45.17', str(set))
        self.assertAlmostEqual(28.0958, set.hours, 2)

        self.assertAlmostEquals(4.09588185187, h.normalizeHours(set), 3)

        # source that is always up
        rise, set = h.riseSetLSTs(ra, 80.0, now)
        self.assertTrue(set is None) 

        # source that is never up
        rise, set = h.riseSetLSTs(ra, -80.0, now)
        self.assertTrue(rise is None) 

        # but a source that is always up may not survive the el limit 
        h = Horizon(30)
        elLimHr = rad2hr(deg2rad(30))
        rise, set = h.riseSetLSTs(ra, 80.0, now)
        self.assertTrue(set is not None) 



