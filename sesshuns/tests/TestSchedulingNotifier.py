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
                   , start_date = p.start.date() - timedelta(days = 7)
                   , duration = 10 # days
                   , default_period = p
                   , period = None )
        w1.save()

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

