from datetime            import datetime, timedelta
from django.test.client  import Client

from test_utils.NellTestCase import NellTestCase
from sesshuns.models  import *
from utils            import *

class TestShiftPeriodBoundaries(NellTestCase):
    def setUp(self):
        super(TestShiftPeriodBoundaries, self).setUp()

        # setup some periods
        self.start = datetime(2000, 1, 1, 0)
        self.end   = self.start + timedelta(hours = 12)
        times = [(datetime(2000, 1, 1, 0), 5.0, "one")
               , (datetime(2000, 1, 1, 5), 3.0, "two")
               , (datetime(2000, 1, 1, 8), 4.0, "three")
               ]
        self.ps = []
        for start, dur, name in times:
            s = create_sesshun()
            s.name = name
            s.save()
            pa = Period_Accounting(scheduled = dur)
            pa.save()
            state = first(Period_State.objects.filter(abbreviation = 'S'))
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
        super(TestShiftPeriodBoundaries, self).tearDown()

        for p in self.ps:
            p.session.delete()
            p.remove() #delete()

    def test_shift_period_boundaries(self):
        create_sesshun()
        c = Client()

        period_id = self.ps[1].id
        new_time = self.ps[1].start + timedelta(hours = 1)
        time = new_time.strftime("%Y-%m-%d %H:%M:%S")

        response = c.post('/schedule/shift_period_boundaries'
                        , dict(period_id = period_id
                             , start_boundary = 1
                             , description = "test"
                             , time    = time)) #"2009-10-11 04:00:00"))
        self.failUnless("ok" in response.content)

