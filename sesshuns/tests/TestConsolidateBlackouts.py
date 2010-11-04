from datetime import datetime

from test_utils.NellTestCase import NellTestCase
from sesshuns.models         import consolidate_events

class TestConsolidateBlackouts(NellTestCase):

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

