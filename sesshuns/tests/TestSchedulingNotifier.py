from datetime   import datetime, timedelta

from nell.utilities  import SchedulingNotifier
from scheduler.tests.utils           import create_sesshun
from scheduler.tests.PeriodsTestCase import PeriodsTestCase
from scheduler.models import *
#from nell.utilities.ReversionUtilityTester  import VersionDiff
from nell.utilities.RevisionUtilityTester import VersionTester
from nell.utilities.VersionDiff import VersionDiff

class TestSchedulingNotifier(PeriodsTestCase):

    def setUp(self):
        super(TestSchedulingNotifier, self).setUp()

        self.sn = SchedulingNotifier.SchedulingNotifier(test = True)

        # SchedulingNotifier relies on PeriodChanges to know what changes
        # to notify people about.  PeriodChanges uses the revision system
        # to track pertinent changes, but that system doesn't work w/
        # unit tests, so heres how we fake it:
        for p in self.ps:
            self.addToTestRevisions(p)
            self.addToTestRevisions(p.accounting)

    def addToTestRevisions(self, o):
        "When Unit Testing with PeriodChanges, gotta do this:"

        self.sn.periodChanges.revisions.versions[o] = {} 
        self.sn.periodChanges.revisions.diffs[o] = {}

    def setVersions(self, o, vs):
        "When Unit Testing with PeriodChanges, gotta do this:"
        self.sn.periodChanges.revisions.versions[o] = vs 

    def setDiffs(self, o, diffs):
        "When Unit Testing with PeriodChanges, gotta do this:"
        self.sn.periodChanges.revisions.diffs[o] = diffs 

    def test_examinePeriods(self):

        self.sn.examinePeriods(self.ps, self.ps)
        self.assertEquals(self.ps, self.sn.observingPeriods)
        self.assertEquals([], self.sn.changedPeriods)
        self.assertEquals([], self.sn.deletedPeriods)

    def test_examinePeriods_2(self):

        # now delete one of these periods
        #p = self.ps[0]
        self.ps[0].state = Period_State.get_state("D")
        self.ps[0].accounting.lost_time_other = self.ps[0].duration
        self.ps[0].save()

        # The above change must be caught by the scheduling notifier,
        # but teh revision system that it relies on doesn't work in unit
        # tests, so we have to fake it here.
        # What would the revision system look like?
        dt1 = self.start + timedelta(minutes = 1)
        dt2 = self.start + timedelta(minutes = 2)
        versions = [VersionTester(fields = {'state' : 2}
                                , dt = dt1)
                  , VersionTester(fields = {'state' : 3}
                                , dt = dt2)
                    ]
        self.setVersions(self.ps[0], versions)
        stateDiff = VersionDiff(dt = dt2
                              , field = 'state'
                              , value1 = 2
                              , value2 = 3)
        self.setDiffs(self.ps[0], [stateDiff])                   
        ltoDiff = VersionDiff(dt = dt2
                            , field = 'lost_time_other'
                            , value1 = 0
                            , value2 = self.ps[0].duration)
        self.setDiffs(self.ps[0].accounting, [ltoDiff])                   
                           
        # also create a windowed session with default period that
        # is in the deleted state
        s = create_sesshun()
        s.session_type = Session_Type.objects.get(type = "windowed")
        s.save()

        # new default period for a window that is after the original periods
        start_time = self.ps[2].start + timedelta(hours = self.ps[2].duration)
        dur = 3.0

        pa = Period_Accounting(scheduled = 0)
        pa.save()
        state = Period_State.objects.get(abbreviation = "D")
        p = Period( session    = s
                  , start      = start_time
                  , duration   = dur
                  , state      = state
                  , accounting = pa
                  )
        p.save()
        w1 = Window( session = s
                   #, start_date = p.start.date() - timedelta(days = 7)
                   #, duration = 10 # days
                   , default_period = p
                   )
        w1.save()
        wr = WindowRange(window = w1
                   , start_date = p.start.date() - timedelta(days = 7)
                   , duration = 10 # days
                         )
        wr.save()                 

        self.addToTestRevisions(p)

        ps = [self.ps[0]
            , self.ps[1]
            , self.ps[2]
            , p
             ]
        self.sn.examinePeriods(ps, ps)

        obsPeriods = self.ps[1:]
        self.assertEquals(obsPeriods, self.sn.observingPeriods)
        self.assertEquals([self.ps[0]], self.sn.changedPeriods)
        self.assertEquals([self.ps[0]], self.sn.deletedPeriods)

        self.assertEquals(1, len(self.sn.changes.keys()))
        self.assertEquals(2, len(self.sn.changes[self.ps[0]]))
        self.assertEquals(stateDiff, self.sn.changes[self.ps[0]][0])
        self.assertEquals(ltoDiff,   self.sn.changes[self.ps[0]][1])

    def setupUser(self):

        # assign some observers to the periods
        u = User(last_name = "Nubbles"
               , first_name = "Dr."
               , role = Role.objects.get(role = "Observer")
               , pst_id = 821 # give it Marganian's contact info
                )
        u.save()        

        for p in self.ps:
            inv = Investigator(user = u
                             , project = p.session.project
                             , observer = True
                             , principal_investigator = True
                              )
            inv.save() 

    def test_setPeriods(self):
        "setPeriods sets up all the subsequent emails."

        self.setupUser()

        self.sn.setPeriods(self.ps, self.ps)

        # test the staff email
        email = self.sn.email_templates.getObject("staff")
        self.assertEquals(["gbtops@gb.nrao.edu", "gbtinfo@gb.nrao.edu", "gbtime@gb.nrao.edu"]
                        , email.recipients)
        self.assertEquals(email.subject, "GBT schedule for Dec 31-Jan 01")  
        partialBody = """Dec 31 19:00 | Jan 01 00:00 | 01:18 |  5.00 | Nubbles   |           | one
Jan 01 00:00 | Jan 01 05:00 | 06:19 |  3.00 | Nubbles   |           | two
Jan 01 03:00 | Jan 01 08:00 | 09:19 |  4.00 | Nubbles   |           | three"""
        self.assertTrue(partialBody in email.body)       

        # test the observer email
        email = self.sn.email_templates.getObject("observer")
        exp = [u'pmargani@nrao.edu', u'pmargani@gmail.com', u'paghots@hotmail.com']
        self.assertEquals(exp, email.recipients)
        self.assertEquals("Your GBT project has been scheduled (Dec 31-Jan 01)", email.subject)
        self.assertTrue(partialBody in email.body)       

        # test the changed email - no changes, no recipients
        email = self.sn.email_templates.getObject("changed")
        self.assertEquals([], email.recipients)

    def test_setPeriods_changes(self):

        self.setupUser()

        # now delete one of these periods
        self.ps[0].state = Period_State.get_state("D")
        self.ps[0].accounting.lost_time_other = self.ps[0].duration
        self.ps[0].save()

        # The above change must be caught by the scheduling notifier,
        # but teh revision system that it relies on doesn't work in unit
        # tests, so we have to fake it here.
        # What would the revision system look like?
        dt1 = self.start + timedelta(minutes = 1)
        dt2 = self.start + timedelta(minutes = 2)
        versions = [VersionTester(fields = {'state' : 2}
                                , dt = dt1)
                  , VersionTester(fields = {'state' : 3}
                                , dt = dt2)
                    ]
        self.setVersions(self.ps[0], versions)
        stateDiff = VersionDiff(dt = dt2
                              , field = 'state'
                              , value1 = 2
                              , value2 = 3)
        self.setDiffs(self.ps[0], [stateDiff])                   
        ltoDiff = VersionDiff(dt = dt2
                            , field = 'lost_time_other'
                            , value1 = 0
                            , value2 = self.ps[0].duration)
        self.setDiffs(self.ps[0].accounting, [ltoDiff])

        # now change one of the periods
        self.ps[1].duration = self.ps[1].duration - 1
        self.ps[1].save()

        # What would the revision system look like?
        #dt1 = self.start + timedelta(minutes = 1)
        #dt2 = self.start + timedelta(minutes = 2)
        versions = [VersionTester(fields = {'state' : 2}
                                , dt = dt1)
                  , VersionTester(fields = {'state' : 2}
                                , dt = dt2)
                    ]
        self.setVersions(self.ps[1], versions)
        durDiff = VersionDiff(dt = dt2
                            , field = 'state'
                            , value1 = self.ps[1].duration + 1
                            , value2 = self.ps[1].duration)
        self.setDiffs(self.ps[1], [durDiff])              

        self.sn.setPeriods(self.ps, self.ps)

        # test the staff email
        email = self.sn.email_templates.getObject("staff")
        self.assertEquals(["gbtops@gb.nrao.edu", "gbtinfo@gb.nrao.edu", "gbtime@gb.nrao.edu"]
                        , email.recipients)
        self.assertEquals(email.subject, "GBT schedule for Dec 31-Jan 01")  
        partialBody = """Jan 01 00:00 | Jan 01 05:00 | 06:19 |  2.00 | Nubbles   |           | two
Jan 01 03:00 | Jan 01 08:00 | 09:19 |  4.00 | Nubbles   |           | three"""
        self.assertTrue(partialBody in email.body)       
        deletedStr = "Dec 31 19:00 | Jan 01 00:00 | 01:18 |  5.00 | Nubbles   |           | one"
        self.assertTrue(deletedStr not in email.body)       

        # test the observer email
        email = self.sn.email_templates.getObject("observer")
        exp = [u'pmargani@nrao.edu', u'pmargani@gmail.com', u'paghots@hotmail.com']
        self.assertEquals(exp, email.recipients)
        self.assertEquals("Your GBT project has been scheduled (Dec 31-Jan 01)", email.subject)
        self.assertTrue(partialBody in email.body)       

        # test the changed email - no changes, no recipients
        email = self.sn.email_templates.getObject("changed")
        self.assertEquals(exp, email.recipients)
        deleteLine = "A period for project GBT09A-001 has been deleted."
        changedLine = "A period for project GBT09A-001 has been changed."
        self.assertTrue(deleteLine in  email.body)
        self.assertTrue(changedLine in  email.body)

    def test_setPeriods_deletedElective(self):

        self.setupUser()

        # setup a deleted elective period
        s = create_sesshun()
        s.name = "wtf"
        s.session_type = Session_Type.objects.get(type = "elective")
        s.save()

        pa = Period_Accounting(scheduled = 0)
        pa.save()
        p = Period(session = s
                 , start = datetime(2000, 1, 1, 3)
                 , duration = 1 
                 , state = Period_State.get_state("D")
                 , accounting = pa
                  )
        p.save()

        self.ps.append(p)

        
        # now, we have to make these changes show up in the revisions system
        #self.sn.periodChanges.revisions.versions[p] = {}
        #self.sn.periodChanges.revisions.diffs[p] = {}
        self.addToTestRevisions(p)

        # TBF: make the test flag actually do something!
        #sn = SchedulingNotifier.SchedulingNotifier(test = True)
        self.sn.setPeriods(self.ps, self.ps)

        for x in ["observer", "changed", "staff"]:
            staffEmail = self.sn.email_templates.getObject(x)
            #print "!!!!!!!!!!!!!!!!!!: ", x
            #print staffEmail.subject
            #print staffEmail.recipients
            #print staffEmail.body

        self.assertEquals([], self.sn.deletedPeriods)
        self.assertEquals([p], self.sn.deletedElectivePeriods)

        # test the staff email
        email = self.sn.email_templates.getObject("staff")
        exp = ["gbtops@gb.nrao.edu"
             , "gbtinfo@gb.nrao.edu"
             , "gbtime@gb.nrao.edu"
             , 'pmargani@nrao.edu'
             , 'pmargani@gmail.com'
             , 'paghots@hotmail.com']
        self.assertEquals(exp, email.recipients)
        self.assertEquals(email.subject, "GBT schedule for Dec 31-Jan 01")  
        partialBody = """Dec 31 19:00 | Jan 01 00:00 | 01:18 |  5.00 | Nubbles   |           | one
Jan 01 00:00 | Jan 01 05:00 | 06:19 |  3.00 | Nubbles   |           | two
Jan 01 03:00 | Jan 01 08:00 | 09:19 |  4.00 | Nubbles   |           | three"""
        #print email.body
        self.assertTrue(partialBody in email.body)       
        self.assertTrue("Note: Project GBT09A-001 will not be scheduled on Dec 31 22:00" in email.body)

        # test the observer email
        email = self.sn.email_templates.getObject("observer")
        exp = [u'pmargani@nrao.edu', u'pmargani@gmail.com', u'paghots@hotmail.com']
        self.assertEquals(exp, email.recipients)
        self.assertEquals("Your GBT project has been scheduled (Dec 31-Jan 01)", email.subject)
        self.assertTrue(partialBody in email.body)       
        
        # test the changed email - no changes to scheduled period, 
        # so no recipients
        email = self.sn.email_templates.getObject("changed")
        self.assertEquals([], email.recipients)
