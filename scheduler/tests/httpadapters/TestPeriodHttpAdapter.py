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

from test_utils import NellTestCase
from scheduler.models import *
from scheduler.httpadapters import PeriodHttpAdapter
from scheduler.tests.utils  import create_sesshun
from datetime  import datetime

class TestPeriodHttpAdapter(NellTestCase):

    def setUp(self):
        super(TestPeriodHttpAdapter, self).setUp()
        self.s       = create_sesshun()

    def test_windowed_period_init(self):
        self.s.session_type = Session_Type.objects.get(type = 'windowed')
        self.s.save()
        window = Window(session    = self.s
                      , total_time = 10)
        window.save()
        windowRange = WindowRange(window     = window
                                , start_date = datetime(2011, 10, 12, 12)
                                , duration   = 7)
        windowRange.save()
        adapter = PeriodHttpAdapter(Period())
        data    = {'handle': '%s (%s) %s' % (self.s.name, self.s.project.pcode, self.s.id)
                 , 'window_id': str(window.id)
                   }
        adapter.init_from_post(data, 'UTC')

        # Make sure the period starts on the last date of the window (default)
        self.assertEqual(adapter.period.start.date(), window.last_date())
