from datetime import datetime

from test_utils.NellTestCase import NellTestCase
from sesshuns.models         import compliment_events

class TestComplimentEvents(NellTestCase):

    def test_compliment_events(self):

        start = datetime(2006, 2, 10)
        end   = datetime(2006, 2, 20)

        # special cases
        result = compliment_events([], start, end)
        self.assertEquals([(start, end)], result)

        result = compliment_events([(start, end)], start, end)
        self.assertEquals([], result)

        # more general
        events = [(datetime(2006, 2, 15), end)]
        comp   = [(start,                 datetime(2006, 2, 15))]
        result = compliment_events(events, start, end)
        self.assertEquals(comp, result)

        events = [(start,                 datetime(2006, 2, 15))]
        comp   = [(datetime(2006, 2, 15), end)]
        result = compliment_events(events, start, end)
        self.assertEquals(comp, result)

        # make more events
        events = [(datetime(2006, 2, 12), datetime(2006, 2, 13))
                , (datetime(2006, 2, 17), datetime(2006, 2, 19))
                , (datetime(2006, 2, 19, 12), end)]
        comp   = [(start,                 datetime(2006, 2, 12))
                , (datetime(2006, 2, 13), datetime(2006, 2, 17))
                , (datetime(2006, 2, 19), datetime(2006, 2, 19, 12))]
        result = compliment_events(events, start, end)
        self.assertEquals(comp, result)

        events = [(start,                 datetime(2006, 2, 13))
                , (datetime(2006, 2, 17), datetime(2006, 2, 19))
                , (datetime(2006, 2, 19, 12), end)]
        comp   = [(datetime(2006, 2, 13), datetime(2006, 2, 17))
                , (datetime(2006, 2, 19), datetime(2006, 2, 19, 12))]
        result = compliment_events(events, start, end)
        self.assertEquals(comp, result)       
