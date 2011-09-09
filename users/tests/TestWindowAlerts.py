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

from datetime import datetime, date, timedelta

from test_utils              import NellTestCase
from tools.alerts import WindowAlerts
from utilities               import TimeAgent
from scheduler.models         import *
from scheduler.httpadapters   import *
from scheduler.tests.utils                   import create_sesshun

class TestWindowAlerts(NellTestCase):

    def setUp(self):
        super(TestWindowAlerts, self).setUp()

        # setup a project with:
        #   * a user with blackouts
        #   * a windowed session
        #   * a number of windows

        # make the calendar look like this:
        # windows:
        # 4/5 - 4/12         5/5 - 5/12
        # default periods:
        #     4/10

        # user 1 blackouts:
        # 4/1 - 4/3
        # 4/1 - 4/7
        # 4/2 - 4/4

        # user 1 blackouts:
        # 4/1 - 4/3
        # 4/1 - 4/7

        # blacked out time:
        # 4/1 - 4/7

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

        # Create the first user (on project) 
        self.user1 = User(sanctioned = True
                        , role = Role.objects.get(role = "Observer")
                     )
        self.user1.save()

        self.investigator1 =  Investigator(project  = self.project
                                         , user     = self.user1
                                         , observer = True)
        self.investigator1.save()
         
        # Create the second user (on project)
        self.user2 = User(sanctioned = True
                        , role = Role.objects.get(role = "Observer")
                     )
        self.user2.save()

        self.investigator2 =  Investigator(project  = self.project
                                         , user     = self.user2
                                         , observer = True)
        self.investigator2.save()

        # Create Investigator1's 3 blackouts.
        blackout11 = Blackout(user       = self.user1
                            , repeat     = Repeat.objects.all()[0]
                            , start_date = datetime(2009, 4, 1, 11)
                            , end_date   = datetime(2009, 4, 3, 11))
        blackout11.save()

        blackout12 = Blackout(user       = self.user1
                            , repeat     = Repeat.objects.all()[0]
                            , start_date = datetime(2009, 4, 1, 18)
                            , end_date   = datetime(2009, 4, 7, 18))
        blackout12.save()

        blackout13 = Blackout(user       = self.user1
                            , repeat     = Repeat.objects.all()[0]
                            , start_date = datetime(2009, 4, 2, 12)
                            , end_date   = datetime(2009, 4, 7, 20))
        blackout13.save()

        # Create Investigator2's 2 blackouts.
        blackout21 = Blackout(user       = self.user2
                            , repeat     = Repeat.objects.all()[0]
                            , start_date = datetime(2009, 4, 1, 11)
                            , end_date   = datetime(2009, 4, 3, 11))
        blackout21.save()

        blackout22 = Blackout(user       = self.user2
                            , repeat     = Repeat.objects.all()[0]
                            , start_date = datetime(2009, 4, 1, 18)
                            , end_date   = datetime(2009, 4, 7, 13))
        blackout22.save()

        # make a session
        self.sesshun = create_sesshun()
        self.sesshun.session_type = \
            Session_Type.objects.get(type = "windowed")
        self.sesshun.project = self.project
        # '1070' available 4/6 - 4/16
        SessionHttpAdapter(self.sesshun).save_receivers('1070')        
        self.sesshun.save()

        # make the first window
        self.window = Window(session = self.sesshun
                 #, start_date   = date(2009, 4, 5)
                 #, duration    = 7
                 , total_time = 4.0
                 , complete = False)
        self.window.save()
        wr = WindowRange(window = self.window
                       , start_date = date(2009, 4, 5)
                       , duration = 7)
        wr.save()               

        # make a period for it
        fdata = {'session'  : self.sesshun.id
               , 'date'     : '2009-04-10'
               , 'time'     : '10:00'
               , 'duration' : 4.0
               , 'backup'   : False}
        self.period = Period()
        self.period_adapter = PeriodHttpAdapter(self.period)
        self.period_adapter.init_from_post(fdata, 'UTC')

        # link the period and window
        self.period.window = self.window
        self.period.save()
        self.window.default_period = self.period
        self.window.save()

        # setup a receiver schedule
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

        # The        4/5 - 4/12 window suffers from:
        # blackouts: 4/1 - 4/7
        # no rcvr:   4/1 - 4/6
        # pre-schd:  none

        # so: schedulable = 4/6 - 4/12 -> 6 * 24 ~ 144 hrs
        # but: blackouts  = 4/1 - 4/7, 1 day overlap ~ 24 hrs

    def testGetWindowTimes(self):

        # test
        wa = WindowAlerts.WindowAlerts()
        now = datetime(2009, 1, 1)
        times = wa.getWindowTimes(now)

        # expected result
        sch = [(datetime(2009, 4, 6), self.window.end_datetime()) ]
        bss = [(datetime(2009, 4, 6), datetime(2009, 4, 7, 13, 0))]
        schHrs = TimeAgent.timedelta2minutes(sch[0][1] - sch[0][0])/60.0
        bssHrs = TimeAgent.timedelta2minutes(bss[0][1] - bss[0][0])/60.0
        exp = [(self.window
              , (schHrs
               , bssHrs
               , sch
               , [bss]))]

        self.assertEquals(exp[0][0], times[0][0])
        self.assertEquals(exp[0][1], times[0][1])

        # add some blacked out time - 3 days
        bsStart = datetime(2009, 4, 8)
        bsEnd   = datetime(2009, 4, 11)
        blackout = Blackout(project    = self.project
                          , start_date = bsStart
                          , end_date   = bsEnd
                          , repeat     = Repeat.objects.all()[0]
                           )
        blackout.save()
        bss.insert(0, (bsStart, bsEnd))
        bssHrs += 3*24

        times = wa.getWindowTimes(now)

        exp = [(self.window
              , (schHrs
               , bssHrs
               , sch
               , [bss]))]

        self.assertEquals(exp[0][0], times[0][0])
        self.assertEquals(exp[0][1], times[0][1])

        # move the current time forward
        now = datetime(2009, 4, 9, 12, 15, 0)
        times = wa.getWindowTimes(now)

        sch = [(now, self.window.end_datetime()) ]
        bss = [(now, bsEnd)]
        schHrs = TimeAgent.timedelta2minutes(sch[0][1] - sch[0][0])/60.0
        bssHrs = TimeAgent.timedelta2minutes(bss[0][1] - bss[0][0])/60.0
        exp = [(self.window
              , (schHrs
               , bssHrs
               , sch
               , [bss]))]

        self.assertEquals(exp[0][0], times[0][0])
        self.assertEquals(exp[0][1], times[0][1])

    def testGetWindowTimesNonContigious(self):

        # test
        now = datetime(2009, 1, 1)
        wa = WindowAlerts.WindowAlerts()
        times = wa.getWindowTimes(now)

        # expected result
        sch = [(datetime(2009, 4, 6), self.window.end_datetime()) ]
        bss = [(datetime(2009, 4, 6), datetime(2009, 4, 7, 13, 0))]
        schHrs = TimeAgent.timedelta2minutes(sch[0][1] - sch[0][0])/60.0
        bssHrs = TimeAgent.timedelta2minutes(bss[0][1] - bss[0][0])/60.0
        exp = [(self.window
              , (schHrs
               , bssHrs
               , sch
               , [bss]))]

        self.assertEquals(exp[0][0], times[0][0])
        self.assertEquals(exp[0][1], times[0][1])

        # now split up this window into two ranges w/ out changing result
        # 4/5 -> 4/12 changes to 4/2 - 4/4 and 4/6 - 4/12
        wr1 = self.window.windowrange_set.all()[0]
        wr1.start_date = datetime(2009, 4, 6)
        wr1.duration = 6 # days
        wr1.save()

        wr2 = WindowRange(window = self.window
                        , start_date = datetime(2009, 4, 2)
                        , duration = 2)
        wr2.save()

        wa = WindowAlerts.WindowAlerts()
        times = wa.getWindowTimes(now)

        # expected result
        sch = [(datetime(2009, 4, 6), self.window.end_datetime()) ]
        bss = [(datetime(2009, 4, 6), datetime(2009, 4, 7, 13, 0))]
        schHrs = TimeAgent.timedelta2minutes(sch[0][1] - sch[0][0])/60.0
        bssHrs = TimeAgent.timedelta2minutes(bss[0][1] - bss[0][0])/60.0
        exp = [(self.window
              , (schHrs
               , bssHrs
               , sch
               , [bss]))]

        self.assertEquals(exp[0][0], times[0][0])
        self.assertEquals(exp[0][1], times[0][1])

        # now change the window ranges to affect the result - change the 
        # second range so that there is less scheduable time
        wr1.start_date = datetime(2009, 4, 7)
        wr1.duration = 5
        wr1.save()

        wa = WindowAlerts.WindowAlerts()
        times = wa.getWindowTimes(now)

        # expected result
        sch = [(datetime(2009, 4, 7), self.window.end_datetime()) ]
        bss = [(datetime(2009, 4, 7), datetime(2009, 4, 7, 13, 0))]
        schHrs = TimeAgent.timedelta2minutes(sch[0][1] - sch[0][0])/60.0
        bssHrs = TimeAgent.timedelta2minutes(bss[0][1] - bss[0][0])/60.0
        exp = [(self.window
              , (schHrs
               , bssHrs
               , sch
               , [bss]))]

    def testFindAlertLevels(self):

        wa = WindowAlerts.WindowAlerts()
        now = datetime(2009, 1, 1)
 
        # we 37/144 = 25% of scheduble time blacked out
        # so we should raise a level 1 alert
        ns = wa.findAlertLevels(now)
        
        self.assertEquals(1, len(ns))             
        self.assertEquals(self.window, ns[0][0])
        self.assertEquals(1, ns[0][2])

        # if we introduce more blacked out time, we should
        # see this elevate to a level 2 alert
        blackout = Blackout(project    = self.project
                          , start_date = datetime(2009, 4, 8)
                          , end_date   = datetime(2009, 4, 11)
                          , repeat     = Repeat.objects.all()[0]
                          )
        blackout.save()

        ns = wa.findAlertLevels(now)

        self.assertEquals(1, len(ns))             
        self.assertEquals(self.window, ns[0][0])
        self.assertEquals(2, ns[0][2]) # level two!

    def testFindAlerts(self):

        wa = WindowAlerts.WindowAlerts()
 
        # We 37/144 = 25% of scheduble time blacked out
        # so we should raise an alaram.
        # Long before the window starts, the weekly notification
        # will tell about this (stage I):
        now = datetime(2009, 1, 1)
        ns = wa.findBlackoutAlerts(stage = 1
                         , now = now
                           )
        self.assertEquals(1, len(ns))
        self.assertEquals(self.window, ns[0][0])
        self.assertEquals(1, ns[0][2])

        # This would not be sent out in stage II
        ns = wa.findBlackoutAlerts(stage = 2, now = now)
        self.assertEquals(0, len(ns))

        # But would be once we get close enough to the window
        now = self.window.start_datetime() - timedelta(days = 5)
        ns = wa.findBlackoutAlerts(stage = 2, now = now)
        self.assertEquals(1, len(ns))
        self.assertEquals(self.window, ns[0][0])
        self.assertEquals(1, ns[0][2])

