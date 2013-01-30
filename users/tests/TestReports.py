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

from datetime                import datetime, timedelta
from scheduler.models        import *
from test_utils              import NellTestCase
from tools.reports  import *
from scheduler.tests.utils                   import create_sesshun
import sys
import calendar

from tools.reports.CompletionReport  import GenerateReport as completionReport
from tools.reports.BlackoutReport  import GenerateBlackoutReport
from tools.reports.DBHealthReport  import GenerateReport as dbHealth
from tools.reports.DBHealthReport  import report_overlaps
from tools.reports.ObservingReport  import generateReport as observingReport
from tools.reports.ObservingReport  import filterPeriodsByDate as observingFilterPeriods
from tools.reports.NSFReport  import GenerateReport as nsfReport
from tools.reports.NSFReport  import normalizePeriodStartStop, getTime
from tools.reports.NSFReport import filterPeriodsByDate, getScheduledTime, getPeriods 
from tools.reports.NSFReport import getMaintenance, getDowntime, getTesting 
from tools.reports.MyNSFReport import myFilterPeriodsByDate
from tools.reports.ProjectReport  import GenerateProjectReport
from tools.reports.ProjTimeAcctReport  import GenerateProjectTimeAccountingReport
from tools.reports.ScheduleReport import ScheduleReport
from tools.reports.SessionReport  import GenerateReport as sessionReport
from tools.reports.StartEndReport  import get_projects_between_start_end 
from tools.reports.WeeklyReport  import WeeklyReport
from tools.reports.WindowsReport  import WindowsReport 
from utilities import TimeAgent

# This breaks the one unit test class per class pattern, since this 
# is a single test class for all the reports, but wtf.

class TestReports(NellTestCase):

    def setUp(self):
        super(TestReports, self).setUp()

        # setup some data to report on
        
        # period dates
        dt1 = datetime(2010, 1, 1, 0)
        dt2 = datetime(2010, 1, 1, 2)
        dt3 = datetime(2010, 1, 1, 5)
        dt4 = datetime(2010, 1, 1, 6)
        dt5 = datetime(2010, 1, 1, 8)

        scheduled = Period_State.get_state("S")

        # an L band sesssion
        self.s1 = create_sesshun()
        self.s1.name = "One"
        self.s1.save()

        rg = Receiver_Group(session = self.s1)
        L = (Receiver.get_rcvr('L'))
        rg.save()
        rg.receivers.add(L)
        rg.save()

        # two periods for this session
        dur = 2.0
        pa = Period_Accounting(scheduled = dur)
        pa.save()
        p = Period(session = self.s1
                 , start = dt1
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()
        pg = Period_Receiver(period = p, receiver = L)
        pg.save()

        dur = 1.0
        pa = Period_Accounting(scheduled = dur, lost_time_rfi = 0.5)
        pa.save()
        p = Period(session = self.s1
                 , start = dt3
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()
        pg = Period_Receiver(period = p, receiver = L)
        pg.save()

        # an X band session
        self.s2 = create_sesshun()
        self.s2.name = "Two"
        self.s2.save()

        rg = Receiver_Group(session = self.s2)
        rg.save()
        X = Receiver.get_rcvr('X')
        rg.receivers.add(X)
        rg.save()

        # two periods for this session
        dur = 3.0
        pa = Period_Accounting(scheduled = dur)
        pa.save()
        p = Period(session = self.s2
                 , start = dt2
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()
        pg = Period_Receiver(period = p, receiver = X)
        pg.save()

        dur = 2.0
        pa = Period_Accounting(scheduled = dur, not_billable = 0.5)
        pa.save()
        p = Period(session = self.s2
                 , start = dt4
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()
        pg = Period_Receiver(period = p, receiver = X)
        pg.save()

    def test_rcvrTimeAccntReport(self):

        r = RcvrTimeAccntReport()
        r.quietReport = True # shhh!

        start = datetime(2010, 1, 1)
        end = datetime(2010, 1, 2)
        r.report(start, end)
        ls = "".join(r.reportLines)
        
        l = "NS      0.00      0.00      0.00      0.00      0.00      0.00"
        self.assertTrue(l in ls)

        l = "L      3.00      2.50      0.00      2.50      0.50      0.00"
        self.assertTrue(l in ls)
        l = "X      5.00      4.50      0.50      5.00      0.00      0.00"
        self.assertTrue(l in ls)

    def test_windowsReport(self):

        # first, nothing much to report
        wr = WindowsReport(filename = "WindowsReport.txt")
        wr.quietReport = True
        wr.report()
        report = "".join(wr.reportLines)
        self.assertEquals(468, len(report))
        self.assertTrue("Number of Windowed Sessions w/ out Windows (VERY BAD): 0" in report)

        # now create a Windowed sesssion
        s = create_sesshun()
        s.session_type = Session_Type.objects.get(type = "windowed")
        s.name = "Win"
        s.save()

        # test
        wr.reportLines = []
        wr.report()
        report = "".join(wr.reportLines)
        self.assertEquals(468, len(report))
        self.assertTrue("Number of Windowed Sessions w/ out Windows (VERY BAD): 1" in report)

        # now create a window for it
        w = Window(session = s)
        w.save()

        # test
        wr.reportLines = []
        wr.report()
        report = "".join(wr.reportLines)
        self.assertEquals(897, len(report))
        self.assertTrue("Number of Windowed Sessions w/ out Windows (VERY BAD): 0" in report)


        # now create a period for it
        rg = Receiver_Group(session = s)
        L = (Receiver.get_rcvr('L'))
        rg.save()
        rg.receivers.add(L)
        rg.save()
        dt1 = datetime(2010, 1, 1, 0)
        scheduled = Period_State.get_state("S")
        dur = 2.0
        pa = Period_Accounting(scheduled = dur)
        pa.save()
        p = Period(session = s
                 , start = dt1
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()
        pg = Period_Receiver(period = p, receiver = L)
        pg.save()

        w.default_period = p
        w.save()

        # test
        wr.reportLines = []
        wr.report()
        report = "".join(wr.reportLines)
        self.assertEquals(988, len(report))
        self.assertTrue("Number of Windowed Sessions w/ out Windows (VERY BAD): 0" in report)

    def test_weeklyReport(self):

        # make sure the project has some alloted time!
        p =  Project.objects.all()[0]
        a = Allotment.objects.all()[0]
        pa = Project_Allotment(project = p, allotment = a)
        pa.save()

        wr = WeeklyReport(datetime(2010, 1, 1))

        # first unit test some helper methods
        ps = Period.objects.all().order_by('start')
        # last period is in 2010-01-01, whichever timezone
        time = wr.get_observed_time(1, [ps[3]], "True")
        self.assertEquals(2.0, time)
        time = wr.get_observed_time(12, [ps[3]], "True")
        self.assertEquals(0.0, time)
        # the next one is still in 2010-01-01, both timezones`
        time = wr.get_observed_time(1, [ps[2]], "True")
        self.assertEquals(1.0, time)
        time = wr.get_observed_time(12, [ps[2]], "True")
        self.assertEquals(0.0, time)

        wr.report()

        for key in ["weather", "other", "billed_to_project"]:
            self.assertEquals(wr.lost_hours[key], 0.0)
        for key in ["total_time", "RFI"]:
            self.assertEquals(wr.lost_hours[key], 0.5)
        
        scheduled_hours = {'shutdown': (0, 0)
                         , 'astronomy': (0, 8.0)
                         , 'test_comm': (0, 0)
                         , 'maintenance': (0, 0)}
        self.assertEquals(scheduled_hours, wr.scheduled_hours)
        self.assertEquals([p], wr.backlog)
        backlog = {'total_time': 93.5
                 , 'monitoring': 0 
                 , 'vlbi': 0
                 , 'years': {'2006': (0, 0)
                           , '2007': (0, 0)
                           , '2004': (0, 0)
                           , '2005': (0, 0)
                           , '2008': (0, 0)
                           , '2009': (93.5, 1)}
                  }
        self.assertEquals(backlog, wr.backlog_hours)          

        # now do the report for the following week:
        # nothing should change but the lost time calcs
        wr = WeeklyReport(datetime(2010, 1, 1) + timedelta(days = 7))
        wr.report()
        self.assertEquals(scheduled_hours, wr.scheduled_hours)
        self.assertEquals(backlog, wr.backlog_hours)          
        for key in wr.lost_hours.keys(): 
            self.assertEquals(wr.lost_hours[key], 0.0)

        
        # now do it for the previous week:
        wr = WeeklyReport(datetime(2010, 1, 1) - timedelta(days = 7))
        wr.report()
        # there are no scheduled hours, because the months covered
        # are 11 and 12!
        for key in wr.scheduled_hours.keys():
            self.assertEquals(wr.scheduled_hours[key], (0,0))

        self.assertEquals(backlog, wr.backlog_hours)          
        for key in wr.lost_hours.keys(): 
            self.assertEquals(wr.lost_hours[key], 0.0)

        # now, introduce a new period that stradles Jan & Feb
        dur = 23.0
        pa = Period_Accounting(scheduled = dur)
        pa.save()
        dt5 = datetime(2010, 1, 31, 12)
        p = Period(session = self.s1
                 , start = dt5
                 , duration = dur
                 , state = Period_State.get_state('S')
                 , accounting = pa
                  )
        p.save()
        L = Receiver.get_rcvr('L')
        pg = Period_Receiver(period = p, receiver = L)
        pg.save()        

        # and see how the report does when reporting in January.
        wr = WeeklyReport(datetime(2010, 1, 28))
        wr.report()
        scheduled_hours = {'shutdown': (0, 0)
                         , 'astronomy': (0, (8.0+12.0)) 

                         , 'test_comm': (0, 0)
                         , 'maintenance': (0, 0)}
        self.assertEquals(scheduled_hours, wr.scheduled_hours)
        backlog = {'total_time': (93.5 - dur)
                 , 'monitoring': 0 
                 , 'vlbi': 0
                 , 'years': {'2006': (0, 0)
                           , '2007': (0, 0)
                           , '2004': (0, 0)
                           , '2005': (0, 0)
                           , '2008': (0, 0)
                           , '2009': ((93.5-dur), 1)
                           }
                  }
        self.assertEquals(backlog, wr.backlog_hours)
        for key in wr.lost_hours.keys(): 
            self.assertEquals(wr.lost_hours[key], 0.0)

        # now see how the report does when reporting in Feb.
        wr = WeeklyReport(datetime(2010, 2, 1))
        wr.report()
        scheduled_hours['astronomy'] = ((8.0+12.0), 0)
        self.assertEquals(scheduled_hours, wr.scheduled_hours)
        self.assertEquals(backlog, wr.backlog_hours)
        for key in wr.lost_hours.keys(): 
            self.assertEquals(wr.lost_hours[key], 0.0)

        # move up to July, and we'll start reporting 2010 from
        # previous semesters
        wr = WeeklyReport(datetime(2010, 7, 1))
        wr.report()
        backlog['years']['2010'] = (0,0)
        self.assertEquals(backlog, wr.backlog_hours)

    def test_startEndReport(self):
        # make it quiet
        orig = sys.stdout
        sys.stdout = open("test_completionReport.txt", 'w')

        start = datetime(2010, 1, 1)
        end   = datetime(2010, 1, 7)
        results = get_projects_between_start_end(start, end)

        sys.stdout = orig

    def test_sessionReport(self):

        sr = sessionReport(datetime.today())

    def test_blackoutReport(self):

        br = GenerateBlackoutReport()

    def test_completionReport(self):

        # make it quiet
        orig = sys.stdout
        sys.stdout = open("test_completionReport.txt", 'w')
        cr = completionReport(datetime.today())
        sys.stdout = orig

    def test_dbHealthReport(self):

        # test generating the entire report
        db = dbHealth()

        # test just the overlaps method
        # first there should be no overlap
        ps = Period.objects.all().order_by("start")
        overlaps = report_overlaps(ps)
        self.assertEquals([], overlaps)
 
        # make sure these periods are in the future
        now = ps[0].start - timedelta(days = 7)

        # no, make two overlapping pending periods, this 
        # should not get reported
        p0, p1 = ps[0:2]
        pending = Period_State.get_state('P')
        p0.state = pending
        p0.duration = p0.duration + 0.25 # 15 minute overlap
        p0.save()
        p1.state = pending
        p1.save()
        # there should be no overlap
        ps = Period.objects.all().order_by("start")
        overlaps = report_overlaps(ps, now = now)
        self.assertEquals([], overlaps)

        # now move one of them back to scheduled, and watch it
        # raise an alarm
        scheduled = Period_State.get_state('S')
        p0.state = scheduled
        p0.save()
        ps = Period.objects.all().order_by("start")
        overlaps = report_overlaps(ps, now = now)
        self.assertEquals(1, len(overlaps))
        self.assertTrue("Overlap with scheduled period" in overlaps[0])

        # move it back to pending, no alarm
        p0.state = pending
        p0.save()
        ps = Period.objects.all().order_by("start")
        overlaps = report_overlaps(ps, now = now)
        self.assertEquals([], overlaps)

        # now raise the the alarm by making this in the past
        now2 = ps[0].start + timedelta(days = 7)
        overlaps = report_overlaps(ps, now = now2)
        self.assertEquals(1, len(overlaps))
        self.assertTrue("Overlap in past" in overlaps[0])

        # move it back to the future, no alarm
        ps = Period.objects.all().order_by("start")
        overlaps = report_overlaps(ps, now = now)
        self.assertEquals([], overlaps)
 
        # make the overlap involve 3 periods, to raise an alarm
        p1.state = pending
        p1.save()
        p3 = ps[2]
        p3.start = p1.start
        p3.state = pending
        p3.save()
        overlaps = report_overlaps(ps, now = now)
        self.assertEquals(1, len(overlaps))
        self.assertTrue("Overlap of 3 periods" in overlaps[0])

    def test_projectReport(self):

        pr = GenerateProjectReport()

    def test_projTimeAcctReport(self):

        # make it quiet
        orig = sys.stdout
        sys.stdout = open("test_projTimeAcctReport.txt", 'w')

        p = Project.objects.all()[0]
        tr = GenerateProjectTimeAccountingReport(p.pcode)

        sys.stdout = orig
 
    def test_scheduleReport(self):

        sr = ScheduleReport()
        sr.quietReport = True
        start = datetime(2010, 1, 1)
        days = 30
        sr.report(start, days)
        ls = "".join(sr.reportLines)

        result = """Start (ET)   |      UT      |  LST  |  (hr) | T | S |    PI     | Rx        | Session
--------------------------------------------------------------------------------------
Dec 31 19:00 | Jan 01 00:00 | 01:20 |  2.00 | O | S | Unknown   | L         | One
Dec 31 21:00 | Jan 01 02:00 | 03:21 |  3.00 | O | S | Unknown   | X         | Two
Jan 01 00:00 | Jan 01 05:00 | 06:21 |  1.00 | O | S | Unknown   | L         | One
Jan 01 01:00 | Jan 01 06:00 | 07:21 |  2.00 | O | S | Unknown   | X         | Two"""
        self.assertTrue(result in ls)

    def test_observingReport(self):

        # Periods look like (UTC, EST subtract 5):
        # 1 One: 2010-01-01 00:00:00 for  2.00 Hrs
        # 3 Two: 2010-01-01 02:00:00 for  3.00 Hrs
        # 2 One: 2010-01-01 05:00:00 for  1.00 Hrs - this one start in Jan, EST
        # 4 Two: 2010-01-01 06:00:00 for  2.00 Hrs

        # run the report to catch the 2cd half of our periods
        periods = []
        quarter = 2
        year = 2010
        fiscal_year = 2010
        for m in [1,2,3]:
            periods.extend(observingFilterPeriods(datetime(year, m, 1)))
        pcodes, sch, obs = observingReport('Q%d FY %d' % (quarter, fiscal_year), periods)
        self.assertEquals([u'GBT09A-001'], pcodes)
        self.assertEquals({u'GBT09A-001': 3.0}, sch)
        self.assertEquals({u'GBT09A-001': 2.5}, obs)

        # now make huge period spanning across month boundary and w/ lost time
        dur = 36.0
        scheduled = Period_State.get_state("S")
        pa = Period_Accounting(scheduled = dur, lost_time_rfi = 30.0)
        pa.save()
        p = Period(session = self.s1
                 , start = datetime(2010, 1, 31, 0)
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()

        L = (Receiver.get_rcvr('L'))
        pg = Period_Receiver(period = p, receiver = L)
        pg.save()

        periods = []
        for m in [1,2,3]:
            periods.extend(observingFilterPeriods(datetime(year, m, 1)))
        pcodes, sch, obs = observingReport('Q%d FY %d' % (quarter, fiscal_year), periods)
        pcode = u'GBT09A-001'
        self.assertEquals([pcode], pcodes)
        self.assertAlmostEquals(sch[pcode], 3.0 + dur, 2)
        self.assertAlmostEquals(obs[pcode], 2.5 + dur - 30.0, 2)

    def test_nsfReport(self):

        # Periods look like (UTC, EST subtract 5):
        # 1 One: 2010-01-01 00:00:00 for  2.00 Hrs
        # 3 Two: 2010-01-01 02:00:00 for  3.00 Hrs
        # 2 One: 2010-01-01 05:00:00 for  1.00 Hrs - this one start in Jan, EST
        # 4 Two: 2010-01-01 06:00:00 for  2.00 Hrs
       
        decStart = datetime(2009,12, 1, 0)
        janStart = datetime(2010, 1, 1, 0)
        ps = Period.objects.all().order_by('start')
        ps = list(ps)

       
        # what are the periods that lie in Dec (EST)?
        filterd = filterPeriodsByDate(decStart)
        self.assertEquals([1,3], [p.id for p in filterd])
        # what are the periods that lie in Jan (EST)?
        filterd = filterPeriodsByDate(janStart)
        self.assertEquals([2,4], [p.id for p in filterd])

        pids = [1,2,4]
        dts = [decStart, janStart, janStart]
        for pid, dt in zip(pids, dts):
            p = Period.objects.get(id = pid)
            start, stop = normalizePeriodStartStop(p, dt)
            self.assertEquals(start, TimeAgent.utc2est(p.start))
            self.assertEquals(stop, TimeAgent.utc2est(p.end()))
        # Period 3 is a special case
        p = Period.objects.get(id = 3)
        start, stop = normalizePeriodStartStop(p, decStart)
        self.assertEquals(start, TimeAgent.utc2est(p.start))
        self.assertEquals(stop, datetime(2009, 12, 31, 23, 59, 59))


        self.assertAlmostEquals(5.000, getTime(ps[:2], decStart), 2)    
        self.assertAlmostEquals(3.000, getTime(ps[2:], janStart), 2)    

        # tail of Q1
        dt = decStart
        fps = filterPeriodsByDate(dt)
        self.assertAlmostEquals(5.000, getScheduledTime(fps, dt), 2)    
        self.assertEquals(0.0, getDowntime(fps, dt))    
        self.assertEquals(0.0, getMaintenance(fps, dt))    
        self.assertEquals(0.0, getTesting(fps, dt))    

        # Start of Q2!
        dt = janStart
        fps = filterPeriodsByDate(dt)
        self.assertAlmostEquals(3.000, getScheduledTime(fps, dt), 2)    
        self.assertEquals(0.5, getDowntime(fps, dt))    
        self.assertEquals(0.0, getMaintenance(fps, dt))    
        self.assertEquals(0.0, getTesting(fps, dt))    

        argv = ["program", "1", "2010"]
        quarters = {
            1: [10, 11, 12]
          , 2: [1, 2, 3]
          , 3: [4, 5, 6]
          , 4: [7, 8, 9]
                   }

        quarter     = int(argv[1])
        fiscal_year = int(argv[2])
    
        months = quarters[quarter]
        year   = fiscal_year if quarter != 1 else fiscal_year - 1
   
        nsfReport('Q%dFY%d' % (quarter, fiscal_year)
                     , [datetime(year, m, 1) for m in months])


        # can we handle 24 hour periods?
        dur = 24.0
        scheduled = Period_State.get_state("S")
        pa = Period_Accounting(scheduled = dur)
        pa.save()
        p = Period(session = self.s1
                 , start = datetime(2010, 1, 1, 8)
                 , duration = dur
                 , state = scheduled
                 , accounting = pa
                  )
        p.save()

        L = (Receiver.get_rcvr('L'))
        pg = Period_Receiver(period = p, receiver = L)
        pg.save()

        start, stop = normalizePeriodStartStop(p, janStart)
        self.assertEquals(start, TimeAgent.utc2est(p.start))
        self.assertEquals(stop, TimeAgent.utc2est(p.end()))

        dt = janStart
        fps = filterPeriodsByDate(dt)
        self.assertAlmostEquals(27.000, getScheduledTime(fps, dt), 2)    
        self.assertEquals(0.5, getDowntime(fps, dt))    
        self.assertEquals(0.0, getMaintenance(fps, dt))    
        self.assertEquals(0.0, getTesting(fps, dt)) 
