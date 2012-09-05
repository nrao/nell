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

from django.test         import TestCase

from datetime import date, datetime

from utilities import TimeAgent
from pht.tools.Sun import Sun

class TestSun(TestCase):

    def test_getSunRise(self):

        sun = Sun()

        # close to the winter solstice
        dt = date(2011, 12, 25)
        rise = TimeAgent.quarter(sun.getSunRise(dt))
        # 12:30 UT
        self.assertEqual(datetime(2011, 12, 25, 12, 30), rise) 
        # close to the summer solstice
        dt = date(2012, 6, 25)
        rise = TimeAgent.quarter(sun.getSunRise(dt))
        # 10 UT
        self.assertEqual(datetime(2012, 6, 25, 10, 0), rise) 

    def test_getSunSet(self):

        sun = Sun()

        # close to the winter solstice
        dt = date(2011, 12, 25)
        set = TimeAgent.quarter(sun.getSunSet(dt))
        # 22:00 UT
        self.assertEqual(datetime(2011, 12, 25, 22, 0), set) 
        # close to the summer solstice
        dt = date(2012, 6, 25)
        set = TimeAgent.quarter(sun.getSunSet(dt))
        # 00:45 UT ON THE NEXT DAY
        self.assertEqual(datetime(2012, 6, 26, 0, 45), set) 

    def test_getRiseSet(self):

        sun = Sun()

        dt = date(2011, 12, 25)
        rise, set = sun.getRiseSet(dt)
        # 12:30 UT
        self.assertEqual(datetime(2011, 12, 25, 12,30)
                       , TimeAgent.quarter(rise)) 
        self.assertEqual(datetime(2011, 12, 25, 22, 0)
                       , TimeAgent.quarter(set)) 
        # close to the summer solstice
        dt = date(2012, 6, 25)
        rise, set = sun.getRiseSet(dt)
        # 00:45 UT ON THE NEXT DAY
        self.assertEqual(datetime(2012, 6, 25, 10, 0)
                       , TimeAgent.quarter(rise)) 
        self.assertEqual(datetime(2012, 6, 26, 0, 45)
                       , TimeAgent.quarter(set)) 

        # close to the summer solstice
        dts = (date(2012, 8, 1)
             , date(2012, 8, 2)
             , date(2012, 8, 3)
             , date(2013, 1, 29)
             , date(2013, 1, 30)
             )
        expected = ((datetime(2012, 8, 1, 10, 21, 31), datetime(2012, 8, 2, 0, 30, 12))
                  , (datetime(2012, 8, 2, 10, 22, 24), datetime(2012, 8, 3, 0, 29, 12))
                  , (datetime(2012, 8, 3, 10, 23, 16), datetime(2012, 8, 4, 0, 28, 10))
                  , (datetime(2013, 1, 29, 12, 26, 38), datetime(2013, 1, 29, 22, 38, 52))
                  , (datetime(2013, 1, 30, 12, 25, 49), datetime(2013, 1, 30, 22, 40, 0))
                    )
        for dt, (exp_rise, exp_set) in zip(dts, expected):
            rise, set = sun.getRiseSet(dt)
            self.assertEqual(exp_rise, rise) 
            self.assertEqual(exp_set, set) 

    def test_getPTCSRiseSet(self):

        sun = Sun()

        dt = date(2011, 12, 25)
        rise, set = sun.getPTCSRiseSet(dt)
        self.assertEqual(datetime(2011, 12, 25, 12,30)
                       , TimeAgent.quarter(rise)) 
        self.assertEqual(datetime(2011, 12, 26,  1, 0)
                       , TimeAgent.quarter(set)) 
        # close to the summer solstice
        dt = date(2012, 6, 25)
        rise, set = sun.getPTCSRiseSet(dt)
        self.assertEqual(datetime(2012, 6, 25, 10, 0)
                       , TimeAgent.quarter(rise)) 
        self.assertEqual(datetime(2012, 6, 26, 3, 45)
                       , TimeAgent.quarter(set)) 

