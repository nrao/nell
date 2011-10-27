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
from datetime            import datetime, timedelta

from test_utils              import BenchTestCase, timeIt
from scheduler.models         import Project, Project_Type, Semester
from users.utilities      import *
from scheduler.tests.utils import create_maintenance_sesshun
from scheduler.tests.utils import create_maintenance_project
from scheduler.tests.utils import create_maintenance_elective
from users.tests.utils     import create_maintenance_activity

class TestUtilities(BenchTestCase):

    def test_project_search(self):

        # create some projects
        pt = Project_Type.objects.all()[0]
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

    def test_get_gbt_schedule_events_fixed(self):
        """
        Step through the setup of a single fixed maintenance day,
        with two simple activities, and watch what happens when this
        period gets published.
        """

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10, 1)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)
    
        # create the Maintenance Project
        proj = create_maintenance_project()
    
        # create the fixed maintenance session
        ms = create_maintenance_sesshun()
    
        # create a pending period for the thursday (9/29) of the work week
        # starting monday (9/26)
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        pending = Period_State.get_state("P")
        p = Period(session = ms
                 , start = datetime(2011, 9, 29, 10)
                 , duration = 1.0
                 , state = pending
                 , accounting = pa
                  )
        p.save()

        # the schedule should remain empty: fixed period not yet published.
        exp = self.assert_empty_schedule(start, end)

        # now publish the period!
        p.publish()
        p.save()

        # now get the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        # Should now appear on Thursday
        calEvents = sch[4][1]
        self.assertEqual(1,len(calEvents))
        mag = calEvents[0].contained
        self.assertEqual('1 -- 2011-09-26; (2011-09-29); x; active; Empty', mag.__unicode__())
        self.assertEqual([], mag.get_maintenance_activity_set())

        # now create a simple event
        ma = create_maintenance_activity()
        ma.set_start(datetime(2011, 9, 26, 10), 'UTC')
        ma.group = mag
        ma.save()

        # Get the maintenance on Thurdsay again, check to see if our activity is there
        calEvents = sch[4][1]
        self.assertEqual(1,len(calEvents))
        mag = calEvents[0].contained
        self.assertEqual('1 -- 2011-09-26; (2011-09-29); x; active; Test Maintenance Activity',
                         mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(1, len(mas))
        ma = mas[0]
        self.assertEqual("Test Maintenance Activity", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())

        # now create a daily repeat!
        ma = create_maintenance_activity()
        ma.subject = "Repeat Daily 1"
        ma.set_start(datetime(2011, 9, 26, 9), 'UTC')
        ma.group = mag
        ma.repeat_interval = 1
        ma.repeat_end = datetime(2011, 9, 30, 10)
        ma.save()

        # where does it show up?  It should only appear once on Thursday
        sch = get_gbt_schedule_events(start, end, timezone)
        calEvents = sch[4][1]
        self.assertEqual(1,len(calEvents))
        mag = calEvents[0].contained
        self.assertEqual('1 -- 2011-09-26; (2011-09-29); x; active; Repeat Daily 1, Test Maintenance Activity',
                         mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(2, len(mas))
       
        # make sure the DB makes sense
        all_ma = Maintenance_Activity.objects.all()
        # There should be 3 maintenance activities: the one added
        # above, the template for 'Repeat Daily 1', and an instance of
        # 'Repeat Daily 1'.
        self.assertEqual(3, len(all_ma))
        self.assertEqual(1, len(Maintenance_Activity_Group.objects.all()))


    def test_get_gbt_schedule_events_elective(self):
        """
        Step through the setup of a single elective maintenance, 
        with two simple activities, and watch what happens when a
        period gets published.
        """

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10, 1)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)

        # create the Maintenance Project
        proj = create_maintenance_project()

        #week = datetime(2011, 04, 11)
        per_data = ((datetime(2011, 9, 27, 8), 8),
                    (datetime(2011, 9, 28, 8), 8),
                    (datetime(2011, 9, 29, 8), 8),
                    (datetime(2011, 9, 30, 8), 8))
        me = create_maintenance_elective(per_data)    

        # now see what the calendar brings up - the elective
        # is actually diplayed as a 'floating maintenance day' on the 
        # monday of the week (9/26)
        sch = get_gbt_schedule_events(start, end, timezone)
        # all other days are still blank
        blankDays = [0,2,3,4,5]
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])
       
        # what's on the monday?
        calEvents = sch[1][1]
        self.assertEqual(1,len(calEvents))
        mag = calEvents[0].contained
        self.assertEqual("1 -- 2011-09-26; (2011-09-26); A; active; Empty", mag.__unicode__())
        self.assertEqual([], mag.get_maintenance_activity_set())

        # now create a simple event
        ma = create_maintenance_activity()
        ma.set_start(datetime(2011, 9, 26, 10), 'UTC')
        ma.group = mag
        ma.save()

        # make sure it shows up in the floating maint. day
        sch = get_gbt_schedule_events(start, end, timezone)
        # all other days are still blank
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])
       
        # what's on the monday?  Should show our new activity too!
        calEvents = sch[1][1]
        self.assertEqual(1,len(calEvents))
        mag = calEvents[0].contained
        self.assertEqual("1 -- 2011-09-26; (2011-09-26); A; active; Test Maintenance Activity", mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(1, len(mas))
        ma = mas[0]
        self.assertEqual("Test Maintenance Activity", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())

        # now create a daily repeat!
        ma = create_maintenance_activity()
        ma.subject = "Repeat Daily 1"
        ma.set_start(datetime(2011, 9, 26, 9), 'UTC')
        ma.group = mag
        ma.repeat_interval = 1
        ma.repeat_end = datetime(2011, 9, 30, 10)
        ma.save()

        # where does it show up?  It should only appear once on the
        # floating day:
        sch = get_gbt_schedule_events(start, end, timezone)
        # all other days are still blank
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])

        # Monday?    
        calEvents = sch[1][1]
        self.assertEqual(1,len(calEvents))
        self.assertEqual('CalEventFloatingMaintenance', calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        self.assertEqual("1 -- 2011-09-26; (2011-09-26); A; active; Repeat Daily 1, Test Maintenance Activity", mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(2, len(mas))
        ma = mas[0]
        self.assertEqual("Repeat Daily 1", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())
        self.assertEqual(True, ma.is_repeat_template())
        ma = mas[1]
        self.assertEqual("Test Maintenance Activity", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())
        self.assertEqual(False, ma.is_repeat_template())

        # make sure the DB makes sense
        self.assertEqual(2, len(Maintenance_Activity.objects.all()))
        self.assertEqual(1, len(Maintenance_Activity_Group.objects.all()))

        # now publish the period on Wed (9/28)!
        p = me.periods.all().order_by("start")[1]
        p.publish()
        p.save()

        # make sure the DB makes sense
        self.assertEqual(2, len(Maintenance_Activity.objects.all()))
        self.assertEqual(1, len(Maintenance_Activity_Group.objects.all()))

        # that really changes things!
        sch = get_gbt_schedule_events(start, end, timezone)
        # now there's nothing on monday, but there is on thursday 
        blankDays = [0,1,2,4,5]
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])
        # check out Wed.    
        calEvents = sch[3][1]
        self.assertEqual(1,len(calEvents))
        # see how the class has changed!
        self.assertEqual('CalEventFixedMaintenance', calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        # note how the .week is the same, but .date() has changed
        self.assertEqual("1 -- 2011-09-26; (2011-09-28); A; active; Repeat Daily 1, Test Maintenance Activity", mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(2, len(mas))
        ma = mas[0]
        self.assertEqual("Repeat Daily 1", ma.subject)
        self.assertEqual(True, ma.is_repeat_activity())
        self.assertEqual(False, ma.is_repeat_template())
        self.assertEqual(2, ma.repeat_template_id)
        ma = mas[1]
        self.assertEqual("Test Maintenance Activity", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())
        self.assertEqual(False, ma.is_repeat_template())
        
        # make sure the DB makes sense
        self.assertEqual(1, len(Maintenance_Activity_Group.objects.all()))
        # Woah!  check it out: 2 -> 3 because the original repeat stays
        # as is, but there's a new one for display on Thursday
        self.assertEqual(3, len(Maintenance_Activity.objects.all()))
        
    def test_get_gbt_schedule_events_incidental(self):
        """
        Put some shit up on the calendar when there are no maintenance
        days planeed yet
        """

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10, 1)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)

        # make sure the DB makes sense
        self.assertEqual(0, len(Maintenance_Activity.objects.all()))
        self.assertEqual(0, len(Maintenance_Activity_Group.objects.all()))        
        # now create a simple event for Tuesday
        ma = create_maintenance_activity()
        ma.set_start(datetime(2011, 9, 27, 10), 'UTC')
        ma.save()

        sch = get_gbt_schedule_events(start, end, timezone)
        blankDays = [0,1,3,4,5]
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])
        # check out Tuesday    
        calEvents = sch[2][1]
        self.assertEqual(1,len(calEvents))
        # see how the class has changed!
        self.assertEqual('CalEventIncidental', calEvents[0].__class__.__name__)
        mas = calEvents[0].contained
        self.assertEqual(1, len(mas))
        self.assertEqual("Test Maintenance Activity", mas[0].subject)

        # let's see what repeats do: make one starting on Wed. 
        ma = create_maintenance_activity()
        ma.subject = "Repeat Daily 1"
        ma.set_start(datetime(2011, 9, 28, 9), 'UTC')
        ma.repeat_interval = 1
        ma.repeat_end = datetime(2011, 9, 30, 10)
        ma.save()

        sch = get_gbt_schedule_events(start, end, timezone)
        blankDays = [0,1,4,5]
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])
        # check out Tuesday    
        calEvents = sch[2][1]
        self.assertEqual(1,len(calEvents))
        # see how the class has changed!
        self.assertEqual('CalEventIncidental', calEvents[0].__class__.__name__)
        mas = calEvents[0].contained
        self.assertEqual(1, len(mas))
        self.assertEqual("Test Maintenance Activity", mas[0].subject)

        # check out Wed.    
        calEvents = sch[3][1]
        self.assertEqual(1,len(calEvents))
        # see how the class has changed!
        self.assertEqual('CalEventIncidental', calEvents[0].__class__.__name__)
        mas = calEvents[0].contained
        self.assertEqual(1, len(mas))
        self.assertEqual("Repeat Daily 1", mas[0].subject)

    def test_get_gbt_schedule_events_repeats_fixed_weekly(self):
        "Focus on the behavior of repeats with fixed maintenance"

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10,15)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)

        # create the fixed maintenance session
        proj = create_maintenance_project()
        ms = create_maintenance_sesshun()
    
        # create a pending periods for the wed (9/28) and thursday (9/29)
        # of the work week starting monday (9/26)
        ps = []
        # twice a week for three weeks
        dates = [(9, 28), (9, 29), (10, 5), (10, 6), (10, 12), (10, 13)]
        for month, day in dates:
            pa = Period_Accounting(scheduled = 0.0)
            pa.save()
            scheduled = Period_State.get_state("S")
            p = Period(session = ms
                 , start = datetime(2011, month, day, 10)
                 , duration = 1.0
                 , state = scheduled
                 , accounting = pa
                  )
            p.save()
            ps.append(p)

        # check out the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        nonBlankDays = [3,4,10,11,17,18] #[1,8,15] 
        blankDays = [i for i in range(0,20) if i not in nonBlankDays]
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        # check out the days the periods are scheduled for   
        mags = []
        for day in nonBlankDays:
            calEvents = sch[day][1]
            self.assertEqual(1,len(calEvents))
            self.assertEqual('CalEventFixedMaintenance'
                           , calEvents[0].__class__.__name__)
            mag = calEvents[0].contained
            self.assertEqual([], mag.get_maintenance_activity_set())
            mags.append(mag) # for use below
        

        # now create a daily repeating activity for the whole time range   
        ma = create_maintenance_activity()
        ma.subject = "Repeat Daily 1"
        ma.group = mags[0] # the first one from the list above
        ma.set_start(datetime(2011, 9, 27, 10), 'UTC')
        ma.repeat_interval = 1
        ma.repeat_end = datetime(2011, 10, 15, 10)
        ma.save()

        # check out the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        blankDays = [i for i in range(0,20) if i not in nonBlankDays]
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        # check out the periods' days 
        for day in nonBlankDays:
            calEvents = sch[day][1]
            self.assertEqual(1,len(calEvents))
            self.assertEqual('CalEventFixedMaintenance'
                           , calEvents[0].__class__.__name__)
            mag = calEvents[0].contained
            mas = mag.get_maintenance_activity_set()
            self.assertEqual(1, len(mas))
            self.assertEqual("Repeat Daily 1", mas[0].subject)


        # Now create a weekly repeating activity for two weeks 
        ma = create_maintenance_activity()
        ma.subject = "Repeat Weekly 1"
        ma.group = mags[0] # the first one from the list above
        ma.set_start(datetime(2011, 9, 28, 10), 'UTC')
        ma.repeat_interval = 7 # weekly
        ma.repeat_end = datetime(2011, 10, 10, 10)
        ma.save()
        

        # check out the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        blankDays = [i for i in range(0,20) if i not in nonBlankDays]
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        for day in nonBlankDays: 
            calEvents = sch[day][1]
            self.assertEqual(1,len(calEvents))
            self.assertEqual('CalEventFixedMaintenance'
                           , calEvents[0].__class__.__name__)
            mag = calEvents[0].contained
            mas = mag.get_maintenance_activity_set()
            # the weekly only shows up twice
            if day in [3,10]:
                self.assertEqual(2, len(mas))
                self.assertEqual("Repeat Daily 1", mas[0].subject)
                self.assertEqual("Repeat Weekly 1", mas[1].subject)
            else:    
                self.assertEqual(1, len(mas))
                self.assertEqual("Repeat Daily 1", mas[0].subject)

    def test_get_gbt_schedule_events_repeats_unscheduled(self):
        "Focus on the behavior of repeats with fixed maintenance"

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10,15)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)

        # create the fixed maintenance sessions
        proj = create_maintenance_project()
        ms = create_maintenance_sesshun()
        # here's our special 'unscheduled' session!
        mu = create_maintenance_sesshun()
        mu.name = "Unscheduled Maintenance"
        mu.save()

        # create a pending periods for the wed (9/28) and thursday (9/29)
        # of the work week starting monday (9/26)
        # with regular maint. on thursday, unscheduled on wed.
        ps = []
        # twice a week for three weeks
        dates = [(9, 26, ms), (9, 28, mu), (9, 29, ms)]
        for month, day, sess in dates:
            pa = Period_Accounting(scheduled = 0.0)
            pa.save()
            scheduled = Period_State.get_state("S")
            p = Period(session = sess
                 , start = datetime(2011, month, day, 10)
                 , duration = 1.0
                 , state = scheduled
                 , accounting = pa
                  )
            p.save()
            ps.append(p)

        # check out the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        nonBlankDays = [1,3,4] 
        blankDays = [i for i in range(0,7) if i not in nonBlankDays]
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        # check out the days the periods are scheduled for   
        mags = []
        for day in nonBlankDays:
            calEvents = sch[day][1]
            self.assertEqual(1,len(calEvents))
            self.assertEqual('CalEventFixedMaintenance'
                           , calEvents[0].__class__.__name__)
            mag = calEvents[0].contained
            self.assertEqual([], mag.get_maintenance_activity_set())
            mags.append(mag) # for use below
        

        # now create a daily repeating activity for the whole time range
        ma = create_maintenance_activity()
        ma.subject = "Repeat Daily 1"
        ma.group = mags[0] # the first one from the list above
        ma.set_start(datetime(2011, 9, 26, 10), 'UTC')
        ma.repeat_interval = 1
        ma.repeat_end = datetime(2011, 10, 15, 10)
        ma.save()

        # it should only show up on the regular maint. day
        # check out the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        # check out the days the periods are scheduled for   
        for day in nonBlankDays:
            calEvents = sch[day][1]
            self.assertEqual(1,len(calEvents))
            self.assertEqual('CalEventFixedMaintenance'
                           , calEvents[0].__class__.__name__)
            mag = calEvents[0].contained
            mas = mag.get_maintenance_activity_set()
            if day == 3:
                # unscheduled day!
                self.assertEqual(0, len(mas))
            else:
                self.assertEquals(1, len(mas))   

    def test_get_gbt_schedule_events_repeats_electives(self):
        "Focus on the behavoir of repeats with elective maintenance"

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10, 8)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)

        # create an elective for both weeks
        per_data_1 = ((datetime(2011, 9, 27, 8), 8),
                    (datetime(2011, 9, 28, 8), 8),
                    (datetime(2011, 9, 29, 8), 8),
                    (datetime(2011, 9, 30, 8), 8))
        me1 = create_maintenance_elective(per_data_1)
        per_data_2 = ((datetime(2011, 10, 4, 8), 8),
                    (datetime(2011, 10, 5, 8), 8),
                    (datetime(2011, 10, 6, 8), 8),
                    (datetime(2011, 10, 7, 8), 8))
        me2 = create_maintenance_elective(per_data_2)
    
        # now check out the schedule
        sch = get_gbt_schedule_events(start, end, timezone)
        nonBlankDays = [1,8]
        blankDays = [i for i in range(0,13) if i not in nonBlankDays] 
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        # check out Mondays    
        mags = []
        for day in nonBlankDays:
            calEvents = sch[day][1]
            self.assertEqual(1,len(calEvents))
            self.assertEqual('CalEventFloatingMaintenance'
                           , calEvents[0].__class__.__name__)
            mag = calEvents[0].contained
            self.assertEqual([], mag.get_maintenance_activity_set())
            mags.append(mag) # for use below

        # now create a daily repeating activity that spans our whole cal.
        ma = create_maintenance_activity()
        ma.subject = "Repeat Daily 1"
        ma.group = mags[0] # the first one from the list above
        ma.set_start(datetime(2011, 9, 27, 9), 'UTC')
        ma.repeat_interval = 1
        ma.repeat_end = datetime(2011, 10, 9, 10)
        ma.save()

        sch = get_gbt_schedule_events(start, end, timezone)
        for i in blankDays:
            self.assertEqual(exp[i], sch[i])

        # check out the first Monday    
        calEvents = sch[1][1]
        self.assertEqual(1,len(calEvents))
        self.assertEqual('CalEventFloatingMaintenance'
                       , calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(1, len(mas))
        self.assertEqual("Repeat Daily 1", mas[0].subject)

        # check out the second Monday
        calEvents = sch[8][1]
        self.assertEqual(1,len(calEvents))
        self.assertEqual('CalEventFloatingMaintenance'
                       , calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        mas = mag.get_maintenance_activity_set()
        # TBF: the repeat should show up here!
        self.assertEqual(0, len(mas))
        #self.assertEqual(1, len(mas))
        #self.assertEqual("Repeat Daily 1", mas[0].subject)

    def test_get_gbt_schedule_events_elective_2(self):

        # first, make sure an empty schedule looks empty
        start = datetime(2011, 9, 25)
        end   = datetime(2011, 10, 1)
        timezone = 'UTC'
        exp = self.assert_empty_schedule(start, end)

        # create the Maintenance Project
        proj = create_maintenance_project()

        #week = datetime(2011, 04, 11)
        per_data = ((datetime(2011, 9, 27, 8), 8),
                    (datetime(2011, 9, 28, 8), 8),
                    (datetime(2011, 9, 29, 8), 8),
                    (datetime(2011, 9, 30, 8), 8))
        me = create_maintenance_elective(per_data)    

        # need to call this to create the first maint. group
        sch = get_gbt_schedule_events(start, end, timezone)
        mag = Maintenance_Activity_Group.objects.all()[0]

        # now create simple events
        ma1 = create_maintenance_activity()
        ma1.set_start(datetime(2011, 9, 26, 10), 'UTC')
        ma1.group = mag
        ma1.save()
        ma2 = create_maintenance_activity()
        ma2.set_start(datetime(2011, 9, 26, 11), 'UTC')
        ma2.subject = "ma2"
        ma2.group = mag
        ma2.save()

        # now publish the period on Wed (9/28)!
        p = me.periods.all().order_by("start")[1]
        p.publish()
        p.save()

        # see what it looks like
        sch = get_gbt_schedule_events(start, end, timezone)
        # now there's nothing on monday, but there is on Wed. 
        blankDays = [0,1,2,4,5]
        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])
        # check out Wed.    
        calEvents = sch[3][1]
        self.assertEqual(1,len(calEvents))
        self.assertEqual('CalEventFixedMaintenance', calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        self.assertEqual("1 -- 2011-09-26; (2011-09-28); A; active; ma2, Test Maintenance Activity", mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(2, len(mas))
        ma = mas[0]
        self.assertEqual("Test Maintenance Activity", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())
        self.assertEqual(False, ma.is_repeat_template())
        ma = mas[1]
        self.assertEqual("ma2", ma.subject)
        self.assertEqual(False, ma.is_repeat_activity())
        self.assertEqual(False, ma.is_repeat_template())

        # now, schedule an emergency maint. activity for Tuesday.
        ms = create_maintenance_sesshun()
        ms.name = "Emergency Maintenance"
        ms.session_type = Session_Type.objects.get(type = "fixed")
        ms.save()
   
        pa = Period_Accounting(scheduled = 1.0)
        pa.save()
        scheduled = Period_State.get_state("S")
        p = Period(session = ms
                 , start = datetime(2011, 9, 27, 10)
                 , duration = 1.0
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()

        # see what it looks like
        sch = get_gbt_schedule_events(start, end, timezone)
        # now there's nothing on monday, but there is on Wed. 
        blankDays = [0,1,4,5]

        for i in blankDays: 
            self.assertEqual(exp[i], sch[i])

        calEvents = sch[2][1]
        self.assertEqual(1,len(calEvents))
        self.assertEqual('CalEventFixedMaintenance', calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        # make sure it is the 'emergency' mag, not the one that belongs on Wed.
        self.assertEqual("2 -- 2011-09-26; (2011-09-27); x; active; Empty", mag.__unicode__())
        # And it's empty; we didn't add anything above.
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(0, len(mas))
        # check out Wed.
        calEvents = sch[3][1]
        self.assertEqual(1,len(calEvents))
        self.assertEqual('CalEventFixedMaintenance', calEvents[0].__class__.__name__)
        mag = calEvents[0].contained
        self.assertEqual('1 -- 2011-09-26; (2011-09-28); A; active; ma2, Test Maintenance Activity',
                         mag.__unicode__())
        mas = mag.get_maintenance_activity_set()
        self.assertEqual(2, len(mas))


    def assert_empty_schedule(self, start, end):
        timezone = 'UTC'
        days = (end - start).days
        sch = get_gbt_schedule_events(start, end, timezone)
        dts = [start + timedelta(days = i) for i in range(0,days)]
        exp = zip(dts, [[] for i in range(0,days)])
        self.assertEqual(exp, sch)
        return exp
    
