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

        

    

