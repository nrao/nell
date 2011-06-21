# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from django.test.client  import Client
from datetime            import datetime, timedelta, date

from test_utils               import BenchTestCase, timeIt
from sesshuns.models          import *
from scheduler.models         import *
from scheduler.utilities      import getReservationsFromDB
from scheduler.tests.utils    import create_sesshun, create_maintenance_period

class TestViews(BenchTestCase):

    def setupRxSchedule(self):
        d = datetime(2009, 4, 1, 0)
        for i in range(9):
            start_date = d + timedelta(5*i)
            for j in range(1,4):
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = i + j)
                rs.save()
    @timeIt
    def test_receivers_toggle_rcvr(self):
        self.setupRxSchedule()
        client = Client()

        # check initial conditions
        rs = Receiver_Schedule.objects.filter(start_date = datetime(2009, 4, 11)).order_by("receiver")
        self.assertEquals(["342", "450", "600"]
                        , [rd.receiver.abbreviation for rd in rs])

        # toggle a rcvr
        fromDt = toDt = datetime(2009, 4, 11).strftime("%m/%d/%Y %H:%M:%S")
        rcvr = "342" 
        response = client.post('/scheduler/receivers/toggle_rcvr',
                                   {"from" : fromDt,
                                    "to" : toDt,
                                    "rcvr" : rcvr})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"success": "ok"}')
   
        rs = Receiver_Schedule.objects.filter(start_date = \
            datetime(2009, 4, 11)).order_by("receiver")
        self.assertEquals(["450", "600"]
                        , [rd.receiver.abbreviation for rd in rs])

        # check error checking
        response = client.post('/scheduler/receivers/toggle_rcvr',
                                   {"from" : "dog",
                                    "to" : toDt,
                                    "rcvr" : rcvr})
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"message": "One of the following are invalid inputs: dog, 04/11/2009 00:00:00, 342", "error": "Invalid Inputs."}')

    @timeIt
    def test_receivers_schedule(self):
    
        self.setupRxSchedule()
        startdate = datetime(2009, 4, 6, 12)
        p = create_maintenance_period(start = startdate + timedelta(days = 1)
                      , duration = 8
                       )
        p.save()
        client = Client()

        response = client.get('/scheduler/receivers/schedule',
                                   {"startdate" : startdate,
                                    "duration" : 7})
        self.failUnlessEqual(response.status_code, 200)

        self.assertTrue('error' not in response.content)
        # NOTE: time in 'maintenance' key's time stamp should be taken
        # from the period 'p' created above rather than be hardcoded,
        # since the 'create_maintenance_period' utility converts from
        # ET to UTC and this test would fail depending on whether
        # we're in dailight or standard time.
        expected = '{"diff": [{"down": [], "up": ["RRI", "342", "450"], "day": "04/06/2009"}, {"down": ["RRI"], "up": ["600"], "day": "04/11/2009"}], "receivers": ["RRI", "342", "450", "600", "800", "1070", "L", "S", "C", "X", "Ku", "K", "Ka", "Q", "MBA", "Z", "Hol", "KFPA", "W"], "maintenance": ["%s"], "schedule": {"04/11/2009": ["342", "450", "600"], "04/06/2009": ["RRI", "342", "450"]}}' % (p.start)
        self.assertEqual(expected, response.content)

        self.failUnlessEqual(response.status_code, 200)

    def test_get_options(self):
        create_sesshun()
        c = Client()
        response = c.get('/scheduler/sessions/options', dict(mode='project_codes'))
        self.assertEquals(response.content,
                          '{"project codes": ["GBT09A-001"], "project ids": [1]}')
        response = c.get('/scheduler/sessions/options', dict(mode='session_handles', notcomplete='true', enabled='true'))
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
              , 'Total Time(s)': ['false']         , 'explorer': ['/scheduler/projects']
              }
        c = Client()
        response = c.post('/scheduler/configurations/explorer/columnConfigs', data)
        self.failUnlessEqual(response.status_code, 200)

    def test_column_configurations_explorer_get(self):
        c = Client()
        response = c.get('/scheduler/configurations/explorer/columnConfigs', {'explorer': '/project'})
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_filter_combinations_explorer_post(self):
        data = {'Trimester': '08C'
              , 'Project Type': 'science'
              , 'Complete': 'True'
              , 'explorer': '/scheduler/projects'
              , 'name': 'test'
              }
        c = Client()
        response = c.post('/scheduler/configurations/explorer/filterCombos', data)
        self.failUnlessEqual(response.status_code, 200)
        r = eval(response.content)
        ec = ExplorerConfiguration.objects.get(id = r['id'])
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
        response = c.get('/scheduler/reservations', data)
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

