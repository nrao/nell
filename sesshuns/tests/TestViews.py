from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from sesshuns.models         import *
from sesshuns.utilities      import getReservationsFromDB
from utils                   import create_sesshun

class TestViews(BenchTestCase):

    @timeIt
    def test_change_schedule(self):
        create_sesshun()
        c = Client()
        response = c.post('/schedule/change_schedule'
                        , dict(duration = "1.0"
                             , start    = "2009-10-11 04:00:00"))

    def test_get_options(self):
        create_sesshun()
        c = Client()
        response = c.get('/sessions/options', dict(mode='project_codes'))
        self.assertEquals(response.content,
                          '{"project codes": ["GBT09A-001"], "project ids": [1]}')
        response = c.get('/sessions/options', dict(mode='session_handles', notcomplete='true', enabled='true'))
        self.assertEquals(response.content,
                          '{"ids": [1], "session handles": ["Low Frequency With No RFI (GBT09A-001)"]}')

    @timeIt
    def test_column_configurations_explorer_post(self):
        data = {'Thesis?': ['false']               , 'Grade(s)': ['false']
              , 'Name': ['false']                  , 'PSC Time(s)': ['false']
              , 'Remaining Time': ['false']        , 'name': ['foo']
              , 'Co-I': ['false']                  , 'Complete?': ['false']
              , 'PCode': ['false']                 , 'Friend': ['false']
              , 'Max. Trimester Time(s)': ['false'], 'Trimester': ['false']
              , 'PI': ['false']                    , 'Type': ['false']
              , 'Total Time(s)': ['false']         , 'explorer': ['/projects']
              }
        c = Client()
        response = c.post('/configurations/explorer/columnConfigs', data)
        self.failUnlessEqual(response.status_code, 200)

    def test_column_configurations_explorer_get(self):
        c = Client()
        response = c.get('/configurations/explorer/columnConfigs', {'explorer': '/project'})
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_filter_combinations_explorer_post(self):
        data = {'Trimester': '08C'
              , 'Project Type': 'science'
              , 'Complete': 'True'
              , 'explorer': '/projects'
              , 'name': 'test'
              }
        c = Client()
        response = c.post('/configurations/explorer/filterCombos', data)
        self.failUnlessEqual(response.status_code, 200)
        r = eval(response.content)
        ec = first(ExplorerConfiguration.objects.filter(id = r['id']))
        self.assertTrue(ec is not None)

    def test_reservations(self):

        # create a user
        # Brian Cherinka (pst_id 800) has a reservation in Oct.
        # let's get that reservation, but make it point to this user.
        roles = Role.objects.all()
        u = User(first_name = "delete"
               , last_name = "me"
               , role = roles[0]
               # BOS gives id of 802 -> global id of 800
               , pst_id = 800
                 )
        u.save()
        # giv'm a project
        projs = Project.objects.all()
        inv = Investigator(user = u, project = projs[0])
        inv.save()

        c = Client()
        data = {'start' : '10/10/2010'
              , 'days'  : '8'
               }
        response = c.get('/reservations', data)
        self.failUnlessEqual(response.status_code, 200)
        r = eval(response.content)

        exp = {'reservations':
                 [{'pcodes': 'GBT09A-001'
                 , 'start': '10/05/2010'
                 , 'end': '10/10/2010'
                 , 'id': 800
                 , 'name': 'Brian Cherinka'}]
               , 'total': 1}

        self.assertEquals(exp, r)

        # cleanup
        inv.delete()
        u.delete()

    def test_reservations_from_db(self):

        # create a user
        roles = Role.objects.all()
        u = User(first_name = "delete"
               , last_name = "me"
               , role = roles[0]
                 )
        u.save()

        # giv'm a project
        projs = Project.objects.all()
        inv = Investigator(user = u, project = projs[0])
        inv.save()

        # giv'm a reservation
        start = date(2006, 2, 10)
        end   = date(2006, 2, 15)
        res = Reservation(user = u
                        , start_date = start
                        , end_date   = end
                          )
        res.save()

        frmt = "%m/%d/%Y"
        rs = getReservationsFromDB(start.strftime(frmt)
                                 , end.strftime(frmt)
                                  )
        exp = [{'pcodes': u'GBT09A-001'
              , 'start': '02/10/2006'
              , 'end': '02/15/2006'
              , 'id': None
              , 'name': 'delete me'
               }]
        self.assertEquals(exp, rs)

        # make sure it still gets picked up two days later
        start = date(2006, 2, 12)
        end   = date(2006, 2, 17)
        rs = getReservationsFromDB(start.strftime(frmt)
                                 , end.strftime(frmt)
                                  )
        self.assertEquals(exp, rs)

        # make sure it is not picked up
        start = date(2006, 2, 22)
        end   = date(2006, 2, 27)
        rs = getReservationsFromDB(start.strftime(frmt)
                                 , end.strftime(frmt)
                                  )
        self.assertEquals([], rs)

        # cleanup
        res.delete()
        inv.delete()
        u.delete()

