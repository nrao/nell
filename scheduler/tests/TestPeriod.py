from scheduler.httpadapters                 import *
from scheduler.models                       import *
from test_utils                            import BenchTestCase, timeIt
from utils                                 import *

class TestPeriod(BenchTestCase):

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

        self.deleted   = Period_State.get_state('D')
        self.pending   = Period_State.get_state('P')
        self.scheduled = Period_State.get_state('S')

        # create a window 
        self.sesshun.session_type = Session_Type.get_type("windowed")
        self.sesshun.save()
        start = datetime(2009, 6, 1, 12, 15)
        self.dur = 180
        wstart = (start - timedelta(days = 7)).date()
        self.w = Window(session = self.sesshun # = wstart
                 #, duration = 10 # days
                 #, session = self.sesshun
                 , total_time = self.dur
                 , complete = False
                 )
        self.w.save()         
        self.w_id = self.w.id
        wr = WindowRange(window = self.w
                       , start_date = wstart
                       , duration = 10 # days
                        )
        wr.save()                

        # create a period
        self.p = Period(start = start
                      , duration = self.dur
                      , session = self.sesshun
                      , state   = self.pending
                       )
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.p.accounting = pa
        self.p.save()
        self.p_id = self.p.id

        # assign the period to the window
        self.p.window = self.w
        self.p.save()
        # and make it the default
        self.w.default_period = self.p
        self.w.save()

        # create a second period         
        self.p2 = Period(start = start - timedelta(days = 2)
                       , duration = self.dur
                       , session = self.sesshun
                       , state = self.pending
                        )
        pa2 = Period_Accounting(scheduled = 0.0)
        pa2.save()
        self.p2.accounting = pa2
        self.p2.save()
        self.p2_id = self.p2.id

        # now assign this second period as a 'chosen' period for the win.
        self.p2.window = self.w
        self.p2.save()

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

    @timeIt
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

    @timeIt
    def test_publish_chosen_period(self):
        "test publishing the chosen period"

        # test
        self.assertEquals(True,  self.p2.is_windowed())
        self.assertEquals(self.w,     self.p2.window)
        self.assertEquals(False, self.p2.is_windowed_default())

        # now publish!
        # this should move p2 to scheduled, and p to deleted (default)
        self.p2.publish()

        # get these periods fresh from db again
        p  = Period.objects.get(id = self.p_id)
        p2 = Period.objects.get(id = self.p2_id)
        w  = Window.objects.get(id = self.w_id)
        self.assertEquals(self.deleted, p.state)
        self.assertEquals(self.scheduled, p2.state)
        self.assertEquals(0.0, w.timeRemaining())
        self.assertEquals(True, w.complete)
        self.assertEquals([self.scheduled, self.deleted], w.periodStates())

        # cleanup
        p2.delete()
        p.delete()
        w.delete()

    @timeIt
    def test_publish_default_period(self):
        
        # initial tests
        self.assertEqual(self.dur, self.w.timeRemaining())
        self.assertEqual(False, self.w.complete)

        # first, delete the chosen period
        self.p2.move_to_deleted_state()

        # now get everything fresh from the DB, and publish
        dp = Period.objects.get(id = self.p_id)
        dp.publish()
        
        # get these periods fresh from db again
        #p  = Period.objects.get(id = self.p_id)
        p2 = Period.objects.get(id = self.p2_id)
        w  = Window.objects.get(id = self.w_id)
        self.assertEquals(self.deleted, p2.state)
        self.assertEquals(self.scheduled, dp.state)
        self.assertEquals(0.0, w.timeRemaining())
        self.assertEquals(True, w.complete)

    def test_publish_small_period(self):
        "Q: What happens when chosen period is < window time?"

        #A: the default periods should get shrunk, and window NOT sat.!

        # shrink the chosen period
        p2 = Period.objects.get(id = self.p2_id)
        timeLeft = 2*60
        p2.duration = p2.duration - timeLeft
        p2.save()

        # now publish it
        p2 = Period.objects.get(id = self.p2_id)
        p2.publish()

        p  = Period.objects.get(id = self.p_id)
        p2 = Period.objects.get(id = self.p2_id)
        w  = Window.objects.get(id = self.w_id)
        self.assertEquals(self.pending, p.state)
        self.assertEquals(timeLeft, p.duration)
        self.assertEquals(self.scheduled, p2.state)
        self.assertEquals(timeLeft, w.timeRemaining())
        self.assertEquals(False, w.complete)
        self.assertEquals([self.scheduled, self.pending], w.periodStates())

    @timeIt
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

    @timeIt
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

    @timeIt
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

