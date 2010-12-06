from test_utils.NellTestCase import NellTestCase
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestWindow(NellTestCase):

    def setUp(self):
        super(TestWindow, self).setUp()

        self.deleted   = Period_State.get_state("D")
        self.pending   = Period_State.get_state("P")
        self.scheduled = Period_State.get_state("S")


        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("windowed")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        #pending = first(Period_State.objects.filter(abbreviation = "P"))
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.default_period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = self.pending
                                   , accounting = pa
                                   )
        self.default_period.save()    

        start = datetime(2009, 6, 1)
        dur   = 7 # days
        
        # create window
        self.w = Window()
        #self.w.start_date = start
        #self.w.duration = dur
        self.w.session = self.sesshun
        self.w.total_time = self.default_period.duration
        self.w.save()
        wr = WindowRange(window = self.w
                       , start_date = start
                       , duration = dur
                        )
        wr.save()                

        # window & default period must both ref. eachother
        self.w.default_period = self.default_period
        self.w.save()
        self.default_period.window = self.w
        self.default_period.save()
        self.w_id = self.w.id

        # a chosen period
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        dt = self.default_period.start - timedelta(days = 2)
        self.period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = self.pending
                                   , accounting = pa
                                   )
        self.period.save()    

        pjson = PeriodHttpAdapter(self.default_period).jsondict('UTC', 1.1)
        self.fdata = {"session":  1
                    #, "start":    "2009-06-01"
                    #, "duration": 7
                    , "num_periods": 0
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
        #self.assertEqual(w.start_date(), date(2009, 6, 1))
        #self.assertEqual(w.duration(), self.fdata["duration"])
        self.assertEqual(w.default_period, None)
        self.assertEqual(len(w.periods.all()), 0)

    def test_jsondict(self):
         
        start = datetime(2009, 6, 1)
        startStr = start.strftime("%Y-%m-%d")
        dur   = 7 # days
        end = start + timedelta(days = dur - 1)
        endStr = end.strftime("%Y-%m-%d")
        
        w = Window()
        #w.start_date = start
        #w.duration = dur
        w.session = self.sesshun
        w.default_period = self.default_period

        w.save()

        wr = WindowRange(window = w
                       , start_date = start
                       , duration = dur
                        )
        wr.save()

        self.default_period.window = w
        self.default_period.save()

        adapter = WindowHttpAdapter(w)

        jd = adapter.jsondict()

        self.assertEqual(jd["duration"], dur)
        self.assertEqual(jd["start"], startStr)
        self.assertEqual(jd["end"], endStr)
        # session dict just blots this, so we're not using it
        #self.assertEqual(jd["session"], SessionHttpAdapter(self.sesshun).jsondict())
        self.assertEqual(jd["num_periods"], 1)
        self.assertEqual(len(jd["periods"]), 1)

        w.delete()

    def test_publish(self):

        # test - get it fresh from the DB
        w = Window.objects.get(id = self.w_id)
        self.assertEquals(w.default_period.state, self.pending) 
        self.assertTrue(len(w.periods.all()) == 1)
        self.assertEquals(w.periods.all()[0].state, self.pending) 

        # this should move the default_period to scheduled
        # Calling this method will trigger it, but we 
        # are trying to test window.publish, so don't call it
        self.default_period.state = self.scheduled
        self.default_period.save()
        self.default_period.accounting.scheduled = \
            self.default_period.duration
        self.default_period.accounting.save()

        # test
        w = Window.objects.get(id = self.w_id)
        w.publish()

        # get it fresh from the DB
        w = first(Window.objects.filter(id = self.w_id)) 
        self.assertEquals(w.default_period.state, self.scheduled) 
        self.assertTrue(len(w.periods.all()) == 1)
        self.assertEquals(w.periodStates(), [self.scheduled]) 
        self.assertEquals(w.periods.all()[0].id, w.default_period.id) 

    def test_publish_2(self):

        # attach both periods to this window
        self.period.window = self.w
        self.period.save()

        # test
        self.assertEquals(self.w.default_period.state, self.pending) 
        self.assertEquals(self.w.periodStates(), [self.pending, self.pending]) 
        #self.assertEquals(w.state(), self.pending) 

        # this should move the default_period to deleted
        # and the chosen period to scheduled
        self.period.state = self.scheduled
        self.period.save()
        self.period.accounting.scheduled = self.period.duration 
        self.period.accounting.save()

        w = Window.objects.get(id = self.w_id)
        w.publish()

        # test
        # get it fresh from the DB
        w = first(Window.objects.filter(id = self.w_id)) 
        self.assertEquals(w.default_period.state, self.deleted) 
        self.assertTrue(len(w.periods.all()) == 2)
        self.assertEquals(w.periodStates(), [self.scheduled, self.deleted]) 
        #self.assertEquals(w.state(), self.scheduled) 

    def test_setComplete(self):

        # The chosen period was scheduled
        # Don't USE publish method here!
        self.period.state = self.scheduled
        self.period.save()
        self.period.accounting.scheduled = self.period.duration
        self.period.accounting.save()

        # the default was deleted
        self.default_period.state = self.deleted
        self.default_period.save()

        self.period.window = self.w
        self.period.save()

        w = Window.objects.get(id = self.w_id)
 
        # now make sure it makes sense
        self.assertEquals(0.0, w.timeRemaining())
 
        # now fake some time accounting
        lost_time = 2.0
        self.period.accounting.lost_time_other = lost_time
        self.period.accounting.save()

        w = Window.objects.get(id = self.w_id)
        w.complete = True
        #print w, w.complete, w.timeRemaining()

        # test
        w.setComplete(False)
        
        self.assertEquals(False, w.complete)
        self.assertEquals(self.pending, w.default_period.state)
        self.assertEquals(lost_time, w.default_period.duration)
        self.assertEquals(lost_time, w.timeRemaining())

    def test_getWindowTimeBlackedOut(self):

        print self.w.getWindowTimeBlackedOut()
        # make blackout that overlaps this window
        # start = datetime(2009, 6, 1)
        # dur   = 7 # days
        blackout = Blackout(project    = self.w.session.project
                          , start_date = datetime(2009, 5, 30) 
                          , end_date   = datetime(2009, 6, 3)
                          , repeat     = first(Repeat.objects.all())
                           )
        blackout.save()                           
        
        print self.w.getWindowTimeBlackedOut()

