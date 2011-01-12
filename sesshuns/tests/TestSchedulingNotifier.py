from nell.utilities  import SchedulingNotifier
from utils           import create_sesshun
from PeriodsTestCase import PeriodsTestCase
from sesshuns.models import *

class TestSchedulingNotifier(PeriodsTestCase):

    def test_examinePeriods(self):

        # TBF: make the test flag actually do something!
        sn = SchedulingNotifier.SchedulingNotifier(test = True)

        sn.examinePeriods(self.ps)
        self.assertEquals(self.ps, sn.observingPeriods)
        self.assertEquals([], sn.changedPeriods)
        self.assertEquals([], sn.deletedPeriods)

    def test_examinePeriods_2(self):

        # TBF: make the test flag actually do something!
        sn = SchedulingNotifier.SchedulingNotifier(test = True)

        # now delete one of these periods
        #p = self.ps[0]
        self.ps[0].state = Period_State.get_state("D")
        self.ps[0].accounting.lost_time_other = self.ps[0].duration
        self.ps[0].save()

        # also create a windowed session with default period that
        # is in the deleted state
        s = create_sesshun()
        s.session_type = first(Session_Type.objects.filter(type = "windowed"))
        s.save()

        # new default period for a window that is after the original periods
        start_time = self.ps[2].start + timedelta(hours = self.ps[2].duration)
        dur = 3.0

        pa = Period_Accounting(scheduled = 0)
        pa.save()
        state = first(Period_State.objects.filter(abbreviation = "D"))
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

        ps = [self.ps[0]
            , self.ps[1]
            , self.ps[2]
            , p
             ]
        sn.examinePeriods(ps)
        obsPeriods = self.ps[1:]
        self.assertEquals(obsPeriods, sn.observingPeriods)
        self.assertEquals([self.ps[0]], sn.changedPeriods)
        self.assertEquals([self.ps[0]], sn.deletedPeriods)

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

        # TBF: make the test flag actually do something!
        sn = SchedulingNotifier.SchedulingNotifier(test = True)

        sn.setPeriods(self.ps)
        
        for x in ["observer", "deleted"]:
            staffEmail = sn.email_templates.getObject(x)

            #print staffEmail.subject
            #print staffEmail.recipients
            #print staffEmail.body

        # test the staff email
        email = sn.email_templates.getObject("staff")
        self.assertEquals(["gbtops@gb.nrao.edu", "gbtinfo@gb.nrao.edu", "gbtime@gb.nrao.edu"]
                        , email.recipients)
        self.assertEquals(email.subject, "GBT schedule for Dec 31-Jan 01")  
        partialBody = """Dec 31 19:00 | Jan 01 00:00 | 01:18 |  5.00 | Nubbles   |           | one
Jan 01 00:00 | Jan 01 05:00 | 06:19 |  3.00 | Nubbles   |           | two
Jan 01 03:00 | Jan 01 08:00 | 09:19 |  4.00 | Nubbles   |           | three"""
        self.assertTrue(partialBody in email.body)       

        # test the deleted email
        email = sn.email_templates.getObject("deleted")
        self.assertEquals([], email.recipients)
        self.assertEquals("Reminder: GBT Schedule has changed.", email.subject)
        partialBody2 = "This is a reminder that the following projects had been scheduled"
        self.assertTrue(partialBody2 in email.body)       

        # test the observer email
        email = sn.email_templates.getObject("observer")
        exp = [u'pmargani@nrao.edu', u'pmargani@gmail.com', u'paghots@hotmail.com']
        self.assertEquals(exp, email.recipients)
        self.assertEquals("Your GBT project has been scheduled (Dec 31-Jan 01)", email.subject)
        self.assertTrue(partialBody in email.body)       

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

        # TBF: make the test flag actually do something!
        sn = SchedulingNotifier.SchedulingNotifier(test = True)

        sn.setPeriods(self.ps)

        self.assertEquals([], sn.deletedPeriods)
        self.assertEquals([p], sn.deletedElectivePeriods)

        for x in ["observer", "deleted", "staff"]:
            staffEmail = sn.email_templates.getObject(x)
            #print "!!!!!!!!!!!!!!!!!!: ", x
            #print staffEmail.subject
            #print staffEmail.recipients
            #print staffEmail.body


        # test the staff email
        email = sn.email_templates.getObject("staff")
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

        # test the deleted email
        email = sn.email_templates.getObject("deleted")
        self.assertEquals([], email.recipients)
        self.assertEquals("Reminder: GBT Schedule has changed.", email.subject)
        partialBody2 = "This is a reminder that the following projects had been scheduled"
        self.assertTrue(partialBody2 in email.body)       

        # test the observer email
        email = sn.email_templates.getObject("observer")
        exp = [u'pmargani@nrao.edu', u'pmargani@gmail.com', u'paghots@hotmail.com']
        self.assertEquals(exp, email.recipients)
        self.assertEquals("Your GBT project has been scheduled (Dec 31-Jan 01)", email.subject)
        self.assertTrue(partialBody in email.body)       
        
