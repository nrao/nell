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

from datetime            import datetime, timedelta
from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from scheduler.models  import *
from utils            import *

class TestShiftPeriodBoundaries(BenchTestCase):
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
            state = Period_State.objects.get(abbreviation = 'S')
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

    @timeIt
    def test_shift_period_boundaries(self):
        create_sesshun()
        c = Client()

        period_id = self.ps[1].id
        new_time = self.ps[1].start + timedelta(hours = 1)
        time = new_time.strftime("%Y-%m-%d %H:%M:%S")

        response = c.post('/scheduler/schedule/shift_period_boundaries'
                        , dict(period_id = period_id
                             , start_boundary = 1
                             , description = "test"
                             , time    = time)) #"2009-10-11 04:00:00"))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless("ok" in response.content)
