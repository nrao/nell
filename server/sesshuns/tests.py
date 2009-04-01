from django.test.client import Client

from sesshuns.models                     import *
from server.test_utils.NellTestCase import NellTestCase

class TestSesshun(NellTestCase):

    def test_create(self):
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
                }
        s = Sesshun()
        s.init_from_json(fdata)
        s.save()
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.name, fdata["name"])

class TestSessionResource(NellTestCase):

    def setUp(self):
        
        super(TestSessionResource, self).setUp()
        self.client = Client()
        s = Sesshun()
        s.init_from_json({})
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
    
