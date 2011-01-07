from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestProjectResource(BenchTestCase):

    def setUp(self):
        super(TestProjectResource, self).setUp()
        self.client = Client()
        self.fdata = {'semester'   : '09C'
                    , 'type'       : 'science'
                    , 'pcode'      : 'mike'
                    , 'name'       : 'mikes awesome project!'
                    , 'PSC_time'   : '100.0'
                    , 'total_time' : '100.0'
                    , 'sem_time'   : '50.0'
                      }
        self.p = Project()
        ProjectHttpAdapter(self.p).init_from_post(self.fdata)
        self.p.save()

    @timeIt
    def test_create(self):
        response = self.client.post('/projects', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_empty(self):
        response = self.client.post('/projects')
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_no_allotment(self):
        # Get copy of fdata in local scope to modify for the purposes
        # of this test.
        fdata = self.fdata.copy()
        fdata.update({'total_time' : ''
                    , 'PSC_time'   : ''
                    , 'sem_time'   : ''
                    , 'grade'      : ''
                      })

        response = self.client.post('/projects', fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        response = self.client.get('/projects')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 2' in response.content)

    def test_read_with_filter(self):
        response = self.client.get('/projects?filterText=09C')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 1' in response.content)
        self.assertTrue('09C' in response.content)
        self.assertTrue('09A' not in response.content)

    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('/projects/%s' % self.p.id, fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_delete(self):
        response = self.client.post('/projects/%s' % self.p.id, {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)


