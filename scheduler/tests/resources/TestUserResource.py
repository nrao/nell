from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from scheduler.models         import *
from scheduler.tests.utils    import create_users

class TestUserResource(BenchTestCase):

    def setUp(self):
        super(TestUserResource, self).setUp()
        self.client = Client()
        self.fdata = {
                      }
        self.users = create_users()

    @timeIt
    def test_create(self):
        fdata = self.fdata
        fdata.update({"original_id" : "99"
                    , "sanctioned" : "True"
                    , "first_name" : "Foogle"
                    , "last_name"  : "Bar"
                    , "contact_instructions" : "Best to call my mom's house.  Ask for Pooh Bear."
                    , "role": "Observer"
                    , "username": "dss" # in tests only
                     })
        response = self.client.post('/users', fdata)
        self.failUnlessEqual(response.status_code, 200)

        u = User.objects.get(original_id = fdata['original_id'])
        self.assertTrue(u is not None)

        response = self.client.post('/users', {})
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        response = self.client.get('/users')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 3' in response.content)

    def test_read_with_filter(self):
        response = self.client.get('/users?filterText=foo')
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 1' in response.content)

    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"
                    , "pst_id"  : "1"
                    , "original_id"  : "12"
                    , "sanctioned" : "True"
                    , "first_name" : "Foo"
                    , "last_name"  : "Bar"
                    , "contact_instructions" : ""
                    , "role": "Observer"
                    , "username": "dss" # in tests only
                     })
        response = self.client.post('/users/%s' % self.users[0].id, fdata)
        self.failUnlessEqual(response.status_code, 200)

