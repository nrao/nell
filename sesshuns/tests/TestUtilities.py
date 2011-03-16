from django.test.client  import Client
from datetime            import datetime, timedelta

from test_utils              import BenchTestCase, timeIt
from scheduler.models         import *
from scheduler.httpadapters   import *
from sesshuns.utilities      import *
from scheduler.tests.utils                   import create_sesshun

class TestUtilities(BenchTestCase):

    def setupInvestigators(self, invs, proj):
        "Creates investigators, and returns expected emails."

        emails = []
        obs = Role.objects.get(role = "Observer")
        for fn, ln, pi, pc, ob, id in invs:
            u = User(first_name = fn
                   , last_name  = ln
                   , role = obs
                   , pst_id = id # give them sombody's email
                    )
            u.save()
            inv = Investigator(user = u
                             , project = proj
                             , principal_investigator = pi
                             , principal_contact = pc
                             , observer = ob
                              )
            inv.save() 
            emails.append(sorted(u.getEmails()))
        return emails  
       

    def test_getInvestigators(self):

        # get the project we assume is already in the DB
        proj = first(Project.objects.all())

        # create a bunch of investigators for it:
        invs = [("PI", "PI", True, False, False, 821) # Paul
              , ("PC", "PC", False, True, False, 554) # Amy
              , ("obs1", "obs1", False, False, True, 3253) # Mark
              , ("obs2", "obs2", False, False, True, 3680) # Ray
                ]

                
        emails = self.setupInvestigators(invs, proj)
          
        pi, pc, ci, ob, fs = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        self.assertEqual(emails[1], pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[2][0], emails[3][0]], ob)
        self.assertEqual([], fs)

        # try it again, overlapping roles
        for u in User.objects.all():
            u.delete()
        for i in Investigator.objects.all():
            i.delete()
        invs = [("PI", "PI", True, True, False, 821) # Paul
              , ("PC", "PC", False, True, True, 554) # Amy
              , ("obs1", "obs1", False, False, True, 3253) # Mark
              , ("obs2", "obs2", False, False, False, 3680) # Ray
                ]        
                
        emails = self.setupInvestigators(invs, proj)
          
        pi, pc, ci, ob, fs = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        pc_emails = list(emails[1])
        pc_emails.extend(emails[0])
        self.assertEqual(pc_emails, pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[1][0], emails[2][0]], ob)
        self.assertEqual([], fs)

        # now make some friends
        obs = Role.objects.get(role = "Observer")
        u = User(pst_id = 554, role = obs)
        u.save()
        f = Friend(user = u, project = proj)
        f.save()

        pi, pc, ci, ob, fs = getInvestigatorEmails([proj.pcode])
        
        self.assertEqual(emails[0], pi)
        self.assertEqual(pc_emails, pc)
        self.assertEqual([emails[2][0], emails[3][0]], ci)
        self.assertEqual([emails[1][0], emails[2][0]], ob)
        self.assertEqual(emails[1], fs)

    def test_project_search(self):

        # create some projects
        pt = first(Project_Type.objects.all())
        sem10a = Semester.objects.get(semester = "10A")
        p1 = Project(pcode = "GBT10A-001"
                   , semester = sem10a
                   , name = "Greatest Project Ever"
                   , project_type = pt
                    )
        p1.save()            
        p2 = Project(pcode = "GBT10A-002"
                   , semester = sem10a
                   , name = "Suckiest Project Ever"
                   , project_type = pt
                    )
        p2.save()            
        allProjs = Project.objects.all()

        # look for them
        projs = project_search("")
        self.assertEqual(len(allProjs), len(projs))
        projs = project_search("GBT10A-001")
        self.assertEqual(1,  len(projs))
        self.assertEqual(p1, projs[0])
        projs = project_search("GBT10A-002")
        self.assertEqual(1,  len(projs))
        self.assertEqual(p2, projs[0])
        projs = project_search("10A")
        self.assertEqual(2,  len(projs))
        projs = project_search("Suck")
        self.assertEqual(1,  len(projs))
        self.assertEqual(p2, projs[0])
        projs = project_search("10A02")
        self.assertEqual(1,  len(projs))
        self.assertEqual(p2, projs[0])

    def test_copy_elective(self):

        # setup the test:
        # TBF: this was cut and paste from TestElective
        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("elective")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        dur = 5.0
        self.deleted   = Period_State.get_state("D")
        self.pending   = Period_State.get_state("P")
        self.scheduled = Period_State.get_state("S")

        # create an elective to group the periods by
        self.elec = Elective(session = self.sesshun, complete = False)
        self.elec.save()
        
        # create 3 periods separated by a week
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period1 = Period(session = self.sesshun
                            , start = dt 
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period1.save()    

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period2 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 7)
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period2.save() 

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period3 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 2*7)
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period3.save() 

        # finally, done with setup
        origNumWins = len(Elective.objects.all())

        # actually copy the window for testing
        copy_elective(self.elec.id, 1)

        newWins = Elective.objects.all().order_by("id")
        numWins = len(newWins)
        self.assertEquals(origNumWins + 1, numWins)

        ne = newWins[numWins-1]

        self.assertEquals(self.elec.session, ne.session)
        self.assertEquals(self.elec.complete, ne.complete)
        self.assertNotEqual(self.elec.periods.all(),ne.periods.all())
        self.assertEquals(len(self.elec.periods.all())
                        , len(ne.periods.all()))
        self.assertEquals([p.session.id for p in self.elec.periods.all()]
                        , [p.session.id for p in ne.periods.all()])


    def test_copy_window(self):

        self.deleted   = Period_State.get_state("D")
        self.pending   = Period_State.get_state("P")
        self.scheduled = Period_State.get_state("S")

        # TBF: surely I should be able to pull this into some 
        # common code - there are other unit tests that need windows?
        # TBF: cut & paste from TestWindow
        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("windowed")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        #pending = first(Period_State.objects.filter(abbreviation = "P"))
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.default_period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = self.pending
                                   , accounting = pa
                                   )
        self.default_period.save()    

        start = datetime(2009, 6, 1)
        dur   = 7 # days
        
        # create window
        self.w = Window()
        #self.w.start_date = start
        #self.w.duration = dur
        self.w.session = self.sesshun
        self.w.total_time = self.default_period.duration
        self.w.save()
        wr = WindowRange(window = self.w
                       , start_date = start
                       , duration = dur
                        )
        wr.save() 
        self.wr1 = wr

        # window & default period must both ref. eachother
        self.w.default_period = self.default_period
        self.w.save()
        self.default_period.window = self.w
        self.default_period.save()
        self.w_id = self.w.id

        # a chosen period
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        dt = self.default_period.start - timedelta(days = 2)
        self.period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = self.pending
                                   , accounting = pa
                                   )
        self.period.save()    

        pjson = PeriodHttpAdapter(self.default_period).jsondict('UTC', 1.1)
        self.fdata = {"session":  1
                    #, "start":    "2009-06-01"
                    #, "duration": 7
                    , "num_periods": 0
                    , "default_date" : pjson['date'] 
                    , "default_time" : pjson['time'] 
                    , "default_duration" : pjson['duration'] 
                    , "default_state" : pjson['state'] 
                    }

        # finally, done with setup
        origNumWins = len(Window.objects.all())

        # actually copy the window for testing
        copy_window(self.w.id, 1)

        newWins = Window.objects.all().order_by("id")
        numWins = len(newWins)
        self.assertEquals(origNumWins + 1, numWins)

        nw = newWins[numWins-1]

        self.assertEquals(self.w.session, nw.session)
        self.assertEquals(self.w.complete, nw.complete)
        self.assertEquals(self.w.total_time, nw.total_time)
        self.assertEquals(self.w.timeRemaining(), nw.timeRemaining())
        self.assertEquals(self.w.start(), nw.start())
        self.assertEquals(self.w.end(), nw.end())
        self.assertNotEqual(self.w.ranges(),nw.ranges())
        self.assertEquals(self.w.default_period.start
                        , nw.default_period.start)
        self.assertEquals(self.w.default_period.end()
                        , nw.default_period.end())
        self.assertNotEqual(self.w.default_period.id
                        , nw.default_period.id)
        self.assertNotEqual(self.w.periods.all(),nw.periods.all())
        self.assertEquals(len(self.w.periods.all())
                        , len(nw.periods.all()))
        self.assertEquals([p.session.id for p in self.w.periods.all()]
                        , [p.session.id for p in nw.periods.all()])

        # now publish the default period, see what happens
        self.default_period.publish()
        self.w = Window.objects.get(id = self.w.id)
        self.assertEqual(self.w.complete, True)
        self.assertEqual(self.w.timeRemaining(), 0.0)

        # make a copy of this in it's present state
        copy_window(self.w.id, 1)

        newWins = Window.objects.all().order_by("id")
        numWins = len(newWins)
        self.assertEquals(origNumWins + 2, numWins)

        nw = newWins[numWins-1]
        
        self.assertEquals(self.w.session, nw.session)
        self.assertEquals(self.w.complete, nw.complete)
        self.assertEquals(self.w.total_time, nw.total_time)
        self.assertEquals(self.w.timeRemaining(), nw.timeRemaining())
        self.assertEquals(self.w.start(), nw.start())
        self.assertEquals(self.w.end(), nw.end())
        self.assertNotEqual(self.w.ranges(),nw.ranges())
        self.assertEquals(self.w.default_period.start
                        , nw.default_period.start)
        self.assertEquals(self.w.default_period.end()
                        , nw.default_period.end())
        self.assertNotEqual(self.w.default_period.id
                        , nw.default_period.id)
        self.assertNotEqual(self.w.periods.all(),nw.periods.all())
        self.assertEquals(len(self.w.periods.all())
                        , len(nw.periods.all()))
        self.assertEquals([p.session.id for p in self.w.periods.all()]
                        , [p.session.id for p in nw.periods.all()])
        


