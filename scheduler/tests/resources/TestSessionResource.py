from django.test.client  import Client
import simplejson as json

from test_utils              import BenchTestCase, timeIt
from scheduler.httpadapters   import SessionHttpAdapter
from scheduler.models         import *

class TestSessionResource(BenchTestCase):

    def setUp(self):
        super(TestSessionResource, self).setUp()
        self.client = Client()
        s = Sesshun()
        SessionHttpAdapter(s).init_from_post({})
        s.save()
        self.s = s

    @timeIt
    def test_create(self):
        response = self.client.post('/scheduler/sessions')
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

        response = self.client.post('/scheduler/sessions', fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        response = self.client.get('/scheduler/sessions')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/scheduler/sessions', {'limit'     : 50
                                               , 'sortField' : 'null'
                                               , 'sortDir'   : 'NONE'
                                               , 'offset'    : 0
                                                 })
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/scheduler/sessions', {'limit'     : 50
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
        response = self.client.get('/scheduler/sessions/%s' % self.s.id)
        self.failUnlessEqual(response.status_code, 200)

        r_json = json.loads(response.content)
        self.assertEqual(0.0, r_json["session"]["total_time"])

    def test_read_not_found(self):
        response = self.client.get('/scheduler/sessions/4000')
        self.failUnlessEqual(response.status_code, 404)

    @timeIt
    def test_update(self):

        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(True, s.guaranteed())

        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'guaranteed' : ['true']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(True, s.guaranteed())

        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'guaranteed' : ['false']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(False, s.guaranteed())

        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'guaranteed' : ['true']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        self.assertEquals(True, s.guaranteed())

    def test_update_lst_exclude(self):
        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'lst_ex' : ['2.0-4.0']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        exclude = [op.float_value 
          for op in s.observing_parameter_set.filter(parameter__name__contains = 'LST Exclude')]
        self.assertEqual(exclude, [2.0, 4.0])

        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'lst_ex' : ['2.0-4.0, 6.0-10.0']})
        self.failUnlessEqual(response.status_code, 200)
        s = Sesshun.objects.get(id = 1)
        exclude = [op.float_value 
          for op in s.observing_parameter_set.filter(parameter__name__contains = 'LST Exclude')]
        self.assertEqual(exclude, [2.0, 6.0, 4.0, 10.0])

    def test_update_does_not_exist(self):
        response = self.client.post('/scheduler/sessions/1000', {'_method' : 'put'})
        self.failUnlessEqual(response.status_code, 404)

    def test_update_bad_receivers(self):
        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'receiver' : ['X $ L']})
        self.assertTrue('SyntaxError: F1: missing right paren: $' in response.content)
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post('/scheduler/sessions/1', {'_method' : 'put'
                                                  , 'receiver' : ['X & Y']})
        self.assertTrue('ValueError: Y not a receiver' in response.content)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_delete(self):
        response = self.client.post('/scheduler/sessions/1', {'_method' : 'delete'})
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_rcvr(self):
        response = self.client.post('/scheduler/sessions', {'receiver' : 'L'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        self.assertEquals(r_json['receiver'], 'L')

    @timeIt
    def test_create_rcvrs(self):
        response = self.client.post('/scheduler/sessions',
                                    {'receiver' : 'K & (L | S)'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        # Next two lines are logically equivalent
        #self.assertEquals(r_json['receiver'], u'(K) & (L | S)')
        self.assertEquals(r_json['receiver'], u'(K & (L | S))')
        # etc
        response = self.client.post('/scheduler/sessions',
                                    {'receiver' : 'Ka | (342 & S)'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        # Next two lines are logically equivalent
        #self.assertEquals(r_json['receiver'], u'(342 | Ka) & (S | Ka)')
        self.assertEquals(r_json['receiver'], u'((342 | Ka) & (S | Ka))')
