from copy                import copy
from datetime            import date, datetime, timedelta
from django.conf         import settings
from django.contrib.auth import models as m
from django.test.client  import Client
from django.http         import QueryDict
import simplejson as json
import lxml.etree as et

from models                          import *
from test_utils.NellTestCase         import NellTestCase
from tools                           import DBReporter
from tools                           import ScheduleTools
from tools                           import TimeAccounting
from utilities.database              import DSSPrime2DSS
from utilities.receiver              import ReceiverCompile
from utilities                       import UserInfo
from utilities                       import NRAOBosDB

# Test field data
fdata = {"total_time": "3"
       , "req_max": "6"
       , "name": "Low Frequency With No RFI"
       , "grade": "A"
       , "science": "pulsar"
       , "orig_ID": "0"
       , "between": "0"
       , "proj_code": "GBT09A-001"
       , "PSC_time": "2"
       , "sem_time": 0.0
       , "req_min": "2"
       , "freq": 6.0
       , "type": "open"
       , "source" : "blah"
       , "enabled" : False
       , "authorized" : False
       , "complete" : False
       , "backup" : False
         }

def create_sesshun():
    "Utility method for creating a Sesshun to test."

    s = Sesshun()
    s.set_base_fields(fdata)
    allot = Allotment(psc_time          = fdata.get("PSC_time", 0.0)
                    , total_time        = fdata.get("total_time", 0.0)
                    , max_semester_time = fdata.get("sem_time", 0.0)
                    , grade             = 4.0
                      )
    allot.save()
    s.allotment        = allot
    status = Status(
               enabled    = True
             , authorized = True
             , complete   = False
             , backup     = False
                        )
    status.save()
    s.status = status
    s.save()

    t = Target(session    = s
             , system     = first(System.objects.filter(name = "J2000"))
             , source     = "test source"
             , vertical   = 2.3
             , horizontal = 1.0
               )
    t.save()
    return s

# Testing models
class TestUser(NellTestCase):
    def setUp(self):
        # TBF: From here down, till noted, is the same code as TestProject
        super(TestUser, self).setUp()

        self.project = Project()
        pdata = {"semester"   : "09A"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "A"
        }
        self.project.update_from_post(pdata)
        self.project.save()

        obsRole = first(Role.objects.filter(role = "Observer"))

        # Create Investigator1 and his 3 blackouts.
        self.user1 = User(sanctioned = True, role = obsRole)
        self.user1.save()

        self.investigator1 =  Investigator(project  = self.project
                                         , user     = self.user1
                                         , observer = True)
        self.investigator1.save()

        self.user2 = User(sanctioned = True, role = obsRole)
        self.user2.save()

        self.investigator2 =  Investigator(project  = self.project
                                         , user     = self.user2
                                         , observer = True)
        self.investigator2.save()

        self.sesshun = create_sesshun()
        self.sesshun.project = self.project
        self.sesshun.save()

        # TBF: end of redundant code, now add periods
        #period_data = {"session" : self.sesshun
        #             , "date" 
        state = first(Period_State.objects.filter(abbreviation = 'S'))
        self.period1 = Period(session  = self.sesshun
                            , start    = datetime(2010, 10, 1, 0, 0, 0)
                            , duration = 1.0
                            , state    = state
                            , backup   = False)
        self.period1.save()                    
        self.period2 = Period(session  = self.sesshun
                            , start    = datetime(2010, 10, 2, 5, 0, 0)
                            , duration = 3.5
                            , state    = state
                            , backup   = False)
        self.period2.save()                    

        # add the project friend
        self.user3 = User(sanctioned = True, role = obsRole)
        self.user3.save()
        self.project.friend = self.user3
        self.project.save()

        # add an unrelated user
        self.user4 = User(sanctioned = True, role = obsRole)
        self.user4.save()

    def tearDown(self):
        self.investigator2.delete()
        self.user2.delete()
        self.investigator1.delete()
        self.user1.delete()
        self.period1.remove() #delete()
        self.period2.remove() #delete()
        self.project.delete()
        self.user3.delete()
        self.user4.delete()

    def test_canViewProject(self):

        pcode = self.project.pcode
        self.assertEqual(True, self.user1.canViewProject(pcode))
        self.assertEqual(True, self.user2.canViewProject(pcode))
        self.assertEqual(True, self.user3.canViewProject(pcode))
        self.assertEqual(False, self.user4.canViewProject(pcode))

    def test_canViewUser(self):

        self.assertEqual(True, self.user1.canViewUser(self.user2))
        self.assertEqual(True, self.user2.canViewUser(self.user1))
        self.assertEqual(True, self.user3.canViewUser(self.user1))
        self.assertEqual(True, self.user3.canViewUser(self.user2))
        self.assertEqual(False, self.user1.canViewUser(self.user3))
        self.assertEqual(False, self.user2.canViewUser(self.user3))
        self.assertEqual(False, self.user4.canViewUser(self.user1))
        self.assertEqual(False, self.user4.canViewUser(self.user2))
        self.assertEqual(False, self.user4.canViewUser(self.user3))

    def test_getPeriods(self):
        
        # exp values
        periods = [self.period1, self.period2]
        sep1 = datetime(2010,  9, 1, 0, 0, 0)
        oct2 = datetime(2010, 10, 2, 0, 0, 0)
        dec1 = datetime(2010, 12, 1, 0, 0, 0)

        self.assertEqual(periods, self.user1.getPeriods())
        self.assertEqual(periods, self.user2.getPeriods())
        self.assertEqual(periods, self.user1.getUpcomingPeriods(sep1))
        self.assertEqual(periods, self.user2.getUpcomingPeriods(sep1))
        self.assertEqual([self.period2]
                                , self.user2.getUpcomingPeriods(oct2))
        self.assertEqual([self.period1]
                                , self.user2.getObservedPeriods(oct2))
        self.assertEqual([],      self.user2.getUpcomingPeriods(dec1))

class TestPeriod(NellTestCase):

    def setUp(self):
        super(TestPeriod, self).setUp()
        self.sesshun = create_sesshun()
        self.fdata = {"session":  1
                    , "date":    "2009-6-1"
                    , "time":    "12:15"
                    , "duration": 4.25
                    , "backup":   False
                     }

    def test_update_from_post(self):
        p = Period()
        p.init_from_post(self.fdata, 'UTC')
        
        self.assertEqual(p.session, self.sesshun)
        self.assertEqual(p.start, datetime(2009, 6, 1, 12, 15))
        self.assertEqual(p.duration, self.fdata["duration"])
        self.assertEqual(p.backup, self.fdata["backup"])

    def test_jsondict(self):
         
        start = datetime(2009, 6, 1, 12, 15)
        dur   = 180
        
        p = Period()
        p.start = start
        p.duration = dur
        p.session = self.sesshun
        p.backup = True
        p.state = first(Period_State.objects.filter(abbreviation = 'P'))

        p.save()

        jd = p.jsondict('UTC')

        self.assertEqual(jd["duration"], dur)
        self.assertEqual(jd["date"], "2009-06-01")
        self.assertEqual(jd["time"], "12:15")
        self.assertEqual(jd["state"], "P")

        p.delete()

    def test_get_periods(self):

        # setup some periods
        times = [(datetime(2000, 1, 1, 0), 5.0)
               , (datetime(2000, 1, 1, 5), 3.0)
               , (datetime(2000, 1, 1, 8), 4.0)
               ]
        ps = []
        state = first(Period_State.objects.filter(abbreviation = 'P'))
        for start, dur in times:
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            p = Period( session    = self.sesshun
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()          
            ps.append(p)

        # now try and retrieve them from the DB:
        # get them all
        dt1 = datetime(2000, 1, 1, 0)
        dur = 12 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps)

        # get them all because the first overlaps
        dt1 = datetime(2000, 1, 1, 1)
        dur = 12 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps)

        # now leave out the first
        dt1 = datetime(2000, 1, 1, 5)
        dur = 12 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps[1:])

        # keep getting the last one too
        dt1 = datetime(2000, 1, 1, 5)
        dur = 6 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, ps[1:])

        # now just get the middle one
        dt1 = datetime(2000, 1, 1, 5)
        dur = 3 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, [ps[1]])

        # again, just the middle one
        dt1 = datetime(2000, 1, 1, 6)
        dur = 2 * 60
        ps1 = Period.get_periods(dt1, dur)
        self.assertEquals(ps1, [ps[1]])

        # cleanup
        for p in ps:
            p.delete()

class TestReceiver(NellTestCase):

    def setUp(self):
        super(TestReceiver, self).setUp()
        self.client = Client()
        s = Sesshun()
        s.init_from_post({})
        s.save()

    def test_get_abbreviations(self):
        nn = Receiver.get_abbreviations()
        self.assertTrue(len(nn) > 17)
        self.assertEquals([n for n in nn if n == 'Ka'], ['Ka'])

    def test_save_receivers(self):
        s = Sesshun.objects.all()[0]
        rcvr = 'L'
        s.save_receivers(rcvr)
        rgs = s.receiver_group_set.all()
        self.assertEqual(1, len(rgs))
        self.assertEqual(rcvr, rgs[0].receivers.all()[0].abbreviation)

        s.receiver_group_set.all().delete()
        s.save_receivers('L | (X & S)')
        rgs = s.receiver_group_set.all()
        #print rgs
        # TBF WTF? now it is S, then it is X??
        #print rgs[0].receivers.all()[1].abbreviation
        self.assertEqual(2, len(rgs))
        #print rgs[0].receivers.all()[0].abbreviation
        #print rgs[0].receivers.all()[1].abbreviation
        #print rgs[1].receivers.all()[0].abbreviation
        #print rgs[1].receivers.all()[1].abbreviation
        self.assertEqual('L', rgs[0].receivers.all()[0].abbreviation)
        self.assertEqual('X', rgs[0].receivers.all()[1].abbreviation)
        self.assertEqual('L', rgs[1].receivers.all()[0].abbreviation)
        self.assertEqual('S', rgs[1].receivers.all()[1].abbreviation)

class TestReceiverSchedule(NellTestCase):

    def setUp(self):
        super(TestReceiverSchedule, self).setUp()
        self.client = Client()

        d = datetime(2009, 4, 1, 0)
        for i in range(9):
            start_date = d + timedelta(5*i)
            for j in range(1,4):
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = i + j)
                rs.save()

    def test_extract_schedule(self):
        startdate = datetime(2009, 4, 6, 12)
        duration = 15
        schedule = Receiver_Schedule.extract_schedule(startdate = startdate,
                                                      days = duration)
        expected = [datetime(2009, 4, 11, 0, 0)
                  , datetime(2009, 4, 16, 0, 0)
                  , datetime(2009, 4, 6, 0, 0)
                  , datetime(2009, 4, 21, 0, 0)]
        self.assertEqual(expected, schedule.keys())
        jschedule = Receiver_Schedule.jsondict(schedule)
        expected = {'04/11/2009': [u'342', u'450', u'600']
                  , '04/16/2009': [u'450', u'600', u'800']
                  , '04/06/2009': [u'RRI', u'342', u'450']
                  , '04/21/2009': [u'600', u'800', u'1070']}
        self.assertEqual(expected, jschedule)

    def test_previousDate(self):
        self.assertEqual(datetime(2009, 4, 6, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 4, 6, 12)))
        self.assertEqual(datetime(2009, 4, 1, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 4, 5, 23)))
        self.assertEqual(datetime(2009, 5, 11, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 7, 1, 0)))
        self.assertEqual(datetime(2009, 4, 1, 0),
                         Receiver_Schedule.previousDate(
                             datetime(2009, 4, 1, 0)))

    def test_receivers_schedule(self):
        startdate = datetime(2009, 4, 6, 12)
        response = self.client.get('/receivers/schedule',
                                   {"startdate" : startdate,
                                    "duration" : 7})
        self.failUnlessEqual(response.status_code, 200)
        expected = '{"schedule": {"04/11/2009": ["342", "450", "600"], "04/06/2009": ["RRI", "342", "450"]}}'
        self.assertEqual(expected, response.content)

class TestProject(NellTestCase):
    def setUp(self):
        super(TestProject, self).setUp()

        self.project = Project()
        pdata = {"semester"   : "09A"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "A"
        }
        self.project.update_from_post(pdata)
        self.project.save()

        # Create Investigator1 and his 3 blackouts.
        self.user1 = User(sanctioned = True
                        , role = first(Role.objects.filter(role = "Observer"))
                     )
        self.user1.save()

        self.investigator1 =  Investigator(project  = self.project
                                         , user     = self.user1
                                         , observer = True)
        self.investigator1.save()

        self.user2 = User(sanctioned = True
                        , role = first(Role.objects.filter(role = "Observer"))
                     )
        self.user2.save()

        self.investigator2 =  Investigator(project  = self.project
                                         , user     = self.user2
                                         , observer = True)
        self.investigator2.save()

        self.sesshun = create_sesshun()
        self.sesshun.project = self.project
        self.sesshun.save()

    def tearDown(self):
        self.investigator2.delete()
        self.user2.delete()
        self.investigator1.delete()
        self.user1.delete()
        self.project.delete()

    def test_get_blackout_times1(self):
        # Create Investigator1's 3 blackouts.
        blackout11 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        blackout11.save()

        blackout12 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 18)
                            , end_date   = datetime(2009, 1, 4, 18))
        blackout12.save()

        blackout13 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 2, 12)
                            , end_date   = datetime(2009, 1, 4, 20))
        blackout13.save()

        # Create Investigator2's 2 blackouts.
        blackout21 = Blackout(user       = self.user2
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        blackout21.save()

        blackout22 = Blackout(user       = self.user2
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 18)
                            , end_date   = datetime(2009, 1, 4, 13))
        blackout22.save()

        # Now we can finally do our test.
        expected = [
            (datetime(2009, 1, 2, 12), datetime(2009, 1, 3, 11))
        ]

        today = datetime(2009, 1, 1)
        later = today + timedelta(days = 30)
        r = self.project.get_blackout_times(today, later)
        self.assertEquals(expected, r)

        # Clean up
        blackout22.delete()
        blackout21.delete()
        blackout13.delete()
        blackout12.delete()
        blackout11.delete()

    def test_get_blackout_times2(self):
        # Create Investigator1's 3 blackouts.
        self.investigator1.observer = False
        self.investigator1.save()

        blackout11 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        blackout11.save()

        blackout12 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 18)
                            , end_date   = datetime(2009, 1, 4, 18))
        blackout12.save()

        blackout13 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 2, 12)
                            , end_date   = datetime(2009, 1, 4, 20))
        blackout13.save()

        # Create Investigator2's 2 blackouts.
        self.investigator2.observer = False
        self.investigator2.save()

        blackout21 = Blackout(user       = self.user2
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        blackout21.save()

        blackout22 = Blackout(user       = self.user2
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 18)
                            , end_date   = datetime(2009, 1, 4, 13))
        blackout22.save()

        today = datetime(2009, 1, 1)
        later = today + timedelta(days = 30)
        r = self.project.get_blackout_times(today, later)
        self.assertEquals([], r)

        # Clean up
        blackout22.delete()
        blackout21.delete()
        blackout13.delete()
        blackout12.delete()
        blackout11.delete()

        self.investigator2.observer = True
        self.investigator2.save()
        self.investigator1.observer = True
        self.investigator1.save()

    def test_get_blackout_times3(self):
        # Create Investigator1's 3 blackouts.
        blackout11 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        blackout11.save()

        blackout12 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 18)
                            , end_date   = datetime(2009, 1, 4, 18))
        blackout12.save()

        blackout13 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 2, 12)
                            , end_date   = datetime(2009, 1, 4, 20))
        blackout13.save()

        # Investigator 2 has no blackouts - She's available all the time.

        today = datetime(2009, 1, 1)
        later = today + timedelta(days = 30)
        r = self.project.get_blackout_times(today, later)
        self.assertEquals([], r)

        # Clean up
        blackout13.delete()
        blackout12.delete()
        blackout11.delete()

    def test_get_blackout_times4(self):
        # Create Investigator1's 3 blackouts.
        blackout11 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 11)
                            , end_date   = datetime(2009, 1, 3, 11))
        blackout11.save()

        blackout12 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 1, 18)
                            , end_date   = datetime(2009, 1, 4, 18))
        blackout12.save()

        blackout13 = Blackout(user       = self.user1
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 1, 2, 12)
                            , end_date   = datetime(2009, 1, 4, 20))
        blackout13.save()

        # Create Investigator2's 2 blackouts.
        blackout21 = Blackout(user       = self.user2
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 2, 1, 11)
                            , end_date   = datetime(2009, 2, 3, 11))
        blackout21.save()

        blackout22 = Blackout(user       = self.user2
                            , repeat     = first(Repeat.objects.all())
                            , start_date = datetime(2009, 3, 1, 18)
                            , end_date   = datetime(2009, 3, 4, 13))
        blackout22.save()

        today = datetime(2009, 1, 1)
        later = today + timedelta(days = 30)
        r = self.project.get_blackout_times(today, later)
        self.assertEquals([], r) # Coordinated blackouts.

        # Clean up
        blackout22.delete()
        blackout21.delete()
        blackout13.delete()
        blackout12.delete()
        blackout11.delete()

    def test_get_receiver_blackout_ranges(self):
        # Schedule = 4/01/2009:   450,   600,  800
        #            4/06/2009:   600,   800, 1070
        #            4/11/2009:   800,  1070,  1_2
        #            4/16/2009:  1070,   1_2,  2_3
        #            4/21/2009:   1_2,   2_3,  4_6
        #            4/26/2009:   2_3,   4_6, 8_10
        #            5/01/2009:   4_6,  8_10, 12_18
        #            5/06/2009:  8_10, 12_18, 18_26
        #            5/11/2009: 12_18, 18_26, 26_40
        start   = datetime(2009, 4, 1, 0)
        end     = datetime(2009, 6, 1, 0)
        rcvr_id = 3
        for i in range(9):
            start_date = start + timedelta(5*i)
            for j in range(1, 4):
                rcvr_id = rcvr_id + 1
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = rcvr_id)
                rs.save()
            rcvr_id = rcvr_id - 2

        # No sessions, no receivers
        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals([], blackouts)

        # No available receivers at these times: 
        expected = [(datetime(2009, 4, 1), datetime(2009, 4, 11))
                  , (datetime(2009, 5, 1), None)]
        self.sesshun.save_receivers('L | (X & S)')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # No available receivers at these times: 
        expected = [(datetime(2009, 4, 1), datetime(2009, 4, 26))
                  , (datetime(2009, 5, 1), datetime(2009, 5, 6))]
        self.sesshun.save_receivers('K | (X & S)')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # No available receivers at these times: 
        expected = [(datetime(2009, 4, 11), None)]
        self.sesshun.save_receivers('600')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # Always an available receiver.
        self.sesshun.save_receivers('(800 | S) | Ku')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals([], blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # Clean up.
        Receiver_Schedule.objects.all().delete()

    def test_init_from_post(self):
        p1 = Project()
        p2 = Project()
        self.gitrdone(p1, p1.init_from_post, p2, p2.init_from_post)

        p3 = Project()
        p3.init_from_post({})

    def test_update_from_post(self):
        p1 = Project()
        p2 = Project()
        self.gitrdone(p1, p1.update_from_post, p2, p2.update_from_post)

    def gitrdone(self, p1, f1, p2, f2):
        "Mike was here."

        p_fdata = {"semester" : "09A"
                 , "type"     : "science"
                 , "total_time" : "10.0"
                 , "PSC_time"   : "10.0"
                 , "sem_time"   : "10.0"
                 , "grade"      : "A"
                   }
        f1(p_fdata)
        self.defaultAssertion(p_fdata, p1)
        
        p_fdata1 = {"semester" : "09A"
                 , "type"     : "science"
                 , "total_time" : "10.0, 5.0"
                 , "PSC_time"   : "10.0, 5.0"
                 , "sem_time"   : "10.0, 5.0"
                 , "grade"      : "A, B"
                   }
        f2(p_fdata1)
        self.defaultAssertion(p_fdata1, p2)

        p_fdata = {"semester" : "09A"
                 , "type"     : "science"
                 , "total_time" : "10.0, 5.0, 1.0"
                 , "PSC_time"   : "10.0, 5.0, 1.0"
                 , "sem_time"   : "10.0, 5.0, 1.0"
                 , "grade"      : "A, B, C"
                   }
        f2(p_fdata)
        self.defaultAssertion(p_fdata, p2)

        f2(p_fdata1)
        self.defaultAssertion(p_fdata1, p2)

    def defaultAssertion(self, p_fdata, p):
        totals = map(float, p_fdata.get("total_time").split(', '))
        pscs     = map(float, p_fdata.get("PSC_time", "").split(', '))
        max_sems = map(float, p_fdata.get("sem_time", "").split(', '))
        grades   = map(grade_abc_2_float, p_fdata.get("grade", "").split(', '))
        for a in p.allotments.all():
            self.assertTrue(a.total_time in totals)
            self.assertTrue(a.psc_time in pscs)
            self.assertTrue(a.max_semester_time in max_sems)
            self.assertTrue(a.grade in grades)
        
class TestSesshun(NellTestCase):

    def setUp(self):
        super(TestSesshun, self).setUp()
        self.sesshun = create_sesshun()

    def test_get_ha_limit_blackouts(self):
        # With default target.
        startdate = datetime.utcnow()
        days      = 5
        r = self.sesshun.get_ha_limit_blackouts(startdate, days)

        t = Target(session    = self.sesshun
                 , system     = first(System.objects.filter(name = "J2000"))
                 , source     = "test source"
                 , vertical   = 2.3
                 , horizontal = 1.0)
        t.save()

        # TBF: Need to write test.

        t.delete()

    def test_create(self):
        expected = first(Sesshun.objects.filter(id = self.sesshun.id))
        self.assertEqual(expected.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(expected.name, fdata["name"])

    def test_init_from_post(self):
        s = Sesshun()
        s.init_from_post(fdata)
        
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])

        # does this still work if you requery the DB?
        ss = Sesshun.objects.all()
        self.assertEqual(2, len(ss))
        s = ss[1]
        # notice the change in type when we compare this way!
        self.assertEqual(s.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])

    def test_update_from_post(self):
        ss = Sesshun.objects.all()
        s = Sesshun()
        s.init_from_post(fdata)
        
        self.assertEqual(s.frequency, fdata["freq"])
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])

        # change a number of things and see if it catches it
        ldata = dict(fdata)
        ldata["freq"] = "10"
        ldata["source"] = "new source"
        ldata["total_time"] = "99"
        ldata["enabled"] = "true"
        s.update_from_post(ldata)
        
        # now get this session from the DB
        ss = Sesshun.objects.all()
        s = ss[1]
        self.assertEqual(s.frequency, float(ldata["freq"]))
        self.assertEqual(s.allotment.total_time, float(ldata["total_time"]))
        self.assertEqual(s.target_set.get().source, ldata["source"])
        self.assertEqual(s.status.enabled, ldata["enabled"] == "true")

    def test_update_from_post2(self):
        ss = Sesshun.objects.all()
        s = Sesshun()
        s.init_from_post(fdata)
        
        self.assertEqual(s.frequency, fdata["freq"])
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.original_id, int(fdata["orig_ID"]))

        # check to see if we can handle odd types 
        ldata = dict(fdata)
        ldata["freq"] = "10.5"
        ldata["source"] = None 
        ldata["total_time"] = "99.9"
        ldata["orig_ID"] = "0.0"
        ldata["enabled"] = "true" 
        s.update_from_post(ldata)
        
        # now get this session from the DB
        ss = Sesshun.objects.all()
        s = ss[1]
        self.assertEqual(s.frequency, float(ldata["freq"]))
        self.assertEqual(s.allotment.total_time, float(ldata["total_time"]))
        self.assertEqual(s.target_set.get().source, ldata["source"])
        self.assertEqual(s.status.enabled, True) # "True" -> True
        self.assertEqual(s.original_id, 0) #ldata["orig_ID"]) -- "0.0" -> Int

    def test_grade_abc_2_float(self):
        s = Sesshun()
        values = [('A',4.0),('B',3.0),('C',2.0)]
        for letter, num in values:
            fltGrade = grade_abc_2_float(letter)
            self.assertEqual(num, fltGrade)

    def test_grade_float_2_abc(self):
        s = Sesshun()
        values = [('A',4.0),('B',3.0),('C',2.0)]
        for letter, num in values:
            letterGrade = grade_float_2_abc(num)
            self.assertEqual(letter, letterGrade)

# Testing View Resources

class TestPeriodResource(NellTestCase):

    def setUp(self):
        super(TestPeriodResource, self).setUp()
        self.rootURL = '/periods'
        self.sess = create_sesshun()
        self.client = Client()
        self.fdata = {'session'  : self.sess.id
                    , 'date'    : '2009-06-01'
                    , 'time'    : '00:00'
                    , 'duration' : 1.0
                    , 'backup'   : True}
        self.p = Period()
        self.p.init_from_post(self.fdata, 'UTC')
        self.p.save()

    def test_create(self):
        response = self.client.post(self.rootURL + '/UTC', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_create_empty(self):
        response = self.client.post(self.rootURL + '/ET')
        self.failUnlessEqual(response.status_code, 200)

    def test_read(self):
        url = "%s/%s?startPeriods=%s&daysPeriods=%d" % \
                            (self.rootURL 
                           , 'UTC'
                           , self.fdata['date'] + '%20' + self.fdata['time'] + ':00'
                           , 2)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 1')

    def test_read_keywords(self):
        # use a date range that picks up our one period
        url = "%s/%s?startPeriods=%s&daysPeriods=%d" % \
                            (self.rootURL 
                           , 'UTC'
                           , self.fdata['date'] + '%20' + self.fdata['time'] + ':00'
                           , 3)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 1')
        # now use a date range that doesn't
        url = "%s/%s?startPeriods=%s&daysPeriods=%d" % (
                                                     self.rootURL 
                                                   , 'UTC'
                                                   , '2009-06-02 00:00:00' 
                                                   , 3)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 0')


    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('%s/%s/%s' % (self.rootURL
                                                 ,'ET'
                                                 , self.p.id), fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('%s/%s/%s' % (self.rootURL
                                                , 'ET'
                                                , self.p.id)
                                  , {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)

class TestProjectResource(NellTestCase):

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
        self.p.init_from_post(self.fdata)
        self.p.save()

    def test_create(self):
        response = self.client.post('/projects', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_create_empty(self):
        response = self.client.post('/projects')
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

    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('/projects/%s' % self.p.id, fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('/projects/%s' % self.p.id, {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)
        
    
class TestSessionResource(NellTestCase):

    def setUp(self):
        super(TestSessionResource, self).setUp()
        self.client = Client()
        s = Sesshun()
        s.init_from_post({})
        s.save()
        self.s = s

    def test_create(self):
        response = self.client.post('/sessions')
        self.failUnlessEqual(response.status_code, 200)

    def test_create2(self):
        fdata = {'req_max': ['6.0']
               , 'grade': ['A']
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
        self.assertEquals(r_json['receiver'], u'(K) & (L | S)')
        # etc
        response = self.client.post('/sessions',
                                    {'receiver' : 'Ka | (342 & S)'})
        self.failUnlessEqual(response.status_code, 200)
        r_json = json.loads(response.content)
        self.assertTrue(r_json.has_key('receiver'))
        self.assertEquals(r_json['receiver'], u'(342 | Ka) & (S | Ka)')
    
class TestGetOptions(NellTestCase):

    def test_get_options(self):
        create_sesshun()
        c = Client()
        response = c.get('/sessions/options', dict(mode='project_codes'))
        self.assertEquals(response.content,
                          '{"project codes": ["GBT09A-001"]}')
        response = c.get('/sessions/options', dict(mode='session_handles'))
        self.assertEquals(response.content,
                          '{"ids": [1], "session handles": ["Low Frequency With No RFI (GBT09A-001)"]}')

class TestChangeSchedule(NellTestCase):
    def test_change_schedule(self):
        create_sesshun()
        c = Client()
        response = c.post('/schedule/change_schedule'
                        , dict(duration = "1.0"
                             , start    = "2009-10-11 04:00:00"))
        print response                     

class TestShiftPeriodBoundaries(NellTestCase):
    def setUp(self):
        super(TestShiftPeriodBoundaries, self).setUp()

        # setup some periods
        self.start = datetime(2000, 1, 1, 0)
        self.end   = self.start + timedelta(hours = 12)
        times = [(datetime(2000, 1, 1, 0), 5.0, "one")
               , (datetime(2000, 1, 1, 5), 3.0, "two")
               , (datetime(2000, 1, 1, 8), 4.0, "three")
               ]
        self.ps = []
        for start, dur, name in times:
            s = create_sesshun()
            s.name = name
            s.save()
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            state = first(Period_State.objects.filter(abbreviation = 'S'))
            p = Period( session    = s
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()          
            self.ps.append(p)

        self.backup = create_sesshun()
        self.backup.name = "backup"
        self.backup.status.backup = True
        self.backup.save()

    def tearDown(self):
        super(TestShiftPeriodBoundaries, self).tearDown()

        for p in self.ps:
            p.session.delete()
            p.remove() #delete()

    def test_shift_period_boundaries(self):
        create_sesshun()
        c = Client()

        period_id = self.ps[1].id
        new_time = self.ps[1].start + timedelta(hours = 1)
        time = new_time.strftime("%Y-%m-%d %H:%M:%S")

        response = c.post('/schedule/shift_period_boundaries'
                        , dict(period_id = period_id
                             , start_boundary = 1
                             , description = "test"
                             , time    = time)) #"2009-10-11 04:00:00"))
        self.failUnless("ok" in response.content)                     

# Testing Observers UI

class TestObservers(NellTestCase):

    def setUp(self):
        super(TestObservers, self).setUp()

        # Don't use CAS for authentication during unit tests
        if 'django_cas.backends.CASBackend' in settings.AUTHENTICATION_BACKENDS:
            settings.AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS[:-1]
        if 'django_cas.middleware.CASMiddleware' in settings.MIDDLEWARE_CLASSES:
            settings.MIDDLEWARE_CLASSES      = settings.MIDDLEWARE_CLASSES[:-1]

        self.client = Client()
        
        self.auth_user = m.User.objects.create_user('dss', 'dss@nrao.edu', 'asdf5!')
        self.auth_user.is_staff = True
        self.auth_user.save()

        self.u = User(first_name = "Test"
                    , last_name  = "User"
                    , role       = first(Role.objects.all())
                    , username   = self.auth_user.username
                      )
        self.u.save()
        self.client.login(username = "dss", password = "asdf5!")
        
        self.p = Project()
        self.p.init_from_post({'semester'   : '09C'
                             , 'type'       : 'science'
                             , 'pcode'      : 'mike' 
                             , 'name'       : 'mikes awesome project!'
                             , 'PSC_time'   : '100.0'
                             , 'total_time' : '100.0'
                             , 'sem_time'   : '50.0'
                               })
        self.p.save()

        i =  Investigator(project = self.p
                        , user    = self.u
                         )
        i.save()

        fdata2 = copy(fdata)
        fdata2.update({'source_v' : 1.0
                     , 'source_h' : 1.0
                     , 'source'   : 'testing'
                       })
        self.s = Sesshun()
        self.s.init_from_post(fdata2)
        self.s.project = self.p
        self.s.save()

    def tearDown(self):
        super(TestObservers, self).tearDown()

    def get(self, url, data = {}):
        """
        Sets the USER extra kwar
        """
        return self.client.get(url, data, USER = self.auth_user.username)

    def post(self, url, data = {}):
        """
        Sets the USER extra kwar
        """
        return self.client.post(url, data, USER = self.auth_user.username)

    def test_profile(self):
        response = self.get('/profile/%s' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)

    def test_project(self):
        response = self.get('/project/%s' % self.p.pcode)
        self.failUnlessEqual(response.status_code, 200)

    def test_search(self):
        response = self.post('/search', {'search' : 'Test'})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue("User" in response.content)

    def test_toggle_session(self):
        response = self.post(
            '/project/%s/session/%s/enable' % (self.p.pcode, self.s.name))
        self.failUnlessEqual(response.status_code, 302)
        s = first(Sesshun.objects.filter(id = self.s.id))
        self.assertEqual(s.status.enabled, True)

    def test_toggle_observer(self):
        i_id = first(self.p.investigator_set.all()).id
        response = self.post(
            '/project/%s/investigator/%s/observer' % (self.p.pcode, i_id))
        self.failUnlessEqual(response.status_code, 302)
        i = first(Investigator.objects.filter(id = i_id))
        self.assertEqual(i.observer, True)

    def test_dynamic_contact_form(self):
        response = self.get('/profile/%s/dynamic_contact/form' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)

    def test_dynamic_contact_save(self):
        data = {'contact_instructions' : "I'll be at Bob's house."}
        response = self.post('/profile/%s/dynamic_contact' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)
        u = first(User.objects.filter(id = self.u.id))
        self.assertEqual(u.contact_instructions, data.get('contact_instructions'))

    def create_blackout(self):
        b             = Blackout(user = self.u)
        b.start       = datetime(2009, 1, 1)
        b.end         = datetime(2009, 12, 31)
        b.repeat      = first(Repeat.objects.all())
        b.description = "This is a test blackout."
        b.save()
        return b
        
    def test_blackout_form(self):
        response = self.get('/profile/%s/blackout/form' % self.u.id)
        self.failUnlessEqual(response.status_code, 200)

        b = self.create_blackout()
        data = {'_method' : 'PUT'
              , 'id'      : b.id
                }
        response = self.get('/profile/%s/blackout/form' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(b.description in response.content)

    def test_blackout(self):
        b     = self.create_blackout()
        start = datetime(2009, 1, 1)
        end   = datetime(2009, 1, 31)
        until = datetime(2010, 1, 31)
        data = {'start'       : start.date().strftime("%m/%d/%Y")
              , 'starttime'   : start.time().strftime("%H:%M")
              , 'end'         : end.date().strftime("%m/%d/%Y")
              , 'endtime'     : end.time().strftime("%H:%M")
              , 'tz'          : 'UTC'
              , 'repeat'      : 'Once'
              , 'until'       : until.strftime("%m/%d/%Y")
              , 'untiltime'   : until.strftime("%H:%M")
              , 'description' : "This is a test blackout."
              , '_method'     : 'PUT'
              , 'id'          : b.id
                }

        response = self.post(
            '/profile/%s/blackout' % self.u.id, data)
        b = first(Blackout.objects.filter(id = b.id))
        self.assertEqual(b.end_date.date().strftime("%m/%d/%Y") , data.get('end'))
        self.assertEqual(b.until.date().strftime("%m/%d/%Y") , data.get('until'))
        self.failUnlessEqual(response.status_code, 302)
        
        response = self.get(
            '/profile/%s/blackout' % self.u.id
          , {'_method' : 'DELETE', 'id' : b.id})
        self.failUnlessEqual(response.status_code, 302)

        data['end'] = date(2009, 5, 31).strftime("%m/%d/%Y")
        _ = data.pop('_method')
        _ = data.pop('id')
        response    = self.post(
            '/profile/%s/blackout' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)
        b = first(self.u.blackout_set.all())
        self.assertEqual(b.end_date.date().strftime("%m/%d/%Y"), data.get('end'))
        b.delete()

        data['until'] = ''
        response    = self.post(
            '/profile/%s/blackout' % self.u.id, data)
        self.failUnlessEqual(response.status_code, 302)

    def test_get_period_day_time(self):

        # create a period
        s = create_sesshun()
        state = first(Period_State.objects.filter(abbreviation = 'S'))
        p = Period(session = s
                 , start = datetime(2009, 9, 9, 12)
                 , duration = 1.0
                 , state = state)
        p.save()         
        day = datetime(2009, 9, 9)
        
        # make sure it comes back in the correct day for UTC
        data = { 'start': day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz'   : 'UTC' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 9), [(datetime(2009, 9, 9, 12), datetime(2009, 9, 9, 13), False, False, p)])
             , (datetime(2009, 9, 10), [])
             , (datetime(2009, 9, 11), [])]

        self.assertEqual(exp, calendar)     

        # make sure it comes back in the correct day for EST
        data = { 'start': day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz'   : 'ET' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 9), [(datetime(2009, 9, 9, 8), datetime(2009, 9, 9, 9), False, False, p)])
             , (datetime(2009, 9, 10), [])
             , (datetime(2009, 9, 11), [])]
        self.assertEqual(exp, calendar)     

        # clean up
        p.remove() #delete()
        s.delete()

    def test_get_period_day_time2(self):

        # create a period
        s = create_sesshun()
        state = first(Period_State.objects.filter(abbreviation = 'S'))
        p = Period(session = s
                 , start = datetime(2009, 9, 2, 1)
                 , duration = 6.0
                 , state = state)
        p.save()         
        day = datetime(2009, 9, 1)

        # make sure it comes back in the correct day for UTC
        data = { 'start' : day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz' : 'UTC' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 1), [])
             , (datetime(2009, 9, 2), [(datetime(2009, 9, 2, 1), datetime(2009, 9, 2, 7), False, False, p)])
             , (datetime(2009, 9, 3), [])]
        self.assertEqual(exp, calendar)     

        # make sure it comes back in the correct day for EST
        data = { 'start' : day.strftime("%m/%d/%Y")
               , 'days' : 3
               , 'tz' : 'ET' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 1), [(datetime(2009, 9, 1, 21), datetime(2009, 9, 2), False, False, p)])
             , (datetime(2009, 9, 2), [(datetime(2009, 9, 2), datetime(2009, 9, 2, 3), False, False, p)])
             , (datetime(2009, 9, 3), [])]
        self.assertEqual(exp, calendar)     

        # show the cutoff: '(..)'
        data = { 'start' : day.strftime("%m/%d/%Y")
               , 'days' : 1
               , 'tz' : 'ET' }
        response = self.post('/schedule/public', data)
        calendar = response.context['calendar']
        exp = [(datetime(2009, 9, 1), [(datetime(2009, 9, 1, 21), datetime(2009, 9, 2), False, True, p)])]
        self.assertEqual(exp, calendar)  

        # clean up
        p.remove() #delete()
        s.delete()

# Testing Utilities
class TestDBReporter(NellTestCase):

    def test_DBReporter(self):
        "imply make sure that no exceptions are raised."
        db = DBReporter(quiet=True)
        db.report()

class TestDSSPrime2DSS(NellTestCase):

    def test_DSSPrime2DSS(self):
        t = DSSPrime2DSS()
        t.transfer()

class TestReceiverCompile(NellTestCase):

    def test_normalize(self):
        nn = Receiver.get_abbreviations()
        rc = ReceiverCompile(nn)
        self.assertEquals(rc.normalize(u'Q'), [[u'Q']])
        self.assertEquals(rc.normalize('K & (L | S)'),
                                       [['K'], ['L', 'S']])
        self.assertEquals(rc.normalize('342 | (K & Ka)'),
                                       [['342', 'K'], ['342', 'Ka']])
        self.assertEquals(rc.normalize('(L ^ 342) v (K & Ka)'),
                                       [['L', 'K'],   ['L', 'Ka'],
                                        ['342', 'K'], ['342', 'Ka']])
        self.assertEquals(rc.normalize('K | (Ka | Q)'),
                                       [['K', 'Ka', 'Q']])
        try:
            self.assertEquals(rc.normalize('J'), [['J']])
        except ValueError:
            pass
        else:
            self.fail()
        try:
            self.assertEquals(rc.normalize('K | Ka | Q'),
                                           [['K', 'Ka', 'Q']])
            self.assertEquals(rc.normalize('J'), [['J']])
        except SyntaxError:
            pass
        else:
            self.fail()

class TestConsolidateBlackouts(NellTestCase):

    def test_consolidate_events(self):
        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 1, 18)
          , datetime(2009, 1, 2, 11)
          , datetime(2009, 1, 2, 12)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 4, 18)
          , datetime(2009, 1, 4, 13)
          , datetime(2009, 1, 4, 20)
        ]
        expected = [
            # begin = b5 start, end = b1 end
            (datetime(2009, 1, 2, 12), datetime(2009, 1, 3, 11))
        ]

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 1, 11)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 3, 11)
        ]
        expected = [
            # begin = b1 start, end = b1 end
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 3, 11))
        ]

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        starts = [
            datetime(2009, 1, 1, 11)
          , datetime(2009, 1, 4, 11)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
          , datetime(2009, 1, 5, 11)
        ]
        expected = [
            # nothing to reduce
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 3, 11))
          , (datetime(2009, 1, 4, 11), datetime(2009, 1, 5, 11))
        ]

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        starts = [
            datetime(2009, 1, 1, 11)
        ]
        ends   = [
            datetime(2009, 1, 3, 11)
        ]
        expected = [
            # one conflict
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 3, 11))
        ]

        r = consolidate_events([(s, e) for s, e in zip(starts, ends)])
        self.assertEquals(expected, r)

        # No conflicts.
        r = consolidate_events([])
        self.assertEquals([], r)

class TestUserInfo(NellTestCase):

    def setUp(self):
        super(TestUserInfo, self).setUp()

        self.ui = UserInfo()

        #<?xml version="1.0" encoding="UTF-8"?>
        self.xmlStr =  """
        <nrao:query-result xmlns:nrao="http://www.nrao.edu/namespaces/nrao" >
        <nrao:user id="823" domestic="true" xmlns:nrao="http://www.nrao.edu/namespaces/nrao">
        <nrao:name>
        <nrao:prefix>Mr</nrao:prefix>
        <nrao:first-name>Paul</nrao:first-name>
        <nrao:middle-name>Raffi</nrao:middle-name>
        <nrao:last-name>Marganian</nrao:last-name>
        </nrao:name>
        <nrao:contact-info>
        <nrao:email-addresses>
        <nrao:default-email-address addr="pmargani@nrao.edu">
        <nrao:description>Work</nrao:description>
        </nrao:default-email-address>
        <nrao:additional-email-address addr="paghots@hotmail.com">
        <nrao:description>Other</nrao:description>
        </nrao:additional-email-address>
        <nrao:additional-email-address addr="pmargani@gmail.com">
        <nrao:description>Personal</nrao:description>
        </nrao:additional-email-address>
        </nrao:email-addresses>
        <nrao:postal-addresses>
        <nrao:additional-postal-address>
        <nrao:address-type>Office</nrao:address-type>
        <nrao:streetline>NRAO</nrao:streetline>
        <nrao:streetline>PO Box 2</nrao:streetline>
        <nrao:city>Green Bank</nrao:city>
        <nrao:state>West Virginia</nrao:state>
        <nrao:country>USA</nrao:country>
        <nrao:postal-code>24944</nrao:postal-code>
        </nrao:additional-postal-address>
        <nrao:additional-postal-address>
        <nrao:address-type>Other</nrao:address-type>
        <nrao:streetline>49 columbus Ave.</nrao:streetline>
        <nrao:city>W. Bridgewater</nrao:city>
        <nrao:state>Massachusetts</nrao:state>
        <nrao:country>United States</nrao:country>
        <nrao:postal-code>02379</nrao:postal-code>
        </nrao:additional-postal-address>
        </nrao:postal-addresses>
        <nrao:phone-numbers>
        <nrao:default-phone-number number="304-456-2202">
        <nrao:description>Work</nrao:description>
        </nrao:default-phone-number>
        </nrao:phone-numbers>
        </nrao:contact-info>
        <nrao:affiliation-info>
        <nrao:default-affiliation id="5">
        <nrao:formal-name>National Radio Astronomy Observatory </nrao:formal-name>
        </nrao:default-affiliation>
        <nrao:additional-affiliation id="269">
        <nrao:formal-name>Oregon, University of</nrao:formal-name>
        </nrao:additional-affiliation>
        </nrao:affiliation-info>
        <nrao:misc-info>
        <nrao:user-type>NRAO Staff</nrao:user-type>
        <nrao:web-site>http://www.geocities.com/mangophenomena/</nrao:web-site>
        </nrao:misc-info>
        <nrao:account-info>
        <nrao:account-name>pmargani</nrao:account-name>
        <nrao:encrypted-password>d59c3e6cc6236139bd94307de0e775cc</nrao:encrypted-password>
        <nrao:entry-status>Suspect</nrao:entry-status>
        </nrao:account-info>
        </nrao:user>
        </nrao:query-result>
        """
        self.xml = et.fromstring(self.xmlStr)
        self.xmlDict = \
        {'contact-info': \
            {'phone-numbers':   {'default-phone-number': '304-456-2202'}
           , 'email-addresses': {'default-email-address': 'pmargani@nrao.edu'
                             , 'additional-email-address': ['paghots@hotmail.com', 'pmargani@gmail.com']}
           , 'postal-addresses': [{'city': 'Green Bank'
                                 , 'streetlines': ['NRAO', 'PO Box 2']
                                 , 'address-type': 'Office'
                                 , 'state': 'West Virginia'
                                 , 'country': 'USA'
                                 , 'postal-code': '24944'}
                                 , {'city': 'W. Bridgewater'
                                 , 'streetlines': ['49 columbus Ave.']
                                 , 'address-type': 'Other'
                                 , 'state': 'Massachusetts'
                                 , 'country': 'United States'
                                 , 'postal-code': '02379'}]                  
            }
            , 'name': {'prefix': 'Mr'
                     , 'first-name': 'Paul'
                     , 'middle-name': 'Raffi'
                     , 'last-name': 'Marganian'}
            , 'account-info': {'account-name': 'pmargani'}         
            , 'id': '823'
            , 'affiliation-info': [("National Radio Astronomy Observatory ", True)
                             , ("Oregon, University of", False)]
        }

    def test_parseUserXML(self):
        i = self.ui.parseUserXML(self.xml) 
        self.assertEqual(i, self.xmlDict)

    def test_parseUserDict(self):
        info = self.ui.parseUserDict(self.xmlDict)
        # expected values
        emails = ['pmargani@nrao.edu'
                , 'paghots@hotmail.com'
                , 'pmargani@gmail.com']
        phones = ['304-456-2202']        
        postals = \
            ['NRAO, PO Box 2, Green Bank, West Virginia, 24944, USA, (Office)'
           , '49 columbus Ave., W. Bridgewater, Massachusetts, 02379, United States, (Other)']
        affiliations = ['National Radio Astronomy Observatory '
                      , 'Oregon, University of']
        self.assertEquals(emails, info['emails'])        
        self.assertEquals(phones, info['phones'])
        self.assertEquals(postals, info['postals'])
        self.assertEquals(affiliations, info['affiliations'])
        self.assertEquals('pmargani', info['username'])

class TestNRAOBosDB(NellTestCase):

    def setUp(self):
        super(TestNRAOBosDB, self).setUp()

        self.bos = NRAOBosDB()

        #<?xml version="1.0" encoding="utf-8"?>
        self.xmlStr =  """
        <nrao:user domestic="true" id="dbalser" xmlns:nrao="http://www.nrao.edu/namespaces/nrao">
            <nrao:reservation id="2704">
                <nrao:startDate>2009-08-25</nrao:startDate>
                <nrao:endDate>2009-08-28</nrao:endDate>
            </nrao:reservation>
        </nrao:user>
        """
        self.xml = et.fromstring(self.xmlStr)

    def test_parseReservationsXML(self):

        dates = self.bos.parseReservationsXML(self.xmlStr)
        exp = [(datetime(2009, 8, 25, 0, 0), datetime(2009, 8, 28, 0, 0))]
        self.assertEqual(dates, exp)

class TestScheduleTools(NellTestCase):

    def setUp(self):
        super(TestScheduleTools, self).setUp()

        # setup some periods
        self.start = datetime(2000, 1, 1, 0)
        self.end   = self.start + timedelta(hours = 12)
        times = [(datetime(2000, 1, 1, 0), 5.0, "one")
               , (datetime(2000, 1, 1, 5), 3.0, "two")
               , (datetime(2000, 1, 1, 8), 4.0, "three")
               ]
        self.ps = []
        # init them as Scheduled, so that 'deleting' them just changes state
        state = first(Period_State.objects.filter(abbreviation = 'S'))        
        for start, dur, name in times:
            s = create_sesshun()
            s.name = name
            s.save()
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            p = Period( session    = s
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()          
            self.ps.append(p)

        self.backup = create_sesshun()
        self.backup.name = "backup"
        self.backup.status.backup = True
        self.backup.save()

    def tearDown(self):
        super(TestScheduleTools, self).tearDown()

        for p in self.ps:
            p.session.delete()
            p.remove() #delete()


    def test_changeSchedule1(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # try to mirror examples from Memo 11.2
        # Example 2 (Ex. 1 is a no op)
        change_start = self.ps[0].start + timedelta(hours = 2)
        ScheduleTools().changeSchedule(change_start 
                                    , 3.0 
                                    , self.backup
                                    , "other_session_other"
                                    , "SP broke.")
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [5.0, 3.0, 3.0, 4.0]
        observed  = [2.0, 3.0, 3.0, 4.0]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(observed[i] , p.accounting.observed())
        # check affected periods
        canceled = ps[0]
        backup   = ps[1]
        self.assertEquals(self.start, canceled.start)
        self.assertEquals(2.0, canceled.duration)
        self.assertEquals(3.0, canceled.accounting.other_session_other)
        self.assertTrue("SP broke." in canceled.accounting.description)
        self.assertEquals(3.0, backup.accounting.short_notice)
        self.assertTrue("SP broke." in backup.accounting.description)

    def test_changeSchedule2(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # try to mirror examples from Memo 11.2
        # Example 3 - last 3 hrs of first period replaced w/ nothing 
        change_start = self.ps[0].start + timedelta(hours = 2)
        desc = "SP croaked."
        ScheduleTools().changeSchedule(change_start 
                                    , 3.0 
                                    , None
                                    , "lost_time_other"
                                    , desc)
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [5.0, 3.0, 4.0]
        observed  = [2.0, 3.0, 4.0]
        times = [p.start for p in self.ps]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(observed[i] , p.accounting.observed())
            self.assertEquals(times[i] , p.start)
        # check affected periods
        canceled = ps[0]
        self.assertEquals(self.start, canceled.start)
        self.assertEquals(2.0, canceled.duration)
        self.assertEquals(3.0, canceled.accounting.lost_time_other)
        self.assertTrue(desc in canceled.accounting.description)

    def test_changeSchedule3(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # try to mirror examples from Memo 11.2
        # Example 4 (Second Period start early at expense of first)
        change_start = self.ps[1].start - timedelta(hours = 1)
        backup = self.ps[1].session
        desc = "Session Two starting hour early; not billed time for Two."
        ScheduleTools().changeSchedule(change_start 
                                    , 1.0 
                                    , backup
                                    , "other_session_weather"
                                    , desc)
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [5.0, 1.0, 3.0, 4.0]
        observed  = [4.0, 1.0, 3.0, 4.0]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(observed[i] , p.accounting.observed())
        # check affected periods
        canceled = ps[0]
        backup   = ps[1]
        self.assertEquals(self.start, canceled.start)
        self.assertEquals(4.0, canceled.duration)
        self.assertEquals(1.0, canceled.accounting.other_session_weather)
        self.assertTrue(desc in canceled.accounting.description)
        self.assertEquals(1.0, backup.accounting.short_notice)
        self.assertTrue(desc in backup.accounting.description)                        
        # now, don't bill this new period the hour
        self.assertEquals(1.0, backup.accounting.observed())
        self.assertEquals(1.0, backup.accounting.time_billed())
        backup.accounting.not_billable = 1.0
        backup.accounting.save()
        self.assertEquals(1.0, backup.accounting.observed())
        self.assertEquals(0.0, backup.accounting.time_billed())

    def test_changeSchedule4(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # try to mirror examples from Memo 11.2
        # Example 5 (scheduled first period replaced w/ backup)
        change_start = self.ps[0].start 
        desc = "Hurricane Georges"
        ScheduleTools().changeSchedule(change_start 
                                    , 5.0 
                                    , self.backup
                                    , "other_session_weather"
                                    , desc)
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0, ignore_deleted = False)
        # TBF: how to handle these Periods that r compleletly replaced?
        canceled_ps = [p for p in ps if p.state.abbreviation == 'D']
        ps = [p for p in ps if p.state.abbreviation != 'D']
        # check accounting after changing schedule
        scheduled = [5.0, 3.0, 4.0]
        observed  = [5.0, 3.0, 4.0]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(observed[i] , p.accounting.observed())
        # check affected periods
        canceled = first(Period.objects.filter(state__abbreviation = 'D'))
        backup   = ps[0]
        self.assertEquals(self.start, canceled.start)
        self.assertEquals(5.0, canceled.duration)
        self.assertEquals(5.0, canceled.accounting.other_session_weather)
        self.assertTrue(desc in canceled.accounting.description)
        self.assertEquals(5.0, backup.accounting.short_notice)
        self.assertTrue(desc in backup.accounting.description)

    def test_changeSchedule_end_early(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # have a new session override the last one, and make the middle
        # one end early
        change_start = self.ps[1].start + timedelta(hours = 2.0)
        desc = "fix this bug"
        ScheduleTools().changeSchedule(change_start 
                                    , 5.0 
                                    , self.backup
                                    , "other_session_other"
                                    , desc)
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0, ignore_deleted = False)
        # make sure we don't get deleted period
        ps = [p for p in ps if p.state.abbreviation != 'D']
        self.assertEquals(3, len(ps))

        # check accounting after changing schedule
        scheduled = [5.0, 3.0, 5.0]
        observed  = [5.0, 2.0, 5.0]
        oso       = [0.0, 1.0, 0.0]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(oso[i] , p.accounting.other_session())
            self.assertEquals(observed[i] , p.accounting.observed())
        # check affected periods
        canceled = first(Period.objects.filter(state__abbreviation = 'D'))
        self.assertEquals(canceled.start, self.ps[2].start)
        
    def test_changeSchedule_ultimate_chaos(self):
        "gitrdone!"

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # have a new session start before the first ends, and go all
        # the way to near the end of the last
        # one end early
        change_start = self.ps[0].start + timedelta(hours = 2.0)
        desc = "chaos!"
        ScheduleTools().changeSchedule(change_start 
                                    , 8.0 
                                    , self.backup
                                    , "other_session_other"
                                    , desc)
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0, ignore_deleted = False)
        # make sure we don't get deleted period
        ps = [p for p in ps if p.state.abbreviation != 'D']
        self.assertEquals(3, len(ps))

        # check accounting after changing schedule
        scheduled = [5.0, 8.0, 4.0]
        observed  = [2.0, 8.0, 2.0]
        oso       = [3.0, 0.0, 2.0]
        sn        = [0.0, 8.0, 0.0]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
        # check affected periods
        canceled = first(Period.objects.filter(state__abbreviation = 'D'))
        self.assertEquals(canceled.start, self.ps[1].start)
        
    def test_changeSchedule_bisect(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        # make sure we can handle bi-secting a pre-existing period
        change_start = self.ps[0].start + timedelta(hours = 1.0)
        desc = "bisect!"
        ScheduleTools().changeSchedule(change_start 
                                    , 2.0 
                                    , self.backup
                                    , "other_session_other"
                                    , desc)
        
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        self.assertEquals(5, len(ps))
        # check accounting after changing schedule
        scheduled = [5.0, 8.0, 4.0]
        observed  = [1.0, 2.0, 2.0, 3.0, 4.0]
        oso       = [3.0, 0.0, 2.0]
        sn        = [0.0, 8.0, 0.0]
        for i, p in enumerate(ps):
            #self.assertEquals(scheduled[i], p.accounting.scheduled)
            #self.assertEquals(sn[i],        p.accounting.short_notice)
            #self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())

    def test_shiftPeriodBoundaries_start_later(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        new_start = self.ps[1].start + timedelta(hours = 1.0)
        desc = "starting second period an hour latter"
        ScheduleTools().shiftPeriodBoundaries(self.ps[1]
                                     , True # start boundary
                                     , new_start 
                                     , self.ps[0]
                                     , "other_session_other"
                                     , desc)
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [6.0, 3.0, 4.0]
        observed  = [6.0, 2.0, 4.0]
        oso       = [0.0, 1.0, 0.0]
        sn        = [1.0, 0.0, 0.0]
        dur       = [6.0, 2.0, 4.0]
        starts    = [self.ps[0].start
                   , new_start
                   , self.ps[2].start]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
            self.assertEquals(dur[i],       p.duration)
            self.assertEquals(starts[i],    p.start)

        self.assertTrue(desc in ps[0].accounting.description)
        self.assertTrue(desc in ps[1].accounting.description)

    def test_shiftPeriodBoundaries_start_earlier(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        new_start = self.ps[1].start - timedelta(hours = 1.0)
        desc = "starting second period an hour early"
        ScheduleTools().shiftPeriodBoundaries(self.ps[1]
                                     , True # start boundary
                                     , new_start 
                                     , self.ps[0]
                                     , "other_session_other"
                                     , desc)
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [5.0, 4.0, 4.0]
        observed  = [4.0, 4.0, 4.0]
        oso       = [1.0, 0.0, 0.0]
        sn        = [0.0, 1.0, 0.0]
        dur       = [4.0, 4.0, 4.0]
        starts    = [self.ps[0].start
                   , new_start
                   , self.ps[2].start]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
            self.assertEquals(dur[i],       p.duration)
            self.assertEquals(starts[i],    p.start)

        self.assertTrue(desc in ps[0].accounting.description)
        self.assertTrue(desc in ps[1].accounting.description)

    def test_shiftPeriodBoundaries_end_earlier(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        new_end = self.ps[1].end() - timedelta(hours = 1.0)
        desc = "ending second period an hour early"
        ScheduleTools().shiftPeriodBoundaries(self.ps[1]
                                     , False # end boundary
                                     , new_end 
                                     , self.ps[2]
                                     , "other_session_other"
                                     , desc)
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [5.0, 3.0, 5.0]
        observed  = [5.0, 2.0, 5.0]
        oso       = [0.0, 1.0, 0.0]
        sn        = [0.0, 0.0, 1.0]
        dur       = [5.0, 2.0, 5.0]
        starts    = [self.ps[0].start
                   , self.ps[1].start
                   , new_end]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
            self.assertEquals(dur[i],       p.duration)
            self.assertEquals(starts[i],    p.start)

        self.assertTrue(desc in ps[1].accounting.description)
        self.assertTrue(desc in ps[2].accounting.description)

    def test_shiftPeriodBoundaries_end_latter(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        new_end = self.ps[1].end() + timedelta(hours = 1.0)
        desc = "ending second period an hour latter"
        ScheduleTools().shiftPeriodBoundaries(self.ps[1]
                                     , False # end boundary
                                     , new_end 
                                     , self.ps[2]
                                     , "other_session_other"
                                     , desc)
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0)
        # check accounting after changing schedule
        scheduled = [5.0, 4.0, 4.0]
        observed  = [5.0, 4.0, 3.0]
        oso       = [0.0, 0.0, 1.0]
        sn        = [0.0, 1.0, 0.0]
        dur       = [5.0, 4.0, 3.0]
        starts    = [self.ps[0].start
                   , self.ps[1].start
                   , new_end]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
            self.assertEquals(dur[i],       p.duration)
            self.assertEquals(starts[i],    p.start)

        self.assertTrue(desc in ps[1].accounting.description)
        self.assertTrue(desc in ps[2].accounting.description)

    def test_shiftPeriodBoundaries_start_way_earlier(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        new_start = self.ps[2].start - timedelta(hours = 4.0)
        desc = "starting third period four hours early"
        ScheduleTools().shiftPeriodBoundaries(self.ps[2]
                                     , True # start boundary
                                     , new_start 
                                     , self.ps[1]
                                     , "other_session_other"
                                     , desc)
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0, ignore_deleted = False)
        # check accounting after changing schedule
        names     = ["one", "three", "two"]
        scheduled = [5.0, 8.0, 3.0]
        observed  = [4.0, 8.0, 0.0]
        oso       = [1.0, 0.0, 3.0]
        sn        = [0.0, 4.0, 0.0]
        dur       = [4.0, 8.0, 3.0]
        states    = ['S', 'S', 'D']
        starts    = [self.ps[0].start
                   , new_start
                   , self.ps[1].start]
        for i, p in enumerate(ps):
            self.assertEquals(names[i],     p.session.name)
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
            self.assertEquals(dur[i],       p.duration)
            self.assertEquals(starts[i],    p.start)
            self.assertEquals(states[i],    p.state.abbreviation)
            self.assertTrue(desc in p.accounting.description)

    def test_shiftPeriodBoundaries_end_way_latter(self):

        # check accounting before changing schedule
        scheduled = [5.0, 3.0, 4.0]
        for i, p in enumerate(self.ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(scheduled[i], p.accounting.observed())

        new_end = self.ps[0].end() + timedelta(hours = 4.0)
        desc = "ending first period four hours latter"
        ScheduleTools().shiftPeriodBoundaries(self.ps[0]
                                     , False # end boundary
                                     , new_end 
                                     , self.ps[1]
                                     , "other_session_other"
                                     , desc)
        # get the periods from the DB again for updated values
        ps = Period.get_periods(self.start, 12.0*60.0, ignore_deleted = False)
        # check accounting after changing schedule
        scheduled = [9.0, 3.0, 4.0]
        observed  = [9.0, 0.0, 3.0]
        oso       = [0.0, 3.0, 1.0]
        sn        = [4.0, 0.0, 0.0]
        dur       = [9.0, 3.0, 3.0]
        states    = ['S', 'D', 'S']
        starts    = [self.ps[0].start
                   , self.ps[1].start
                   , new_end]
        for i, p in enumerate(ps):
            self.assertEquals(scheduled[i], p.accounting.scheduled)
            self.assertEquals(sn[i],        p.accounting.short_notice)
            self.assertEquals(oso[i],       p.accounting.other_session())
            self.assertEquals(observed[i],  p.accounting.observed())
            self.assertEquals(dur[i],       p.duration)
            self.assertEquals(starts[i],    p.start)
            self.assertEquals(states[i],    p.state.abbreviation)
            self.assertTrue(desc in p.accounting.description)

class TestTimeAccounting(NellTestCase):

    def setUp(self):
        super(TestTimeAccounting, self).setUp()

        # setup some periods
        self.start = datetime(2000, 1, 1, 0)
        self.end   = self.start + timedelta(hours = 12)
        times = [(datetime(2000, 1, 1, 0), 5.0, "one")
               , (datetime(2000, 1, 1, 5), 3.0, "two")
               , (datetime(2000, 1, 1, 8), 4.0, "three")
               ]
        self.ps = []
        state = first(Period_State.objects.filter(abbreviation = 'P'))        
        for start, dur, name in times:
            s = create_sesshun()
            s.name = name
            s.save()
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            p = Period( session    = s
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()          
            self.ps.append(p)

    def tearDown(self):
        super(TestTimeAccounting, self).tearDown()

        for p in self.ps:
            p.session.delete()
            p.delete()

    def test_getTimeLeft(self):
        project = Project.objects.order_by('pcode').all()[0]
        ta = TimeAccounting()

        timeLeft = ta.getTimeLeft(project)
        self.assertEqual(-3.0, timeLeft)

        names = ["one", "three", "two"]
        times = [-2.0, -1.0, 0.0]

        for i, s in enumerate(project.sesshun_set.order_by("name").all()):
            timeLeft = ta.getTimeLeft(s)
            self.assertEqual(names[i], s.name)
            self.assertEqual(times[i], timeLeft)


    def test_getTime(self):

        project = Project.objects.order_by('pcode').all()[0]
        ta = TimeAccounting()

        pScheduled = ta.getTime('scheduled', project)
        self.assertEqual(pScheduled, 12.0)

        pNotBillable = ta.getTime('not_billable', project)
        self.assertEqual(pNotBillable, 0.0)

        # now change something and watch it bubble up
        self.ps[0].accounting.not_billable = 1.0
        self.ps[0].accounting.save()
        project = Project.objects.order_by('pcode').all()[0]

        pNotBillable = ta.getTime('not_billable', self.ps[0].session)
        self.assertEqual(pNotBillable, 1.0)

        pNotBillable = ta.getTime('not_billable', project)
        self.assertEqual(pNotBillable, 1.0)



    def test_jsondict(self):

        project = Project.objects.order_by('pcode').all()[0]
        ta = TimeAccounting()

        dct = ta.jsondict(project)
        self.assertEqual(3, len(dct['sessions']))
        self.assertEqual(1, len(dct['sessions'][0]['periods']))

        # test identity
        ta.update_from_post(project, dct)
        # get it fressh from the DB
        project = Project.objects.order_by('pcode').all()[0]
        dct2 = ta.jsondict(project)
        self.assertEqual(dct, dct2)

        # now change something
        dct['sessions'][0]['periods'][0]['not_billable'] = 1.0
        ta.update_from_post(project, dct)
        # get it fressh from the DB
        project = Project.objects.order_by('pcode').all()[0]
        dct2 = ta.jsondict(project)
        # they're different becuase not_billable bubbles up
        self.assertNotEqual(dct, dct2)
        b = dct2['not_billable'] 
        self.assertEqual(b, 1.0)

    def test_report(self):

        # just make sure it doesn't blow up
        project = Project.objects.order_by('pcode').all()[0]
        ta = TimeAccounting()
        ta.quietReport = True
        ta.report(project)
        
