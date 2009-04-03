from datetime           import datetime, timedelta
from django.test.client import Client
import simplejson as json

from sesshuns.models                     import *
from server.test_utils.NellTestCase import NellTestCase

##################
# Testing models #
##################

# Test field data
fdata = {"total_time": "3"
       , "req_max": "6"
       , "name": "Low Frequency With No RFI"
       , "grade": "4"
       , "science": "pulsar"
       , "orig_ID": "0"
       , "between": "0"
       , "proj_code": "GBT09A-001"
       , "PSC_time": "2"
       , "sem_time": 0.0
       , "req_min": "2"
       , "freq": "6"
       , "type": "open"
       , "source" : "blah"
         }

def create_sesshun():
    "Utility method for creating a Sesshun to test."

    s = Sesshun()
    s.set_base_fields(fdata)
    allot = Allotment(psc_time          = fdata.get("PSC_time", 0.0)
                    , total_time        = fdata.get("total_time", 0.0)
                    , max_semester_time = fdata.get("sem_time", 0.0)
                      )
    allot.save()
    s.allotment        = allot
    s.save()
    return s


class TestSesshun(NellTestCase):
    def setUp(self):
        super(TestSesshun, self).setUp()
        self.sesshun = create_sesshun()

    def test_create(self):
        expected = first(Sesshun.objects.filter(id = self.sesshun.id))
        self.assertEqual(expected.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(expected.name, fdata["name"])

    def test_init_from_post(self):
        s = Sesshun()
        s.init_from_post(fdata)
        
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])

class TestWindow(NellTestCase):

    def test_create(self):
        w = Window(session = create_sesshun(), required = True)
        w.save()

        expected = first(Window.objects.filter(id = w.id))
        self.assertTrue(expected.required)

##########################
# Testing View Resources #
##########################

class TestSessionResource(NellTestCase):

    def setUp(self):
        super(TestSessionResource, self).setUp()
        self.client = Client()
        s = Sesshun()
        s.init_from_post({})
        s.save()

    def test_create(self):
        response = self.client.post('/sessions')
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        response = self.client.get('/sessions')
        self.failUnlessEqual(response.status_code, 200)

    def test_update(self):
        response = self.client.post('/sessions/1', {'_method' : 'put'})
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('/sessions/1', {'_method' : 'delete'})
        self.failUnlessEqual(response.status_code, 200)
    
class TestWindowResource(NellTestCase):

    def setUp(self):
        super(TestWindowResource, self).setUp()
        self.client = Client()
        s = Sesshun()
        s.init_from_post({})
        s.save()

    def test_create(self):
        num_opps = 4
        starts = [datetime(2009, 4, 1, 12) + timedelta(days = d) for d in range(num_opps)]
        fdata = {"session_id" : "1"
               , "start_time" : map(str, starts)
               , "duration"   : [1 + i for i in range(len(starts))]
                 }
        response = self.client.post('/windows', fdata)

        expected = json.dumps({"required": False
                             , "id": 1
                             , "opportunities": [{"duration": 1.0
                                                , "start_time": "2009-04-01 12:00:00"
                                                , "id": 1}
                                               , {"duration": 2.0
                                                , "start_time": "2009-04-02 12:00:00"
                                                , "id": 2}
                                               , {"duration": 3.0
                                                , "start_time": "2009-04-03 12:00:00"
                                                , "id": 3}
                                               , {"duration": 4.0
                                                , "start_time": "2009-04-04 12:00:00"
                                                , "id": 4}]})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(expected, response.content)

    def test_read(self):
        response = self.client.get('/windows')
        self.failUnlessEqual(response.status_code, 200)

    def test_update(self):
        s = first(Sesshun.objects.all())
        w = Window(session = s)
        w.init_from_post()

        num_opps = 4
        starts = [datetime(2009, 4, 10, 12) + timedelta(days = d) for d in range(num_opps)]
        fdata = {"session_id" : "1"
               , "start_time" : map(str, starts)
               , "duration"   : [1 + i for i in range(len(starts))]
                 }
        fdata.update({'_method' : 'put'})
        response = self.client.post('/windows/%i' % w.id
                                  , fdata)

        self.failUnlessEqual(response.status_code, 200)

        expected = first(w.opportunity_set.all()).start_time
        self.assertEqual(expected, datetime(2009, 4, 10, 12))


    def test_delete(self):
        s = first(Sesshun.objects.all())
        w = Window(session = s)
        w.init_from_post()

        response = self.client.post('/windows/%i' % w.id, {'_method' : 'delete'})
        self.failUnlessEqual(response.status_code, 200)

        # Make sure that deleting the window deletes all opportunities
        opps = Opportunity.objects.filter(window = w)
        self.failUnlessEqual(len(opps), 0)

        
    
