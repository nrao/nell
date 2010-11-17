from django.test.client  import Client

from test_utils.NellTestCase import NellTestCase
from sesshuns.httpadapters   import SessionHttpAdapter
from sesshuns.models         import *

class TestSessionResource(NellTestCase):

    def setUp(self):
        super(TestSessionResource, self).setUp()
        self.client = Client()
        s = Sesshun()
        SessionHttpAdapter(s).init_from_post({})
        s.save()
        self.s = s

    def test_create(self):
        response = self.client.post('/sessions')
        self.failUnlessEqual(response.status_code, 200)

    def test_create2(self):
        fdata = {'req_max': ['6.0']
               , 'grade': ['4.0']
               , 'req_min': ['2.0']
               , 'sem_time': ['1.0']
               , 'id': ['0']
               , 'source': ['1']
               , 'authorized': ['true']
               , 'between': ['0.0']
               , 'type': ['open']
               , 'total_time': ['1.0']
               , 'coord_mode': ['J2000']
               , 'complete': ['false']
               , 'source_h': ['1']
               , 'source_v': ['1']
               , 'PSC_time': ['1.0']
               , 'freq': ['1.0']
               , 'name': ['All Fields']
               , 'science': ['pulsar']
               , 'orig_ID': ['0']
               , 'enabled': ['false']
               , 'receiver': ['(K | Ka) | Q']
               , 'backup': ['false']
                 }

        response = self.client.post('/sessions', fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        response = self.client.get('/sessions')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/sessions', {'limit'     : 50
                                               , 'sortField' : 'null'
                                               , 'sortDir'   : 'NONE'
                                               , 'offset'    : 0
                                                 })
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/sessions', {'limit'     : 50
                                               , 'sortField' : 'null'
                                               , 'sortDir'   : 'NONE'
                                               , 'offset'    : 0
                                               , 'filterType': "Open"
                                               , 'filterFreq': "20"
                                               , 'filterClp' : "True"
                                                 })
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("windowed" not in response.content)

    def test_read_one(self):
        response = self.client.get('/sessions/%s' % self.s.id)
        self.failUnlessEqual(response.status_code, 200)

        r_json = json.loads(response.content)
        self.assertEqual(0.0, r_json["session"]["total_time"])

    def test_update(self):

        response = self.client.post('/sessions/1', {'_method' : 'put'})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(True, s.gaurenteed())

        response = self.client.post('/sessions/1', {'_method' : 'put'
                                                  , 'gaurenteed' : ['true']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(True, s.gaurenteed())

        response = self.client.post('/sessions/1', {'_method' : 'put'
                                                  , 'gaurenteed' : ['false']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(False, s.gaurenteed())

        response = self.client.post('/sessions/1', {'_method' : 'put'
                                                  , 'gaurenteed' : ['true']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(True, s.gaurenteed())

    def test_delete(self):
        response = self.client.post('/sessions/1', {'_method' : 'delete'})
        self.failUnlessEqual(response.status_code, 200)

    def test_create_rcvr(self):
        response = self.client.post('/sessions', {'receiver' : 'L'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        self.assertEquals(r_json['receiver'], 'L')

    def test_create_rcvrs(self):   # TBF hold until handles multiple rcvrs
        response = self.client.post('/sessions',
                                    {'receiver' : 'K & (L | S)'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        # Next two lines are logically equivalent
        #self.assertEquals(r_json['receiver'], u'(K) & (L | S)')
        self.assertEquals(r_json['receiver'], u'(K & (L | S))')
        # etc
        response = self.client.post('/sessions',
                                    {'receiver' : 'Ka | (342 & S)'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        # Next two lines are logically equivalent
        #self.assertEquals(r_json['receiver'], u'(342 | Ka) & (S | Ka)')
        self.assertEquals(r_json['receiver'], u'((342 | Ka) & (S | Ka))')
