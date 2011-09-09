import MySQLdb as mysql
from datetime                import datetime
from tools.database          import DSSPrime2DSS
from tools.database          import Schedtime2DSS
from scheduler.models        import *
from test_utils              import NellTestCase

class TestSchedtime2DSS(NellTestCase):

    def assert_DB_empty(self):
        # make sure our DB is almost blank
        projects = Project.objects.all()
        self.assertEquals(1, len(projects))
        ss = Sesshun.objects.all()
        self.assertEquals(0, len(ss))
        users = User.objects.all()
        self.assertEquals(0, len(users))
        ps = Period.objects.all()


    def test_transfer_fixed_periods(self):
        
        # Clarify the inital state of the DB
        self.assert_DB_empty()

        # This is not very *unit* testy, but most of these tests
        # won't work if we don't already have a DSS database setup
        # with the projects and sessions that the schedtime table
        # refers to.  So, we need to do this step first
        t = DSSPrime2DSS(database = 'dss_prime_unit_tests_schedtime')
        t.quiet = True
        t.transfer()

        # Make sure it has really been setup
        projects = Project.objects.all()
        # len(93) == 92 + 1 prexisting project in models
        self.assertEquals(93, len(projects))
        self.assertEquals(267, len(Sesshun.objects.all()))
        origSessions = Sesshun.objects.all().order_by("name")
        origNames = [s.name for s in origSessions]

        # Now transfer the fixed periods over from the schedtime table.
        # Again, not a real *unit* test since we're connecting to this DB
        sem = "09C"
        sd = Schedtime2DSS.Schedtime2DSS(database = 'dss_prime_unit_tests_schedtime')
        sd.transfer_fixed_periods(sem)

        # How many new projects, sessions, periods do we have now?
        self.assertEquals(93, len(projects))
        self.assertEquals(294, len(Sesshun.objects.all()))
        self.assertEquals(133, len(Period.objects.all()))

        # what sessions got created?
        nowSessions =  Sesshun.objects.all().order_by("name")
        nowNames = [s.name for s in nowSessions]
        newNames = [n for n in nowNames if n not in origNames]
        expNewNames = [u'BZ tests-Harris'
                     , u'GainCal-Ghigo'
                     , u'GUPPI-Ford,Ransom'
                     , u'GUPPI-Ransom'
                     , u'GUPPI-Ransom,Ford'
                     , u'HOLO'
                     , u'Ka/CCB pointing'
                     , u'KFPA'
                     , u'KFPA IF'
                     , u'KFPA Line obs'
                     , u'KFPA mapping'
                     , u'KFPA P/F'
                     , u'Maintenance'
                     , u'M&C Integ'
                     , u'M&C Reg'
                     , u'Mustang-Mason'
                     , u'Mustang OOF-Mason'
                     , u'OOF'
                     , u'Quadrant detector'
                     , u'RCO-Minter'
                     , u'Scal-Minter'
                     , u'Scal-Minter,Maddalena'
                     , u'Servo'
                     , u'Shutdown'
                     , u'Shutdown-Minter'
                     , u'Startup-Minter'
                     , u'Test map for KFPA']
        self.assertEquals(expNewNames, newNames)

        # spot check the periods
        ps = [(p.session.name, p.start, p.duration) for p in Period.objects.all().order_by("start")]
        self.assertEquals(("Maintenance",     datetime(2009, 10,  1, 11), 10.5), ps[0])
        self.assertEquals(("BZ tests-Harris", datetime(2009, 10,  7,  9),  3.0), ps[1])
        self.assertEquals(("Maintenance",     datetime(2010,  1, 27, 13),  8.5), ps[len(ps)-1])

        # The original DB for this unit test, dss_prime_09C_final had some periods whose named sessions & projects
        # did not exist in the other tables!  We fixed this by copying the DB over to dss_prime_unit_tests_schedtime
        # and removing all the non-GBT09C% Astronomy periods.  Here's the code for discovering the problem:
#        q1 = "select distinct(pcode) from projects where pcode like 'GBT09C%';"
#        sd.cursor.execute(q1)
#        projPcodes = sd.cursor.fetchall()

        #q2 = "select distinct(pcode) from schedtime;" 
#        q2 = "SELECT distinct(pcode)  FROM schedtime WHERE pcode LIKE 'GBT09C%';"
#        sd.cursor.execute(q2)
#        schedtimePcodes = sd.cursor.fetchall()
#        schedtimePcodes = []
#        for p in allPcodes:
#            if p not in schedtimePcodes:
#                schedtimePcodes.append(p)

#        bads = []
#        for p in schedtimePcodes:
#            #print "testing: ", p, bads
#            if p not in projPcodes and p not in bads:
#                bads.append(p)

#        print "Of %d distinct projects listed schedtime, %d are not in projects" % (len(schedtimePcodes), len(bads))

    def test_create_project_and_session(self):

        # Clarify the inital state of the DB
        self.assert_DB_empty()

        sd = Schedtime2DSS.Schedtime2DSS(database = 'dss_prime_unit_tests_schedtime')

        sd.create_project_and_session( "09C"
                                     , "Shutdown"
                                     , "non-science"
                                     , "Shutdown"
                                     , "maintenance")        

        projects = Project.objects.all().order_by("pcode")
        self.assertEquals(2, len(projects))
        ss = Sesshun.objects.all()
        self.assertEquals(1, len(ss))
        users = User.objects.all()
        self.assertEquals(0, len(users))
        ps = Period.objects.all()                                       

        self.assertEquals([u'GBT09A-001', u'Shutdown'], [p.pcode for p in projects])
        self.assertEquals("Shutdown", ss[0].name)
        self.assertEquals("maintenance", ss[0].observing_type.type)

    def test_get_schedtime_dates(self):
        sd = Schedtime2DSS.Schedtime2DSS(database = 'dss_prime_unit_tests_schedtime')
        start, end = sd.get_schedtime_dates("09C")
        self.assertEquals("20091001", start)
        self.assertEquals("20100131", end)
        start, end = sd.get_schedtime_dates("10A")
        self.assertEquals("20100201", start)
        self.assertEquals("20100531", end)

    def test_get_testing_session(self):

        # Clarify the inital state of the DB
        self.assert_DB_empty()

        sd = Schedtime2DSS.Schedtime2DSS(database = 'dss_prime_unit_tests_schedtime')
        row = ('20100126', '1630', '1800', '1.500', 'Tests', '', '0', 'Td:RCO-Minter', 'PF2', '', '') 
        dur = 1.5 
        semester = "09C"

        newSess = sd.get_testing_session(row, dur, semester)

        # this should have created a new session and project
        projects = Project.objects.all().order_by("pcode")
        self.assertEquals(2, len(projects))
        ss = Sesshun.objects.all()
        self.assertEquals(1, len(ss))
        users = User.objects.all()
        self.assertEquals(0, len(users))
        ps = Period.objects.all()                                       

        self.assertEquals([u'GBT09A-001', u'TGBT09C_500'], [p.pcode for p in projects])
        self.assertEquals("RCO", newSess.name)
        self.assertEquals(0.0, newSess.frequency)
        self.assertEquals(1.5, newSess.allotment.total_time)
        self.assertEquals("(1070)", newSess.receiver_list())
  
        # here we will *not* create a new session, just update the last one
        row = ('20100105', '1630', '1800', '1.500', 'Tests', '', '0', 'Td:RCO-Minter', '8', '', '') 
        dur = 1.5 
        semester = "09C"

        newSess = sd.get_testing_session(row, dur, semester)
        projects = Project.objects.all().order_by("pcode")
        self.assertEquals(2, len(projects))
        ss = Sesshun.objects.all()
        self.assertEquals(1, len(ss))
        users = User.objects.all()
        self.assertEquals(0, len(users))
        ps = Period.objects.all()                                       

        self.assertEquals([u'GBT09A-001', u'TGBT09C_500'], [p.pcode for p in projects])
        self.assertEquals("RCO", newSess.name)
        self.assertEquals(0.0, newSess.frequency)
        # only the alloted time is updated!!!
        self.assertEquals(3.0, newSess.allotment.total_time)
        self.assertEquals("(1070)", newSess.receiver_list())

    def test_get_schedtime_observers(self):


        # Clarify the inital state of the DB
        self.assert_DB_empty()

        # setup a user
        u = User(last_name = "White"
               , first_name = "Steve"
               , role = Role.objects.all()[0]
                )
        u.save()        

        sd = Schedtime2DSS.Schedtime2DSS(database = 'dss_prime_unit_tests_schedtime')

        # nothing gets added to the DB unless the last name matches
        obs = sd.get_schedtime_observers("Minter")
        self.assertEquals([], obs)

        obs = sd.get_schedtime_observers('White & Langston')
        self.assertEquals([u], obs)

    def test_get_schedtime_rcvrs(self):


        sd = Schedtime2DSS.Schedtime2DSS(database = 'dss_prime_unit_tests_schedtime')

        r = sd.get_schedtime_rcvrs("PF1*4")
        self.assertEquals("450", r[0].abbreviation)
        r = sd.get_schedtime_rcvrs("RRI")
        self.assertEquals("RRI", r[0].abbreviation)
        r = sd.get_schedtime_rcvrs("L")
        self.assertEquals("L", r[0].abbreviation)

