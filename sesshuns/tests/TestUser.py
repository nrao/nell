from nell.test_utils              import NellTestCase
from sesshuns.models              import *
from sesshuns.httpadapters        import *
from utils                        import create_sesshun

class TestUser(NellTestCase):
    def setUp(self):
        # TBF: From here down, till noted, is the same code as TestProject
        super(TestUser, self).setUp()

        self.project = Project()
        pdata = {"semester"   : "09A"
               , "pcode"      : "GBT09A-009"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
        }
        adapter = ProjectHttpAdapter(self.project)
        adapter.update_from_post(pdata)

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
        self.user3 = User(sanctioned = True
                        , role = obsRole
                        , first_name = "Best"
                        , last_name = "Friend"
                         )
        self.user3.save()
        friend = Friend(user = self.user3, project = self.project)
        friend.save()

        # add an unrelated user
        self.user4 = User(sanctioned = True, role = obsRole)
        self.user4.save()

    def tearDown(self):
        super(TestUser, self).tearDown()
        self.investigator2.delete()
        self.user2.delete()
        self.investigator1.delete()
        self.user1.delete()
        self.period1.remove() #delete()
        self.period2.remove() #delete()
        self.project.delete()
        self.user3.delete()
        self.user4.delete()

    def test_getFriendLastNames(self):

        self.assertEquals(['Friend'], self.user1.getFriendLastNames())
        self.assertEquals(['Friend'], self.user2.getFriendLastNames())
        self.assertEquals([], self.user3.getFriendLastNames())
        self.assertEquals([], self.user4.getFriendLastNames())

    def test_isFriend(self):

        self.assertEquals(self.user1.isFriend('GBT09A-009'), False)
        self.assertEquals(self.user3.isFriend('GBT09A-009'), True)

    def test_getProjects(self):
    
        self.assertEquals(self.user1.getProjects(), ['GBT09A-009'])
        self.assertEquals(self.user2.getProjects(), ['GBT09A-009'])
        self.assertEquals(self.user3.getProjects(), [])
        self.assertEquals(self.user4.getProjects(), [])

    def test_getFriendedProjects(self):

        self.assertEquals(self.user1.getFriendedProjects(), [])
        self.assertEquals(self.user2.getFriendedProjects(), [])
        self.assertEquals(self.user3.getFriendedProjects(),[self.project])
        self.assertEquals(self.user4.getFriendedProjects(), [])

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

