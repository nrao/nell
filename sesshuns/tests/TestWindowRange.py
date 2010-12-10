from test_utils.NellTestCase import NellTestCase
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

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

        start = datetime(2009, 6, 1)
        dur   = 7 # days
        

        # create window range
        w = WindowRange(window = self.w
                      , start_date = start
                      , duration = dur)
        w.save()

        self.assertEquals(datetime(2009, 6, 7), w.last_date())

    def test_lstInRange(self):

        tg = first(self.sesshun.target_set.all())
        # ra to lst: rads to hours
        lst = TimeAgent.rad2hr(tg.horizontal)

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

    

