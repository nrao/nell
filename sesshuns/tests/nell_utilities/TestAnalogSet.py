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

from utilities.AnalogSet      import *
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
        self.assertEquals(expected[12], f((d0, d2), (d1, d2)))

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
             , [(d0, d2)]
              ]
        self.runAllCombinations(union, exp)
        self.assertEquals([(3,6)], union((3,5), (5,6)))

    def test_unions1(self):
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

    def test_unions2(self):
        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 1, 18)
          , datetime(2009, 1, 2, 11)
          , datetime(2009, 1, 2, 12)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 4, 18)
          , datetime(2009, 1, 4, 13)
          , datetime(2009, 1, 4, 20)
        ]
        expected = [
            # begin = b1 start, end = b5 end
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 4, 20))
        ]

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)
        return
        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 1, 11)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 3, 11)
        ]
        expected = [
            # begin = b1 start, end = b1 end
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 3, 11))
        ]

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 4, 11)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 5, 11)
        ]
        expected = [
            # nothing to reduce
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 3, 11))
          , (datetime(2009, 1, 4, 11), datetime(2009, 1, 5, 11))
        ]

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        starts = [
            datetime(2009, 1, 1, 11)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
        ]
        expected = [
            # one conflict
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 3, 11))
        ]

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        # No conflicts.
        r = unions([])
        self.assertEquals([], r)

    def test_unions3(self):

        # test 1
        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 2, 11)
          , datetime(2009, 1, 1,  0)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 4, 13)
          , datetime(2009, 1, 5,  0)
        ]
        expected = [
            # begin = b3 start, end = b3 end
            (datetime(2009, 1, 1), datetime(2009, 1, 5))
        ]
        
        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)
        
        # test 2
        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 4, 11)
          , datetime(2009, 1, 1,  0)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 4, 23)
          , datetime(2009, 1, 5,  0)
        ]
        expected = [
            (datetime(2009, 1, 1), datetime(2009, 1, 5))
        ]

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        # test 3
        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 4, 11)
          , datetime(2009, 1, 1,  0)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 4, 23)
          , datetime(2009, 1, 5,  0)
        ]
        expected = [
            (datetime(2009, 1, 1), datetime(2009, 1, 5))
        ]

        r = unions([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        # test 4
        starts = [
            datetime(2009, 1, 1, 0)
          , datetime(2009, 1, 4, 0)
          , datetime(2009, 1, 2, 0)
        ]
        ends   = [
            datetime(2009, 1, 5, 0)
          , datetime(2009, 1, 7, 0)
          , datetime(2009, 1, 3, 0)
        ]
        expected = [
            (datetime(2009, 1, 1), datetime(2009, 1, 7))
        ]

        r = unions(sorted([(s, e) for s, e in zip(starts, ends)]))
        self.assertEquals(expected, r)

        # test x
        starts = [
            datetime(2009, 11, 6, 16)
          , datetime(2009, 11, 11, 0)
          , datetime(2009, 11, 15, 0, 45)
         ]
        ends = [
            datetime(2009, 11, 17, 23, 59, 59)
          , datetime(2009, 11, 14, 20, 45,  0)
          , datetime(2009, 11, 18,  0, 30,  0)
         ]
        expected = [(datetime(2009, 11, 6, 16), datetime(2009, 11, 18, 0, 30))]

        r = unions(sorted([(s, e) for s, e in zip(starts, ends)]))
        self.assertEquals(expected, r)

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
             , [(d0, d1)]
              ]
        self.runAllCombinations(diff, exp)
        self.assertEquals([(d0, d2)],  diff((d0, d3), (d2, d3)))

    def test_diffs1(self):
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
        self.assertEquals([(1, 2)], diffs([(1, 3)], [(2, 3)]))


    def test_diffs2(self):

        start = datetime(2006, 2, 10)
        end   = datetime(2006, 2, 20)
        range_a = [(start, end)]

        # special cases
        result = diffs(range_a, [])
        self.assertEquals([(start, end)], result)

        result = diffs(range_a, range_a)
        self.assertEquals([], result)

        # more general
        events = [(datetime(2006, 2, 15), end)]
        comp   = [(start,                 datetime(2006, 2, 15))]
        result = diffs(range_a, events)
        self.assertEquals(comp, result)

        events = [(start,                 datetime(2006, 2, 15))]
        comp   = [(datetime(2006, 2, 15), end)]
        result = diffs(range_a, events)
        self.assertEquals(comp, result)

        # make more events
        events = [(datetime(2006, 2, 12), datetime(2006, 2, 13))
                , (datetime(2006, 2, 17), datetime(2006, 2, 19))
                , (datetime(2006, 2, 19, 12), end)]
        comp   = [(start,                 datetime(2006, 2, 12))
                , (datetime(2006, 2, 13), datetime(2006, 2, 17))
                , (datetime(2006, 2, 19), datetime(2006, 2, 19, 12))]
        result = diffs(range_a, events)
        self.assertEquals(comp, result)

        events = [(start,                 datetime(2006, 2, 13))
                , (datetime(2006, 2, 17), datetime(2006, 2, 19))
                , (datetime(2006, 2, 19, 12), end)]
        comp   = [(datetime(2006, 2, 13), datetime(2006, 2, 17))
                , (datetime(2006, 2, 19), datetime(2006, 2, 19, 12))]
        result = diffs(range_a, events)
        self.assertEquals(comp, result)       

if __name__ == "__main__":
    unittest.main()
