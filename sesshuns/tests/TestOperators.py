from copy                      import copy
from django.test.client        import Client
from django.conf               import settings
from django.contrib.auth       import models as m
from datetime                  import datetime, timedelta

from test_utils                import BenchTestCase, timeIt
from scheduler.models           import *
from scheduler.httpadapters     import *
from utilities                  import TimeAgent
from scheduler.tests.utils                     import create_sesshun, fdata
from sesshuns.utilities        import create_user
from sesshuns.GBTCalendarEvent import CalEventPeriod
from TestObserversBase         import TestObserversBase

class TestOperators(TestObserversBase):

    def setUp(self):
        super(TestOperators, self).setUp()

        # setup some periods 
        self.start = datetime.utcnow() #datetime(2008, 1, 1)
        self.estStart = datetime.now()
        self.dur   = 4.0 # hrs
        self.periods = []
        for i in range(3):
            pa = Period_Accounting(scheduled = self.dur)
            pa.save()
            p = Period( session = self.s
                      , start = self.start + timedelta(hours = self.dur*i)
                      , duration = self.dur
                      , state = Period_State.get_state("S")
                      , accounting = pa
                      )
            p.save()          
            self.periods.append(p)

        # put some receivers up
        #d = datetime.now()
        for i in range(9):
            start_date = self.start + timedelta(5*i)
            for j in range(1,4):
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = i + j)
                rs.save()

    def test_remotely_qualified(self):
        response = self.get('/investigators/qualified')
        self.failUnlessEqual(response.status_code, 200)
        # nobody is qualifed for remote observing
        self.assertTrue("Observers Sanctioned for Remote Observing" in response.content)
        self.assertTrue("Friend" not in response.content)
        self.assertTrue("account" not in response.content)

    #def test_moc_reschedule(self):
    #    pass

    #def test_moc_degraded(self):
    #    pass

    def test_gbt_schedule(self):
        response = self.get('/schedule/')
        self.failUnlessEqual(response.status_code, 200)
        hdr = '<th title="Ordered list of observers to contact for this project">Observers</th>'
        # header appears no matter what
        self.assertTrue(hdr in response.content)
        # now make sure our periods show up there
        for i in range(len(self.periods)):
            startStr = datetime.strftime(self.estStart, "%H:%M")
            estEnd = self.estStart + timedelta(hours = self.dur)
            endStr = datetime.strftime(self.estStart, "%H:%M")
            self.assertTrue(startStr in response.content)
            self.assertTrue(endStr in response.content)
        self.assertTrue("mikes awesome project" in response.content)

    def test_rcvr_schedule(self):
        response = self.get('/receivers')
        self.failUnlessEqual(response.status_code, 200)
        # header appears no matter what
        self.assertTrue('<th class="grid" title="1.15 GHz - 1.73 GHz">L</th>' in response.content)
        # if *something* is available, this will appear
        self.assertTrue("available grid" in response.content)

    def test_summary(self):
        # setup a period for a month before
        lastMonth = self.start - timedelta(days = 30)
        lastMonthEst = TimeAgent.utc2est(lastMonth)
        pa = Period_Accounting(scheduled = self.dur)
        pa.save()
        p = Period( session = self.s
                  , start = lastMonth 
                  , duration = self.dur
                  , state = Period_State.get_state("S")
                  , accounting = pa
                  )
        p.save()          
        
        # get - sets up the form
        response = self.get('/schedule/summary')
        self.failUnlessEqual(response.status_code, 200)
        startStr = datetime.strftime(lastMonthEst, "%H:%M")
        self.assertTrue(startStr in response.content)
        self.assertTrue("mikes awesome project" in response.content)

        # post - they've requested something
        # first, the schedule summary report
        # default to last month
        response = self.post('/schedule/summary', {'summary' : 'schedule'})
        self.failUnlessEqual(response.status_code, 200)        
        self.assertTrue(startStr in response.content)
        self.assertTrue("mikes awesome project" in response.content)

        # now do an earlier month, and our period should not show up
        response = self.post('/schedule/summary'
                          , {'summary' : 'schedule'
                           , 'month'   : 'December'
                           , 'year'    : '2000'}
                            )
        self.failUnlessEqual(response.status_code, 200)        
        self.assertTrue(startStr not in response.content)
        self.assertTrue("mikes awesome project" not in response.content)

        # okay, now test the project summary report
        pcode = self.s.project.pcode
        response = self.post('/schedule/summary'
                          , {'summary' : 'project'
                           , 'project' : pcode}
                            )
        self.failUnlessEqual(response.status_code, 200)        
        self.assertTrue("GBT Project Summary for" in response.content)
        self.assertTrue(pcode in response.content)
        self.assertTrue(str(self.dur) in response.content)

        # make sure we can handle all projects 
        response = self.post('/schedule/summary'
                          , {'summary' : 'project'
                           , 'project' : None}
                            )
        self.failUnlessEqual(response.status_code, 200)        
        self.assertTrue("GBT Project Summary for" in response.content)
        self.assertTrue(pcode in response.content)
        self.assertTrue(str(self.dur) in response.content)
