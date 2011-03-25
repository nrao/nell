from datetime  import datetime, timedelta

from scheduler.utilities     import ScheduleTools
from nell.utilities          import TimeAgent, TimeAccounting
from test_utils              import NellTestCase
from scheduler.models         import *
from utils                   import create_sesshun

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
        state = Period_State.objects.get(abbreviation = 'S')
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


    def test_getSchedulingRange(self):

        # scheduling range is 0:00 of timezone of first day
        # to the last day at 8:00 EST

        # test it in winter time
        dt = datetime(2010, 1, 1)
        days = 2
        expStart = datetime(2010, 1, 1, 0)
        expEnd   = datetime(2010, 1, 3, 13)
        expDur = TimeAgent.dtDiffMins(expStart, expEnd)

        start, dur = ScheduleTools().getSchedulingRange(dt, 'UTC', days)
        self.assertEquals(expStart, start)
        self.assertEquals(expDur, dur)

        # make sure it works in ET too
        expStart = datetime(2010, 1, 1, 5)
        expEnd   = datetime(2010, 1, 3, 13)
        expDur = TimeAgent.dtDiffMins(expStart, expEnd)

        start, dur = ScheduleTools().getSchedulingRange(dt, 'ET', days)
        self.assertEquals(expStart, start)

        # test it in summer time
        dt = datetime(2010, 6, 10)
        days = 3
        expStart = datetime(2010, 6, 10, 0)
        expEnd   = datetime(2010, 6, 13, 12)
        expDur = TimeAgent.dtDiffMins(expStart, expEnd)

        start, dur = ScheduleTools().getSchedulingRange(dt, 'UTC', days)
        self.assertEquals(expStart, start)
        self.assertEquals(expDur, dur)

        # make sure it works in ET too
        expStart = datetime(2010, 6, 10, 4)
        expEnd   = datetime(2010, 6, 13, 12)
        expDur = TimeAgent.dtDiffMins(expStart, expEnd)

        start, dur = ScheduleTools().getSchedulingRange(dt, 'ET', days)
        self.assertEquals(expStart, start)
        self.assertEquals(expDur, dur)

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

        tag = "Period backup: 2000-01-01 02:00:00 for  3.00 Hrs got  3.00 hours from: one: 2000-01-01 00:00:00 for  5.00 Hrs ( 3.00 hours)"
        self.assertTrue(tag in backup.accounting.description)
        self.assertTrue(tag in canceled.accounting.description)

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

        tag = "No Period got time from: one: 2000-01-01 00:00:00 for  5.00 Hrs ( 3.00 hours)"
        self.assertTrue(tag in canceled.accounting.description)

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
        canceled = Period.objects.get(state__abbreviation = 'D')
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
        canceled = Period.objects.get(state__abbreviation = 'D')
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
        canceled = Period.objects.get(state__abbreviation = 'D')
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

        tag = "Period one: 2000-01-01 00:00:00 for  5.00 Hrs got  1.00 hours from: two: 2000-01-01 05:00:00 for  3.00 Hrs ( 1.00 hours) ]"

        self.assertTrue(desc in ps[0].accounting.description)
        self.assertTrue(desc in ps[1].accounting.description)
        self.assertTrue(tag  in ps[0].accounting.description)
        self.assertTrue(tag  in ps[1].accounting.description)

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

