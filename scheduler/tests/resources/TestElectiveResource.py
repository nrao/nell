from django.test.client  import Client
from datetime                   import datetime, timedelta

from test_utils              import BenchTestCase, timeIt
from scheduler.tests.utils    import create_sesshun
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestElectiveResource(BenchTestCase):

    def setUp(self):
        super(TestElectiveResource, self).setUp()
        self.client = Client()
        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("elective")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        dur = 5.0
        self.deleted   = Period_State.get_state("D")
        self.pending   = Period_State.get_state("P")
        self.scheduled = Period_State.get_state("S")

        # create an elective to group the periods by
        self.elec = Elective(session = self.sesshun, complete = False)
        self.elec.save()
        
        # create 3 periods separated by a week
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period1 = Period(session = self.sesshun
                            , start = dt 
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period1.save()    

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period2 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 7)
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period2.save() 

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period3 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 2*7)
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period3.save() 

        self.fdata = {"session":  self.sesshun.id
                    , "true":    "false" }

    def tearDown(self):
        super(TestElectiveResource, self).tearDown()

    @timeIt
    def test_create(self):
        response = self.client.post('/scheduler/electives', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_empty(self):
        response = self.client.post('/scheduler/electives')
        self.failUnlessEqual(response.status_code, 200)

    def test_read_one(self):
        response = self.client.get('/scheduler/electives/%d' % self.elec.id)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"complete": false' in response.content)

    def test_read_filter(self):
        response = self.client.get('/scheduler/electives'
                                , {'filterSession' : self.sesshun.name})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(self.sesshun.name in response.content)

        response = self.client.get('/scheduler/electives'
                                , {'filterSession' : "not_there"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('{"total": 0, "electives": []}' in response.content)

    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('/scheduler/electives/%s' % self.elec.id, fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('/scheduler/electives/%s' % self.elec.id, {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)
        

