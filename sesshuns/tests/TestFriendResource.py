from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from sesshuns.httpadapters   import *
from sesshuns.models         import *

class TestFriendResource(BenchTestCase):

    def setUp(self):
        super(TestFriendResource, self).setUp()
        self.client = Client()
        p_fdata = {'semester'   : '09C'
                 , 'type'       : 'science'
                 , 'pcode'      : 'mike'
                 , 'name'       : 'mikes awesome project!'
                 , 'PSC_time'   : '100.0'
                 , 'total_time' : '100.0'
                 , 'sem_time'   : '50.0'
                   }
        self.p = Project()
        p_adapter = ProjectHttpAdapter(self.p)
        p_adapter.init_from_post(p_fdata)
        self.p.save()

        self.users = []
        self.users.append(User(original_id = 0
                    , pst_id      = 0
                    , sanctioned  = False
                    , first_name  = 'Foo'
                    , last_name   = 'Bar'
                    , contact_instructions = ""
                    , role  = first(Role.objects.all())
                     ))
        self.users[-1].save()
        self.users.append(User(original_id = 0
                    , pst_id      = 0
                    , sanctioned  = True
                    , first_name  = 'Mike'
                    , last_name   = 'McCarty'
                    , contact_instructions = ""
                    , role  = first(Role.objects.all())
                     ))
        self.users[-1].save()
        self.users.append(User(original_id = 0
                    , pst_id      = 0
                    , sanctioned  = True
                    , first_name  = 'Doless'
                    , last_name   = 'NoProject'
                    , contact_instructions = ""
                    , role  = first(Role.objects.all())
                     ))
        self.users[-1].save()

        self.friends = []
        # first user is a friend to the project
        self.friends.append(Friend(project = self.p
                             , user        = self.users[0]
                                   ))
        self.friends[-1].save()
        # second user is also a friend to the project
        self.friends.append(Friend(project = self.p
                                   , user  = self.users[1]
                                   ))
        self.friends[-1].save()

        self.fdata = {'name'       : self.users[-1].last_name
                    , 'project_id' : self.p.id
                    , 'user_id'    : self.users[-1].id
                     }

    @timeIt
    def test_create(self):
        response = self.client.post('/friends'
                                  , self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_empty(self):
        response = self.client.post('/friends'
                                  , {'project_id' : self.p.id
                                   , 'user_id': self.users[-1].id})
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        response = self.client.get('/friends'
                                 , {'project_id' : self.p.id})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 2' in response.content)

    def test_read_with_filter(self):
        response = self.client.get(
              '/friends'
            , {'project_id' : self.p.id
            ,  'filterText' : 'Mike'
            })
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 1' in response.content)
        self.assertTrue('McCarty' in response.content)

    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"
                    , "remote"  : "True"
                    })
        response = self.client.post('/friends/%s' % self.friends[-1].id
                                  , fdata)
        self.failUnlessEqual(response.status_code, 200)

        fdata2 = {u'user_id': [u'494.0']
                , u'name': [u'McCarty, Michael']
                , u'project_id': [u'5.0']
                , u'id': [u'995.0'], u'_method': [u'put']}
        response = self.client.post('/friends/%s' % self.friends[-1].id
                                  , fdata2)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_delete(self):
        response = self.client.post('/friends/%s' % self.friends[-1].id
                                  , {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)

