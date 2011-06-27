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
