from test_utils.NellTestCase import NellTestCase
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestWindow(NellTestCase):
    def setUp(self):
        super(TestWindow, self).setUp()
        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("windowed")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        pending = first(Period_State.objects.filter(abbreviation = "P"))
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.default_period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = pending
                                   , accounting = pa
                                   )
        self.default_period.save()
        pjson = PeriodHttpAdapter(self.default_period).jsondict('UTC', 1.1)
        self.fdata = {"session":  1
                    , "start":    "2009-06-01"
                    , "duration": 7
                    , "default_date" : pjson['date']
                    , "default_time" : pjson['time']
                    , "default_duration" : pjson['duration']
                    , "default_state" : pjson['state']
                    }

    def test_update_from_post(self):
        w = Window()
        adapter = WindowHttpAdapter(w)
        adapter.init_from_post(self.fdata)

        self.assertEqual(w.session, self.sesshun)
        self.assertEqual(w.start_date, date(2009, 6, 1))
        self.assertEqual(w.duration, self.fdata["duration"])
        self.assertEqual(w.default_period.start, self.default_period.start)
        self.assertEqual(w.period, None)

    def test_jsondict(self):

        start = datetime(2009, 6, 1)
        startStr = start.strftime("%Y-%m-%d")
        dur   = 7 # days
        end = start + timedelta(days = dur - 1)
        endStr = end.strftime("%Y-%m-%d")

        w = Window()
        w.start_date = start
        w.duration = dur
        w.session = self.sesshun
        w.default_period = self.default_period

        w.save()

        adapter = WindowHttpAdapter(w)

        jd = adapter.jsondict()

        self.assertEqual(jd["duration"], dur)
        self.assertEqual(jd["start"], startStr)
        self.assertEqual(jd["end"], endStr)
        self.assertEqual(jd["session"], SessionHttpAdapter(self.sesshun).jsondict())
        self.assertEqual(jd["chosen_period"], None)

        w.delete()

    def test_reconcile(self):

        deleted   = Period_State.get_state("D")
        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")

        start = datetime(2009, 6, 1)
        dur   = 7 # days

        w = Window()
        w.start_date = start
        w.duration = dur
        w.session = self.sesshun
        w.default_period = self.default_period
        w.save()
        w_id = w.id

        # test
        self.assertEquals(w.default_period.state, pending)
        self.assertEquals(w.state(), pending)

        # this should move the default_period to scheduled
        # and copy the defatul_period to period
        w.reconcile()

        # test
        # get it fresh from the DB
        w = first(Window.objects.filter(id = w_id))
        self.assertEquals(w.default_period.state, scheduled)
        self.assertTrue(w.period is not None)
        self.assertEquals(w.period.state, scheduled)
        self.assertEquals(w.period.id, w.default_period.id)
        self.assertEquals(w.state(), scheduled)

    def test_reconcile_2(self):

        deleted   = Period_State.get_state("D")
        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")

        # the period to be scheduled
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        dt = self.default_period.start - timedelta(days = 2)
        period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = pending
                                   , accounting = pa
                                   )
        period.save()

        start = datetime(2009, 6, 1)
        dur   = 7 # days

        w = Window()
        w.start_date = start
        w.duration = dur
        w.session = self.sesshun
        w.default_period = self.default_period
        w.period = period
        w.save()
        w_id = w.id

        # test
        self.assertEquals(w.default_period.state, pending)
        self.assertEquals(w.period.state, pending)
        self.assertEquals(w.state(), pending)

        # this should move the default_period to deleted
        # and the chosen period to scheduled
        w.reconcile()

        # test
        # get it fresh from the DB
        w = first(Window.objects.filter(id = w_id))
        self.assertEquals(w.default_period.state, deleted)
        self.assertTrue(w.period is not None)
        self.assertEquals(w.period.state, scheduled)
        self.assertEquals(w.state(), scheduled)

