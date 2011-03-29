# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 675 Mass Ave Cambridge, MA 02139, USA.
#
# Correspondence concerning GBT software should be addressed as follows:
#     GBT Operations
#     National Radio Astronomy Observatory
#     P. O. Box 2
#     Green Bank, WV 24944-0002 USA

if __name__ == "__main__":
    import sys
    sys.path[1:1] = [".."]

from AnalogSet      import *
from datetime       import datetime
import unittest

# Many tests use datetime, but simple floats would work just as well.

d0 = datetime(2009, 1, 1, 0, 0, 0)
d1 = datetime(2009, 1, 1, 1, 0, 0)
d2 = datetime(2009, 1, 1, 2, 0, 0)
d3 = datetime(2009, 1, 1, 3, 0, 0)

class TestAnalogSet(unittest.TestCase):

    def runAllCombinations(self, f, expected):
        self.assertEquals(expected[0],  f((d0, d1), (d2, d3)))
        self.assertEquals(expected[1],  f((d2, d3), (d0, d1)))
        self.assertEquals(expected[2],  f((d0, d1), (d0, d1)))
        self.assertEquals(expected[3],  f((d0, d1), (d1, d2)))
        self.assertEquals(expected[4],  f((d1, d2), (d0, d1)))
        self.assertEquals(expected[5],  f((d1, d2), (d0, d3)))
        self.assertEquals(expected[6],  f((d1, d2), (d0, d2)))
        self.assertEquals(expected[7],  f((d0, d3), (d1, d2)))
        self.assertEquals(expected[8],  f((d0, d2), (d0, d1)))
        self.assertEquals(expected[9],  f((d0, d2), (d1, d3)))
        self.assertEquals(expected[10], f((d0, d1), (d0, d2)))
        self.assertEquals(expected[11], f((d1, d3), (d0, d2)))

    def test_overlaps(self):
        exp = [False
             , False
             , True
             , False
             , False
             , True
             , True
             , True
             , True
             , True
             , True
             , True
              ]
        self.runAllCombinations(overlaps, exp)

    def test_intersect(self):
        exp = [()
             , ()
             , (d0, d1)
             , ()
             , ()
             , (d1, d2)
             , (d1, d2)
             , (d1, d2)
             , (d0, d1)
             , (d1, d2)
             , (d0, d1)
             , (d1, d2)
              ]
        self.runAllCombinations(intersect, exp)

    def test_intersects(self):
        self.assertEquals([], [])

        range_lists = [[(datetime(2009, 1, 1), datetime(2009, 1, 3))]
                     , [(datetime(2009, 1, 2), datetime(2009, 1, 4))]]
        expected = [
            (datetime(2009, 1, 2), datetime(2009, 1, 3))
        ]
        r = intersects(range_lists)
        self.assertEquals(expected, r)

        range_lists = [[(datetime(2009, 4,  9), datetime(2009, 4, 17))
                      , (datetime(2009, 4,  5), datetime(2009, 4,  8))]
                     , [(datetime(2009, 4,  6), datetime(2009, 4,  8))
                      , (datetime(2009, 4, 13), datetime(2009, 4, 25))]]
        expected = [
            (datetime(2009, 4, 13), datetime(2009, 4, 17))
          , (datetime(2009, 4,  6), datetime(2009, 4,  8))
        ]
        r = intersects(range_lists)
        self.assertEquals(expected, r)

        range_lists = [[(datetime(2009, 4, 9), datetime(2009, 4, 17))
                      , (datetime(2009, 4, 5), datetime(2009, 4, 8))]
                     , [(datetime(2009, 4, 6), datetime(2009, 4, 8))]]
        expected = [
            (datetime(2009, 4, 6), datetime(2009, 4, 8))
        ]
        r = intersects(range_lists)
        self.assertEquals(expected, r)

    def test_union(self):
        exp = [[(d0, d1), (d2, d3)]
             , [(d2, d3), (d0, d1)]
             , [(d0, d1)]
             , [(d0, d2)]
             , [(d0, d2)]
             , [(d0, d3)]
             , [(d0, d2)]
             , [(d0, d3)]
             , [(d0, d2)]
             , [(d0, d3)]
             , [(d0, d2)]
             , [(d0, d3)]
              ]
        self.runAllCombinations(union, exp)
        self.assertEquals([(3,6)], union((3,5), (5,6)))

    def test_unions(self):
        self.assertEquals([], unions([]))
        self.assertEquals([(1,2)], unions([(1,2), (1,2)]))
        self.assertEquals([(1,2)], unions([(1,2), (1,2), (1,2)]))
        self.assertEquals([(1,2), (3,4)], unions([(1,2), (3,4)]))
        self.assertEquals([(1,2), (3,4), (5,6)], unions([(1,2), (3,4), (5,6)]))
        self.assertEquals([(1,2), (3,6)], unions([(1,2), (3,5), (5,6)]))
        self.assertEquals([(1,2), (3,6)], unions([(1,2), (5,6), (3,5)]))
        self.assertEquals([(1,2), (3,6)], unions([(3,5), (1,2), (5,6)]))
        self.assertEquals([(3,6), (1,2)], unions([(3,5), (5,6), (1,2)]))
        self.assertEquals([(3,6), (1,2)], unions([(5,6), (3,5), (1,2)]))
        self.assertEquals([(1,2), (3,6)], unions([(5,6), (1,2), (3,5)]))
        self.assertEquals([(1,2), (3,10)], unions([(1,2), (3,6), (5,8), (7,10)]))
        self.assertEquals([(3,10), (1,2)], unions([(3,6), (5,8), (7,10), (1,2)]))
        self.assertEquals([(1,2), (3,10)], unions([(3,6), (7,10), (1,2), (5,8)]))
        self.assertEquals([(3,10), (1,2)], unions([(1,2), (3,6), (5,8), (7,10), (1,2)]))
        self.assertEquals([(3,10), (1,2)], unions([(8,9), (3,6), (5,8), (7,10), (1,2)]))
        self.assertEquals([(1,10)], unions([(8,9), (2,6), (5,8), (7,10), (1,2)]))
        self.assertEquals([(1,2), (4,8), (9,11)], unions([(4,6), (9,10), (1,2), (5,8), (10,11)]))

    def test_diff(self):
        exp = [[(d0, d1)]
             , [(d2, d3)]
             , []
             , [(d0, d1)]
             , [(d1, d2)]
             , []
             , []
             , [(d0, d1), (d2, d3)]
             , [(d1, d2)]
             , [(d0, d1)]
             , []
             , [(d2, d3)]
              ]
        self.runAllCombinations(diff, exp)

    def test_diffs(self):
        self.assertEquals([(16, 18)], diffs([(15, 20)], [(10, 16), (18, 24)]))
        self.assertEquals([(15, 20)], diffs([(15, 20)],[(10, 14), (22, 24)]))
        self.assertEquals([], diffs([(15, 20)],[(10, 18), (18, 24)]))
        self.assertEquals([], diffs([(15, 20)],[(10, 22), (18, 24)]))
        self.assertEquals([(1, 2), (5, 6), (9, 10)]
                        , diffs([(1, 3), (4, 7), (9, 11)]
                               ,[(2, 5), (6, 8), (10, 12)]))
        self.assertEquals([(5, 6), (1, 2), (9, 10)]
                        , diffs([(4, 7), (1, 3), (9, 11)]
                               ,[(2, 5), (10, 12), (6, 8)]))

if __name__ == "__main__":
    unittest.main()
