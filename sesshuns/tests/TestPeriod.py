from sesshuns.httpadapters                 import *
from sesshuns.models                       import *
from test_utils.NellTestCase               import NellTestCase
from utils                                 import *

class TestPeriod(NellTestCase):

    def setUp(self):
        super(TestPeriod, self).setUp()
        self.sesshun = create_sesshun()
        self.fdata = {"session":  1
                    , "date":    "2009-6-1"
                    , "time":    "12:15"
                    , "duration": 4.25
                    , "backup":   False
                    , "receivers": "L, X"
                     }

    def test_create(self):

        # make sure the sesshun has some rcvrs
        SessionHttpAdapter(self.sesshun).save_receivers("L")

        p = Period.create(session = self.sesshun
                        , start = datetime(2009, 10, 1)
                        , duration = 10.0
                        )

        init_rcvrs_from_session(p.session, p)
        self.assertEqual(p.session.id, 1)
        self.assertEqual(p.duration, 10.0)
        self.assertEqual(p.receiver_list(), "L")

    def test_update_from_post(self):
        p = Period()
        adapter = PeriodHttpAdapter(p)
        adapter.init_from_post(self.fdata, 'UTC')

        self.assertEqual(p.session, self.sesshun)
        self.assertEqual(p.start, datetime(2009, 6, 1, 12, 15))
        self.assertEqual(p.duration, self.fdata["duration"])
        self.assertEqual(p.backup, self.fdata["backup"])
        self.assertEqual(len(p.receivers.all()), 2)
        #self.assertEqual(p.receivers.all(), 2)

    def test_jsondict(self):

        start = datetime(2009, 6, 1, 12, 15)
        dur   = 180

        pa = Period_Accounting(scheduled = 0)
        pa.save()

        p = Period()
        p.start = start
        p.duration = dur
        p.session = self.sesshun
        p.backup = True
        p.state = first(Period_State.objects.filter(abbreviation = 'P'))
        p.accounting = pa

        p.save()

        L = Receiver.get_rcvr("L")
        X = Receiver.get_rcvr("X")
        pr = Period_Receiver(period = p, receiver = L)
        pr.save()
        pr = Period_Receiver(period = p, receiver = X)
        pr.save()

        jd = PeriodHttpAdapter(p).jsondict('UTC', 1.1)

        self.assertEqual(jd["duration"], dur)
        self.assertEqual(jd["date"], "2009-06-01")
        self.assertEqual(jd["time"], "12:15")
        self.assertEqual(jd["state"], "P")
        self.assertEqual(jd["receivers"], "L, X")

        p.delete()

    def test_windows(self):
        pending = Period_State.get_state('P')

        # create a window w/ a period
        original_type = self.sesshun.session_type
        self.sesshun.session_type = Session_Type.get_type("windowed")

        start = datetime(2009, 6, 1, 12, 15)
        dur   = 180

        p = Period()
        p.start = start
        p.duration = dur
        p.session = self.sesshun
        p.state = pending
        p.accounting = Period_Accounting(scheduled = 0.0)
        p.accounting.save()
        p.save()
        p_id = p.id

        wstart = (start - timedelta(days = 7)).date()
        w = Window(start_date = wstart
                 , duration = 10 # days
                 , session = self.sesshun
                 , default_period = p)
        w.save()

        # and a period w/ out a window
        p2 = Period()
        p2.start = start
        p2.duration = dur
        p2.session = self.sesshun
        p2.state = pending
        pa2 = Period_Accounting(scheduled = 0.0)
        pa2.save()
        p2.accounting = pa2
        p2.save()
        p2_id = p2.id

        # test
        self.assertEquals(True,  p.is_windowed())
        self.assertEquals(True,  p.has_valid_windows())
        self.assertEquals(True,  p2.is_windowed())
        self.assertEquals(False, p2.has_valid_windows())
        self.assertEquals(w,     p.get_default_window())
        self.assertEquals(w,     p.get_window())
        self.assertEquals(True,  p.is_windowed_default())

        # now assign this second period as the 'chosen' period for the win.
        w.period = p2
        w.save()

        # test
        self.assertEquals(True,  p2.is_windowed())
        self.assertEquals(True,  p2.has_valid_windows())
        self.assertEquals(None,  p2.get_default_window())
        self.assertEquals(w,     p2.get_window())
        self.assertEquals(False, p2.is_windowed_default())

        # now publish!
        #p.publish()

        # test
        #deleted = Period_State.get_state("D")
        #scheduled = Period_State.get_state("S")
        # get these periods fresh from db again
        #p = first(Period.objects.filter(id = p_id))
        #p2 = first(Period.objects.filter(id = p2_id))
        #self.assertEquals(deleted, p.state)
        #self.assertEquals(scheduled, p2.state)

        # cleanup
        self.sesshun.session_type = original_type
        w.delete()
        p.delete()
        p2.save()

    def test_get_periods(self):

        # setup some periods
        times = [(datetime(2000, 1, 1, 0), 5.0)
               , (datetime(2000, 1, 1, 5), 3.0)
               , (datetime(2000, 1, 1, 8), 4.0)
               ]
        ps = []
        state = first(Period_State.objects.filter(abbreviation = 'P'))
        for start, dur in times:
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            p = Period( session    = self.sesshun
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()
            ps.append(p)

        # now try and retrieve them from the DB:
        # get them all
        dt1 = datetime(2000, 1, 1, 0)
        dur = 12 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps)

        # get them all because the first overlaps
        dt1 = datetime(2000, 1, 1, 1)
        dur = 12 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps)

        # now leave out the first
        dt1 = datetime(2000, 1, 1, 5)
        dur = 12 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps[1:])

        # keep getting the last one too
        dt1 = datetime(2000, 1, 1, 5)
        dur = 6 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps[1:])

        # now just get the middle one
        dt1 = datetime(2000, 1, 1, 5)
        dur = 3 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, [ps[1]])

        # again, just the middle one
        dt1 = datetime(2000, 1, 1, 6)
        dur = 2 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, [ps[1]])

        # cleanup
        for p in ps:
            p.delete()

    def test_has_required_receivers(self):
        p = Period.create(session = self.sesshun
                        , start = datetime(2009, 11, 1)
                        , duration = 10.0
                        )

        # No receivers for the session yet.
        self.assertEquals(False, p.has_required_receivers())

        # Make sure the sesshun has some rcvrs
        SessionHttpAdapter(self.sesshun).save_receivers("S")

        # No schedule yet.
        self.assertEquals(False, p.has_required_receivers())

        # Make a schedule.
        rs = Receiver_Schedule()
        rs.start_date = p.start
        rs.receiver   = Receiver.objects.filter(abbreviation = "L")[0]
        rs.save()

        # Receiver still not up on schedule yet.
        self.assertEquals(False, p.has_required_receivers())

        # Make sure the sesshun has a receiver on the schedule.
        rg = Receiver_Group.objects.filter(session = self.sesshun)[0]
        rg.delete()
        SessionHttpAdapter(self.sesshun).save_receivers("L")

        # Receiver now on schedule.
        self.assertEquals(True, p.has_required_receivers())

    def test_has_observed_rcvrs_in_schedule(self):
        p = Period.create(session = self.sesshun
                        , start = datetime(2009, 11, 1)
                        , duration = 10.0
                        )

        # No receivers for the session yet.
        self.assertEquals(False, p.has_observed_rcvrs_in_schedule())

        # Make sure the period has some rcvrs
        #self.sesshun.save_receivers("S")
        adapter = PeriodHttpAdapter(p)
        adapter.update_rcvrs_from_post({"receivers" : "S"})

        # No schedule yet.
        self.assertEquals(False, p.has_observed_rcvrs_in_schedule())

        # Make a schedule.
        rs = Receiver_Schedule()
        rs.start_date = p.start
        rs.receiver   = Receiver.objects.filter(abbreviation = "L")[0]
        rs.save()

        # Receiver still not up on schedule yet.
        self.assertEquals(False, p.has_observed_rcvrs_in_schedule())

        # Make sure the period observed w/ a receiver on the schedule.
        #rg = Receiver_Group.objects.filter(session = self.sesshun)[0]
        #rg.delete()
        #self.sesshun.save_receivers("L")
        adapter.update_rcvrs_from_post({"receivers" : "L"})

        # Receiver now on schedule.
        self.assertEquals(True, p.has_observed_rcvrs_in_schedule())

        # now insist that the period observed w/ two rcvrs, one of which
        # was *not* on the schedule - should return false
        adapter.update_rcvrs_from_post({"receivers" : "L, S"})
        self.assertEquals(False, p.has_observed_rcvrs_in_schedule())

