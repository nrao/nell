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

from test_utils       import NellTestCase
from scheduler.models  import *
from utils            import *

class TestSemester(NellTestCase):

    def test_getFutureSemesters(self):
        dt = datetime(2010, 12, 25, 0, 0, 0)
        future = [s.semester for s in Semester.getFutureSemesters(dt)]
        self.assertEqual([u'11A', u'11B', u'12A', u'12B'], future[:4])

    def test_getPreviousSemesters(self):
        dt = datetime(2010, 12, 25, 0, 0, 0)
        previous = [s.semester for s in Semester.getPreviousSemesters(dt)]
        self.assertEqual([u'04A', u'05A', u'05B', u'05C', u'06A', u'06B'
                        , u'06C', u'07A', u'07B', u'07C', u'08A', u'08B'
                        , u'08C', u'09A', u'09B', u'09C', u'10A', u'10B'
                        , u'10C'], previous)
