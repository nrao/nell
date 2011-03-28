from datetime import datetime

from test_utils              import NellTestCase
from sesshuns.models.common         import consolidate_events
from sesshuns.models         import find_intersections, intersect

class TestConsolidateBlackouts(NellTestCase):

    def test_intersect(self):
        d0 = datetime(2009, 1, 1, 0, 0, 0)
        d1 = datetime(2009, 1, 1, 1, 0, 0)
        d2 = datetime(2009, 1, 1, 2, 0, 0)
        d3 = datetime(2009, 1, 1, 3, 0, 0)

        self.assertEquals((),       intersect((d0, d1), (d2, d3)))
        self.assertEquals((),       intersect((d2, d3), (d0, d1)))
        self.assertEquals((d0, d1), intersect((d0, d1), (d0, d1)))
        self.assertEquals((),       intersect((d0, d1), (d1, d2)))
        self.assertEquals((),       intersect((d1, d2), (d0, d1)))
        self.assertEquals((d1, d2), intersect((d1, d2), (d0, d3)))
        self.assertEquals((d1, d2), intersect((d0, d3), (d1, d2)))
        self.assertEquals((d1, d2), intersect((d0, d2), (d1, d3)))
        self.assertEquals((d1, d2), intersect((d1, d3), (d0, d2)))
        self.assertEquals((d1, d2), intersect((d1, d2), (d0, d2)))
        self.assertEquals((d0, d1), intersect((d0, d2), (d0, d1)))

    def test_find_intersections(self):

        eventSets = [[(datetime(2009, 1, 1), datetime(2009, 1, 3))]
                   , [(datetime(2009, 1, 2), datetime(2009, 1, 4))]]
        expected = [
            (datetime(2009, 1, 2), datetime(2009, 1, 3))
        ]
        r = find_intersections(eventSets)
        self.assertEquals(expected, r)

        eventSets = [[(datetime(2009, 4,  9), datetime(2009, 4, 17))
                    , (datetime(2009, 4,  5), datetime(2009, 4,  8))]
                   , [(datetime(2009, 4,  6), datetime(2009, 4,  8))
                    , (datetime(2009, 4, 13), datetime(2009, 4, 25))]]
        expected = [
            (datetime(2009, 4, 13), datetime(2009, 4, 17))
          , (datetime(2009, 4,  6), datetime(2009, 4,  8))
        ]
        r = find_intersections(eventSets)
        self.assertEquals(expected, r)

        eventSets = [[(datetime(2009, 4, 9), datetime(2009, 4, 17))
                    , (datetime(2009, 4, 5), datetime(2009, 4, 8))]
                   , [(datetime(2009, 4, 6), datetime(2009, 4, 8))]]
        expected = [
            (datetime(2009, 4, 6), datetime(2009, 4, 8))
        ]
        r = find_intersections(eventSets)
        self.assertEquals(expected, r)

    def test_consolidate_events2(self):

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
        
        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
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

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
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

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
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

        r = consolidate_events(sorted([(s, e) for s, e in zip(starts, ends)]))
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

        r = consolidate_events(sorted([(s, e) for s, e in zip(starts, ends)]))
        self.assertEquals(expected, r)

    def test_consolidate_events(self):
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

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
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

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
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

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
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

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        # No conflicts.
        r = consolidate_events([])
        self.assertEquals([], r)

