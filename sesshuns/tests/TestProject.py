from test_utils.NellTestCase import NellTestCase
from sesshuns.models         import *
from sesshuns.httpadapters   import *
from utils                   import create_sesshun

class TestProject(NellTestCase):
    def setUp(self):
        super(TestProject, self).setUp()

        self.project = Project()
        self.project_adapter = ProjectHttpAdapter(self.project)
        pdata = {"semester"   : "09A"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
               , "notes"      : "notes"
               , "schd_notes" : "scheduler's notes"
        }
        self.project_adapter.update_from_post(pdata)

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

        fdata = {'session'  : self.sesshun.id
               , 'date'     : '2009-06-01'
               , 'time'     : '10:00'
               , 'duration' : 1.0
               , 'backup'   : False}
        self.period = Period()
        self.period_adapter = PeriodHttpAdapter(self.period)
        self.period_adapter.init_from_post(fdata, 'UTC')

    def tearDown(self):
        self.investigator2.delete()
        self.user2.delete()
        self.investigator1.delete()
        self.user1.delete()
        self.period.delete()
        self.sesshun.delete()
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
            (datetime(2009, 1, 1, 11), datetime(2009, 1, 4, 13))
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
        SessionHttpAdapter(self.sesshun).save_receivers('L | (X & S)')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # No available receivers at these times:
        expected = [(datetime(2009, 4, 1), datetime(2009, 4, 26))
                  , (datetime(2009, 5, 1), datetime(2009, 5, 6))]
        SessionHttpAdapter(self.sesshun).save_receivers('K | (X & S)')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # No available receivers at these times:
        expected = [(datetime(2009, 4, 11), None)]
        SessionHttpAdapter(self.sesshun).save_receivers('600')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # Always an available receiver.
        SessionHttpAdapter(self.sesshun).save_receivers('(800 | S) | Ku')

        blackouts = self.project.get_receiver_blackout_ranges(start, end)
        self.assertEquals([], blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # Clean up.
        Receiver_Schedule.objects.all().delete()

    def test_get_prescheduled_times(self):
        start = datetime(2009, 6, 1)
        end   = datetime(2009, 6, 2)

        # No periods.
        times = self.project.get_prescheduled_times(start, end)
        self.assertEquals(0, len(times))

        # Now add a project w/ prescheduled times.
        otherproject = Project()
        pdata = {"semester"   : "09A"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
               , "notes"      : "notes"
               , "schd_notes" : "scheduler's notes"
        }
        adapter = ProjectHttpAdapter(otherproject)
        adapter.update_from_post(pdata)

        othersesshun = create_sesshun()
        othersesshun.project = otherproject
        othersesshun.save()

        fdata = {'session'  : othersesshun.id
               , 'date'     : '2009-06-01'
               , 'time'     : '13:00'
               , 'duration' : 1.0
               , 'backup'   : False}
        otherperiod = Period()
        adapter = PeriodHttpAdapter(otherperiod)
        adapter.init_from_post(fdata, 'UTC')
        otherperiod.state = Period_State.objects.filter(abbreviation = 'S')[0]
        otherperiod.save()

        # Test again
        times = self.project.get_prescheduled_times(start, end)
        self.assertEquals(1, len(times))
        self.assertEquals(times[0][0], datetime(2009, 6, 1, 13))
        self.assertEquals(times[0][1], datetime(2009, 6, 1, 14))

        # Clean up
        otherperiod.delete()
        othersesshun.delete()
        otherproject.delete()

    def test_get_prescheduled_days(self):
        start = datetime(2009, 6, 1)
        end   = datetime(2009, 6, 3)

        # No periods.
        days = self.project.get_prescheduled_days(start, end)
        self.assertEquals(0, len(days))

        # Now add a project w/ prescheduled times but not for whole day.
        otherproject = Project()
        pdata = {"semester"   : "09A"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
               , "notes"      : "notes"
               , "schd_notes" : "scheduler's notes"
        }
        project_adapter = ProjectHttpAdapter(otherproject)
        project_adapter.update_from_post(pdata)
        otherproject.save()

        othersesshun = create_sesshun()
        othersesshun.project = otherproject
        othersesshun.save()

        fdata = {'session'  : othersesshun.id
               , 'date'     : '2009-06-01'
               , 'time'     : '13:00'
               , 'duration' : 1.0
               , 'backup'   : False}
        otherperiod = Period()
        period_adapter = PeriodHttpAdapter(otherperiod)
        period_adapter.init_from_post(fdata, 'UTC')
        otherperiod.state = Period_State.objects.filter(abbreviation = 'S')[0]
        otherperiod.save()

        # Test again
        days = self.project.get_prescheduled_days(start, end)
        self.assertEquals(0, len(days))

        # Now add a period w/ prescheduled times for whole day.
        fdata = {'session'  : othersesshun.id
               , 'date'     : '2009-05-31'
               , 'time'     : '23:00'
               , 'duration' : 30.0
               , 'backup'   : False}
        anotherperiod = Period()
        period_adapter.load(anotherperiod)
        period_adapter.init_from_post(fdata, 'UTC')
        anotherperiod.state = Period_State.objects.filter(abbreviation = 'S')[0]
        anotherperiod.save()

        # Test again
        days = self.project.get_prescheduled_days(start, end)
        self.assertEquals(1, len(days))
        self.assertEquals(days[0], datetime(2009, 6, 1))

        # Now make that whole day prescheduled period part of the project.
        anotherperiod.session = self.sesshun
        anotherperiod.save()

        # Test again
        days = self.project.get_prescheduled_days(start, end)
        self.assertEquals(0, len(days))

        # Clean up
        anotherperiod.delete()
        otherperiod.delete()
        othersesshun.delete()
        otherproject.delete()

    def test_init_from_post(self):
        p1 = Project()
        p2 = Project()
        self.gitrdone(p1, ProjectHttpAdapter(p1).init_from_post
                    , p2, ProjectHttpAdapter(p2).init_from_post)

        p3 = Project()
        adapter = ProjectHttpAdapter(p3)
        adapter.init_from_post({})

    def test_update_from_post(self):
        p1 = Project()
        p2 = Project()
        self.gitrdone(p1, ProjectHttpAdapter(p1).update_from_post, p2, ProjectHttpAdapter(p2).update_from_post)

    def gitrdone(self, p1, f1, p2, f2):
        "Mike was here."

        p_fdata = {"semester" : "09A"
                 , "type"     : "science"
                 , "total_time" : "10.0"
                 , "PSC_time"   : "10.0"
                 , "sem_time"   : "10.0"
                 , "grade"      : "4.0"
                   }
        f1(p_fdata)
        self.defaultAssertion(p_fdata, p1)

        p_fdata1 = {"semester" : "09A"
                 , "type"     : "science"
                 , "total_time" : "10.0, 5.0"
                 , "PSC_time"   : "10.0, 5.0"
                 , "sem_time"   : "10.0, 5.0"
                 , "grade"      : "4.0, 3.0"
                   }
        f2(p_fdata1)
        self.defaultAssertion(p_fdata1, p2)

        p_fdata = {"semester" : "09A"
                 , "type"     : "science"
                 , "total_time" : "10.0, 5.0, 1.0"
                 , "PSC_time"   : "10.0, 5.0, 1.0"
                 , "sem_time"   : "10.0, 5.0, 1.0"
                 , "grade"      : "4.0, 3.0, 2.0"
                   }
        f2(p_fdata)
        self.defaultAssertion(p_fdata, p2)

        f2(p_fdata1)
        self.defaultAssertion(p_fdata1, p2)

    def defaultAssertion(self, p_fdata, p):
        totals = map(float, p_fdata.get("total_time").split(', '))
        pscs     = map(float, p_fdata.get("PSC_time", "").split(', '))
        max_sems = map(float, p_fdata.get("sem_time", "").split(', '))
        grades   = map(float, p_fdata.get("grade", "").split(', '))
        for a in p.allotments.all():
            self.assertTrue(a.total_time in totals)
            self.assertTrue(a.psc_time in pscs)
            self.assertTrue(a.max_semester_time in max_sems)
            self.assertTrue(a.grade in grades)

