from datetime                import datetime, timedelta, date
from utilities               import TimeAgent
from test_utils              import NellTestCase
from utils                   import create_sesshun
from scheduler.models         import *
from scheduler.httpadapters   import *

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
        self.wr1 = wr

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

    def test_times(self):
        "Test all the methods that describe the window ranges."

        # the window created in setup is pretty vanilla
        self.assertEquals(True, self.w.isContigious())
        self.assertEquals(date(2009, 6, 1), self.w.start())
        self.assertEquals(date(2009, 6, 1), self.w.start_date())
        self.assertEquals(datetime(2009, 6, 1), self.w.start_datetime())
        
        self.assertEquals(date(2009, 6, 7), self.w.last_date())
        self.assertEquals(date(2009, 6, 7), self.w.end())
        self.assertEquals(datetime(2009, 6, 7, 23, 59, 59), self.w.end_datetime())

        self.assertEquals(7, self.w.duration())

        p = Period(session = self.sesshun
                 , start = datetime(2009, 5, 30, 23)
                 , duration = 2)
        p.save()

        self.assertEquals(False, self.w.isInWindow(p))
        self.assertEquals(False, self.w.isInRanges(p))

        p.start = p.start + timedelta(days = 1)
        p.save()
        self.assertEquals(True, self.w.isInWindow(p))
        self.assertEquals(True, self.w.isInRanges(p))

        p.start = datetime(2009, 6, 7, 23) 
        p.save()
        self.assertEquals(True, self.w.isInWindow(p))
        self.assertEquals(True, self.w.isInRanges(p))

        p.start = p.start + timedelta(days = 1)
        p.save()
        self.assertEquals(False, self.w.isInWindow(p))
        self.assertEquals(False, self.w.isInRanges(p))

        # now give it another range
        wr = WindowRange(window = self.w
                       , start_date = date(2009, 6, 15)
                       , duration = 7 # days
                         )
        wr.save()

        self.w = Window.objects.get(id = self.w.id)
        self.assertEquals(False, self.w.isContigious())
        self.assertEquals(date(2009, 6, 1), self.w.start())
        self.assertEquals(date(2009, 6, 1), self.w.start_date())
        self.assertEquals(datetime(2009, 6, 1), self.w.start_datetime())
        
        self.assertEquals(date(2009, 6, 21), self.w.last_date())
        self.assertEquals(date(2009, 6, 21), self.w.end())
        self.assertEquals(datetime(2009, 6, 21, 23, 59, 59), self.w.end_datetime())

        self.assertEquals(21, self.w.duration())

        p = Period(session = self.sesshun
                 , start = datetime(2009, 5, 30, 23)
                 , duration = 2)
        p.save()

        self.assertEquals(False, self.w.isInWindow(p))
        self.assertEquals(False, self.w.isInRanges(p))

        p.start = p.start + timedelta(days = 1)
        p.save()
        self.assertEquals(True, self.w.isInWindow(p))
        self.assertEquals(True, self.w.isInRanges(p))

        p.start = datetime(2009, 6, 7, 23) 
        p.save()
        self.assertEquals(True, self.w.isInWindow(p))
        self.assertEquals(True, self.w.isInRanges(p))

        p.start = p.start + timedelta(days = 1)
        p.save()
        # note the difference here between isInWindow and isInRanges
        # the period falls between the window's endpoints, but is in 
        # the gap between the window ranges.
        self.assertEquals(True, self.w.isInWindow(p))
        self.assertEquals(False, self.w.isInRanges(p))

    def test_update_from_post(self):
        w = Window()
        adapter = WindowHttpAdapter(w)
        adapter.init_from_post(self.fdata)
       
        self.assertEqual(w.session, self.sesshun)
        self.assertEqual(w.default_period, None)
        self.assertEqual(len(w.periods.all()), 0)

    def test_jsondict(self):
         
        wins = Window.objects.all()
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
        # session dict just bloats this, so we're not using it
        #self.assertEqual(jd["session"], SessionHttpAdapter(self.sesshun).jsondict())
        self.assertEqual(jd["num_periods"], 1)
        self.assertEqual(len(jd["periods"]), 1)
        errors = ['Window is overlapping with window ID(s): 1'] 
        self.assertEqual(jd['errors'], errors)

        # now move the window out of the way
        origW = Window.objects.get(id = 1)
        wr.start_date = origW.last_date() + timedelta(days = 1) #origW.end_datetime()

        wr.save()
        self.default_period.start = wr.start_date + timedelta(days = 3) 
        self.default_period.save()
        adapter = WindowHttpAdapter(w)
        jd = adapter.jsondict()
        self.assertEqual(jd['errors'], ['Window is within 2 days of window ID(s): 1'])

        # oops, apparently that's not far enough away
        wr.start_date = origW.last_date() + timedelta(days = 3) 

        wr.save()
        adapter = WindowHttpAdapter(w)
        jd = adapter.jsondict()
        self.assertEqual(jd['errors'], [])

        # now get the period out of range
        self.default_period.start = datetime(2008, 6, 1)
        self.default_period.save()
        
        adapter = WindowHttpAdapter(w)
        jd = adapter.jsondict()
        errors = ['Window has out of range Period(s): 2008-06-01 00:00:00 for  5.00']
        self.assertEqual(jd['errors'], errors)

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

        # test
        w.setComplete(False)
        
        self.assertEquals(False, w.complete)
        self.assertEquals(self.pending, w.default_period.state)
        self.assertEquals(lost_time, w.default_period.duration)
        self.assertEquals(lost_time, w.timeRemaining())

   
    def test_getWindowTimeBlackedOut(self):

        bHrs = self.w.getWindowTimeBlackedOut()
        self.assertEquals(0.0, bHrs)

        # make blackout that overlaps this window
        # start = datetime(2009, 6, 1)
        # dur   = 7 # days
        blackout = Blackout(project    = self.w.session.project
                          , start_date = datetime(2009, 6, 3) 
                          , end_date   = datetime(2009, 6, 4)
                          , repeat     = first(Repeat.objects.all())
                           )
        blackout.save()                           
        
        # and another that doesn't
        blackout = Blackout(project    = self.w.session.project
                          , start_date = datetime(2009, 6, 8, 12) 
                          , end_date   = datetime(2009, 6, 9, 12)
                          , repeat     = first(Repeat.objects.all())
                           )
        blackout.save()           

        bHrs = self.w.getWindowTimeBlackedOut()
        self.assertEquals(24.0, bHrs)

        # now extend this window and make it non-contigious
        # and see how the new blackouts *dont* picked up.
        wr = WindowRange(window = self.w
                       , start_date = datetime(2009, 6, 10)
                       , duration = 2)
        wr.save()

        # the second window range misses the second blackout out
        # But it needs to be fresh from the DB
        w = Window.objects.get(id = self.w.id)

        bHrs = w.getWindowTimeBlackedOut()
        self.assertEquals(24.0, bHrs)

    def test_lstOutOfRange(self):

        tg = first(self.sesshun.target_set.all())
        # ra to lst: rads to hours
        lst = TimeAgent.rad2hr(tg.horizontal)

        # this first window should not have a problem, since
        # duration > 1 day
        self.assertEquals(False, self.w.hasLstOutOfRange())
        self.assertEquals(False, self.w.hasNoLstInRange())

        # now create a one day window range
        utcStart = datetime(2009, 6, 1)
        utcEnd   = datetime(2009, 6, 2)
        wr = WindowRange(window = self.w
                       , start_date = utcStart
                       , duration = (utcEnd - utcStart).days)
        wr.save()

        # any target should be in range, w/ out a big buffer
        self.assertEquals(False, self.w.hasLstOutOfRange())
        self.assertEquals(False, self.w.hasNoLstInRange())

        # now, increase the buffer:
        self.sesshun.min_duration = 12.0
        self.sesshunmax_duration  = 12.0
        self.sesshun.save()
        self.assertEquals(True, self.w.hasLstOutOfRange())
        self.assertEquals([wr], self.w.lstOutOfRange())
        self.assertEquals(False, self.w.hasNoLstInRange())

        # now, shrink the original window range so that it 
        # is too small as well
        self.wr1.duration = 1
        self.wr1.save()
        self.assertEquals(True, self.w.hasLstOutOfRange())
        self.assertEquals(True, self.w.hasNoLstInRange())

    def test_overlappingRanges(self):

        # our original window has only one window range
        self.assertEquals(False, self.w.hasOverlappingRanges())

        # add one that doesn't overlap
        wr2 = WindowRange(window = self.w
                        , start_date = self.wr1.last_date() + timedelta(days = 2)
                        , duration = 7)
        wr2.save()

        self.assertEquals(False, self.w.hasOverlappingRanges())

        # now make them overlap
        wr2.start_date = self.wr1.last_date() - timedelta(days = 1) 
        wr2.save()

        self.assertEquals(True, self.w.hasOverlappingRanges())

        # contigious windows shouldn't overrlap
        wr2.start_date = self.wr1.last_date() + timedelta(days = 1)
        wr2.save()

        self.assertEquals(False, self.w.hasOverlappingRanges())

    def test_overlappingWindows(self):


        # of course there are none, right now there's only 1 window
        self.assertEquals([], self.w.overlappingWindows())

        # create a second one
        w2 = Window(session = self.sesshun)
        w2.save()
        wr2 = WindowRange(window = w2
                       , start_date = self.w.start()
                       , duration = self.w.duration()
                        )
        wr2.save()

        # it had better overlap!
        self.assertEquals([2], sorted([w.id for w in self.w.overlappingWindows()]))
        self.assertEquals([1], sorted([w.id for w in w2.overlappingWindows()]))

        # move it well out of range
        wr2.start_date = self.w.end() + timedelta(days = 1)
        wr2.save()
        w2 = Window.objects.get(id = w2.id)
        self.assertEquals([], sorted([w.id for w in self.w.overlappingWindows()]))
        self.assertEquals([], sorted([w.id for w in w2.overlappingWindows()]))

        # test the boundary condition:
        # A window's end() or last_date() is it's last day where a period
        # is still in the window.
        # Thus if another window start's on that last date, they overlap
        wr2.start_date = self.w.end() 
        wr2.save()
        w2 = Window.objects.get(id = w2.id)
        self.assertEquals([2], sorted([w.id for w in self.w.overlappingWindows()]))
        self.assertEquals([1], sorted([w.id for w in w2.overlappingWindows()]))

