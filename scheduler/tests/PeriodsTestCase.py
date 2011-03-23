from datetime                import datetime, timedelta
from test_utils              import BenchTestCase
from scheduler.tests.utils                   import create_sesshun
from scheduler.models        import Period_Accounting, Period_State, Period

class PeriodsTestCase(BenchTestCase):
    "Parent class for test cases that need periods to work with."

    def setUp(self):
        super(PeriodsTestCase, self).setUp()

        # setup some periods
        self.start = datetime(2000, 1, 1, 0)
        self.end   = self.start + timedelta(hours = 12)
        times = [(datetime(2000, 1, 1, 0), 5.0, "one", "S")
               , (datetime(2000, 1, 1, 5), 3.0, "two", "P")
               , (datetime(2000, 1, 1, 8), 4.0, "three", "S")
               ]
        self.ps = []
        for start, dur, name, st in times:
            s = create_sesshun()
            s.name = name
            s.save()
            scheduled = dur if st == "S" else 0.0
            pa = Period_Accounting(scheduled = scheduled)
            pa.save()
            state = Period_State.objects.get(abbreviation = st)
            p = Period( session    = s
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()
            self.ps.append(p)

    def tearDown(self):
        super(PeriodsTestCase, self).tearDown()

        for p in self.ps:
            p.session.delete()
            p.remove() #delete()
