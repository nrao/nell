from django.test.client  import Client

from sesshuns.models         import *
from scheduler.models        import *
from test_utils              import timeIt
from PeriodsTestCase         import PeriodsTestCase
from scheduler.tests.utils                   import create_sesshun

class TestViewsPTC(PeriodsTestCase):

    def test_scheduling_email(self):

        # TBF: this is a dumb test, since email is always generated for NOW;
        # we need to create some periods for NOW to show up in the email
        url = "/schedule/email"
        response = Client().get(url, dict(duration = 2))

        self.failUnless(response.status_code == 200)

    def test_projects_email(self):
        pcodes = "GBT09A-001"

        url = "/projects/email"

        response = Client().get(url, dict(pcodes = pcodes))

        self.failUnless(response.status_code == 200)
        self.failUnless('"PCODES": ["GBT09A-001"]' in response.content)

        response = Client().get(url, {})
        self.failUnless(response.status_code == 200)
        self.failUnless('"PCODES": ["GBT09A-001"]' in response.content)

    @timeIt
    def test_delete_pending(self):

        # check current state
        ps = Period.objects.order_by("start")
        exp = ["S", "P", "S"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])
        exp = [5.0, 0.0, 4.0]
        self.assertEquals(exp, [p.accounting.scheduled for p in ps])

        # have to use the scheduling range
        dt = self.ps[0].start - timedelta(days = 1)
        time = dt.strftime("%Y-%m-%d %H:%M:%S")
        tz = "ET"
        duration = 2 #12
        url = "/periods/delete_pending"

        response = Client().post(url, dict(start    = time
                                         , tz       = tz
                                         , duration = duration
                                         ))
        self.failUnless("ok" in response.content)

        ps = Period.objects.order_by("start")
        exp = ["S", "S"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])
        exp = [5.0, 4.0]
        self.assertEquals(exp, [p.accounting.scheduled for p in ps])

    @timeIt
    def test_delete_pending_2(self):
        "Similar to previous test, but with a windowed session"

        # windowed session
        s = create_sesshun()
        s.name = "win"
        s.session_type = Session_Type.objects.get(type = "windowed")
        s.save()

        # a window that covers test scheduling range
        w = Window(session = s, total_time = 1.0)
        w.save()
        wstart = self.ps[0].start - timedelta(days = 3)
        wr = WindowRange(window = w
                       , start_date = wstart
                       , duration = 10 # days)
                         )
        wr.save()

        # a non-default period
        pending = Period_State.get_state("P")
        pa = Period_Accounting(scheduled = 0)
        pa.save()
        p1 = Period(session = s
                  , window = w
                  , start = datetime(2000, 1, 1, 12)
                  , duration = 1.0 # hr
                  , state = pending
                  , accounting = pa
                   )
        p1.save()

        # a default period
        pa = Period_Accounting(scheduled = 0)
        pa.save()
        p2 = Period(session = s
                  , window = w
                  , start = datetime(2000, 1, 1, 13)
                  , duration = 1.0 # hr
                  , state = pending
                  , accounting = pa
                   )
        p2.save()
        w.default_period = p2
        w.save()


        # have to use the scheduling range
        dt = self.ps[0].start - timedelta(days = 1)
        time = dt.strftime("%Y-%m-%d %H:%M:%S")
        tz = "ET"
        duration = 2 #12
        url = "/periods/delete_pending"

        response = Client().post(url, dict(start    = time
                                         , tz       = tz
                                         , duration = duration
                                         ))
        self.failUnless("ok" in response.content)

        # now, p1 should be gone, but p2 is still there
        ps = Period.objects.order_by("start")
        exp = ["S", "S", "P"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])
        exp = [5.0, 4.0, 0.0]
        self.assertEquals(exp, [p.accounting.scheduled for p in ps])
        self.assertEquals(p2.id, ps[2].id)


        
    @timeIt
    def test_publish_periods_by_id(self):
        # check current state
        ps = Period.objects.order_by("start")
        exp = ["S", "P", "S"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])
        exp = [5.0, 0.0, 4.0]
        self.assertEquals(exp, [p.accounting.scheduled for p in ps])

        time = self.ps[0].start.strftime("%Y-%m-%d %H:%M:%S")

        url = "/periods/publish/%d" % self.ps[1].id

        # Remember not to embarrass ourselves by tweeting! tweet == False
        response = Client().post(url, dict(tweet = False))
        self.failUnless("ok" in response.content)

        ps = Period.objects.order_by("start")
        exp = ["S", "S", "S"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])

    @timeIt
    def test_publish_periods(self):
        # check current state
        ps = Period.objects.order_by("start")
        exp = ["S", "P", "S"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])
        exp = [5.0, 0.0, 4.0]
        self.assertEquals(exp, [p.accounting.scheduled for p in ps])

        # have to use the scheduling range
        dt = self.ps[0].start - timedelta(days = 1)
        time = dt.strftime("%Y-%m-%d %H:%M:%S")
        tz = "ET"
        duration = 2 #12
        url = "/periods/publish"

        # Remember not to embarrass ourselves by tweeting! tweet == False
        response = Client().post(url, dict(start    = time
                                         , tz       = tz
                                         , duration = duration
                                         , tweet    = False))
        self.failUnless("ok" in response.content)

        ps = Period.objects.order_by("start")
        exp = ["S", "S", "S"]
        self.assertEquals(exp, [p.state.abbreviation for p in ps])
        exp = [5.0, 3.0, 4.0]
        self.assertEquals(exp, [p.accounting.scheduled for p in ps])

    @timeIt
    def test_publish_periods_with_windows(self):
        # Assign periods to our windows
        # 1 - scheduled -> window 1
        # 2 - pending -> window 2
        # 3 - scheduled -> window 2, make pending
        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")
        windowed  = Session_Type.objects.filter(type = "windowed")[0]

        p1 = self.ps[0]
        p1.session.session_type = windowed
        p1.session.save()

        w1 = Window( session = p1.session
                   #, start_date = p1.start.date() - timedelta(days = 7)
                   #, duration = 10 # days
                   , default_period = p1
                   )
        w1.save()
        wr = WindowRange(window = w1
                       , start_date = p1.start.date() - timedelta(days = 7)
                       , duration = 10 # days
                        )
        wr.save()                

        p1.window = w1
        p1.save()

        p2 = self.ps[1]
        p2.session.session_type = windowed
        p2.session.save()

        p3 = self.ps[2]
        p3.session.session_type = windowed
        p3.session.save()
        p3.state = pending
        p3.save()

        # NOTE: ovelapping windows for same session - shouldn't matter
        w2 = Window( session = p2.session # NOTE: same session for all 3 periods
                   #, start_date = p1.start.date() - timedelta(days = 7)
                   #, duration = 10 # days
                   , default_period = p2
                   )
        w2.save()
        wr = WindowRange(window = w2
                       , start_date = p1.start.date() - timedelta(days = 7)
                       , duration = 10 # days
                        )
        wr.save()                

        p3.window = w2
        p3.save()

        # check the states
        self.assertEquals([scheduled], w1.periodStates())
        self.assertEquals([pending],   w2.periodStates())

        # remeber that we publish using the scheduling range
        dt = w1.start_date() - timedelta(days = 1)
        time = dt.strftime("%Y-%m-%d %H:%M:%S")
        tz = "ET"
        duration = 13 #12
        url = "/periods/publish"

        # Remember not to embarrass ourselves by tweeting! tweet == False
        response = Client().post(url, dict(start    = time
                                         , tz       = tz
                                         , duration = duration
                                         , tweet    = False))
        self.failUnless("ok" in response.content)

        # make sure the states are right now
        #for w in Window.objects.order_by("start_date"):
        wins1 = Window.objects.all() # TBF: how to order????
        for w in wins1:
            self.assertEquals([scheduled], w.periodStates())

        # Put things back the way we found them.
        open = Session_Type.objects.filter(type = "open")[0]
        p1.session.session_type = open
        p1.session.save()
        p2.session.session_type = open
        p2.session.save()
        p3.session.session_type = open
        p3.session.save()

    @timeIt
    def test_period_time_accounting(self):

        # first see what the period looks like to start with 
        pid = Period.objects.all().order_by("id")[0].id
        url = "/periods/UTC/%d" % pid
        response = Client().get(url)
        self.assertTrue('"lost_time_bill_project": 0.0' in response.content)
        period = Period.objects.get(id = pid)
        self.assertEquals(period.accounting.lost_time_bill_project, 0.0)
        self.assertEquals(period.accounting.scheduled, 5.0)
        self.assertEquals(period.accounting.observed(), 5.0)

        # change the time accounting
        url = "/period/%d/time_accounting" % pid
        response = Client().post(url, {"lost_time_bill_project" : 1.0})
        self.assertTrue('"lost_time_bill_project": 1.0' in response.content)
        period = Period.objects.get(id = pid)
        self.assertEquals(period.accounting.lost_time_bill_project, 1.0)
        self.assertEquals(period.accounting.observed(), 5.0)


