from datetime                import datetime, date, timedelta
from utilities               import TimeAgent
from test_utils              import NellTestCase
from utils                   import create_sesshun
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestWindowRange(NellTestCase):

    def setUp(self):
        super(TestWindowRange, self).setUp()

        # create a session
        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("windowed")
        self.sesshun.save()

        # create window
        self.w = Window(session = self.sesshun)
        self.w.save()

    def test_times(self):

        start = date(2009, 6, 1)
        dur   = 7 # days
        

        # create window range
        w = WindowRange(window = self.w
                      , start_date = start
                      , duration = dur)
        w.save()

        self.assertEquals(datetime(2009, 6, 1), w.start_datetime())
        self.assertEquals(date(2009, 6, 7), w.last_date())
        self.assertEquals(date(2009, 6, 7), w.end())
        self.assertEquals(datetime(2009, 6, 8, 0), w.end_datetime())
        self.assertEquals(False, w.inWindow(date(2009, 5, 31)))
        self.assertEquals(True,  w.inWindow(date(2009, 6, 1)))
        self.assertEquals(True,  w.inWindow(date(2009, 6, 7)))
        self.assertEquals(False, w.inWindow(date(2009, 6, 8)))
        self.assertEquals(False, w.inWindowDT(datetime(2009, 5, 31, 23, 59, 59)))
        self.assertEquals(True, w.inWindowDT(datetime(2009, 6, 1)))
        self.assertEquals(True, w.inWindowDT(datetime(2009, 6, 7, 23)))
        self.assertEquals(False, w.inWindowDT(datetime(2009, 6, 8)))

        p = Period(session = self.sesshun
                 , start = datetime(2009, 5, 30, 23)
                 , duration = 2)
        p.save()

        self.assertEquals(False, w.isInWindow(p))

        p.start = p.start + timedelta(days = 1)
        p.save()
        self.assertEquals(True, w.isInWindow(p))

        p.start = datetime(2009, 6, 7, 23) 
        p.save()
        self.assertEquals(True, w.isInWindow(p))

        p.start = p.start + timedelta(days = 1)
        p.save()
        self.assertEquals(False, w.isInWindow(p))

    def test_lstInRange(self):

        # ra to lst: rads to hours
        lst = TimeAgent.rad2hr(self.sesshun.target.horizontal)

        # create the window range
        utcStart = datetime(2009, 6, 1)
        utcEnd   = datetime(2009, 6, 2)
        wr = WindowRange(window = self.w
                       , start_date = utcStart
                       , duration = (utcEnd - utcStart).days)
        wr.save()

        # any target should be in range, w/ out a buffer
        inRange = wr.lstInRange(lst)
        self.assertEquals(True, inRange)

        # but with a big enough buffer, no target can be in range
        buffer = 12.0
        inRange = wr.lstInRange(lst, buffer = buffer)
        self.assertEquals(False, inRange)
        
        # make the buffer reasonable enough, and it passes again
        buffer = 4.5
        inRange = wr.lstInRange(lst, buffer = buffer)
        self.assertEquals(True, inRange)

    

