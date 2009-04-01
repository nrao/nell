from django.test.client import Client

from sesshuns.models                     import *
from server.test_utils.NellTestCase import NellTestCase

class TestSesshun(NellTestCase):
    def setUp(self):
        self.fdata = {"total_time": "3"
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
        super(TestSesshun, self).setUp()

    def test_create(self):
        s = Sesshun()
        s.set_base_fields(self.fdata)
        allot = Allotment(psc_time          = self.fdata.get("PSC_time", 0.0)
                        , total_time        = self.fdata.get("total_time", 0.0)
                        , max_semester_time = self.fdata.get("sem_time", 0.0)
                          )
        allot.save()
        s.allotment        = allot
        s.save()

        expected = first(Sesshun.objects.filter(id = s.id))
        self.assertEqual(expected.allotment.total_time, float(self.fdata["total_time"]))
        self.assertEqual(expected.name, self.fdata["name"])

    def test_init_from_post(self):
        s = Sesshun()
        s.init_from_post(self.fdata)
        
        self.assertEqual(s.allotment.total_time, self.fdata["total_time"])
        self.assertEqual(s.target_set.get().source, self.fdata["source"])

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
    
