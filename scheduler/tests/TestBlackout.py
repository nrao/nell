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

from datetime import datetime, timedelta
from time     import mktime

from test_utils               import NellTestCase
from scheduler.models         import *
from utils                    import create_blackout

class TestBlackout(NellTestCase):

    def setUp(self):
        super(TestBlackout, self).setUp()

        # create some user blackouts
        self.u = User(first_name = "Test"
                    , last_name  = "User"
                      )
        self.u.save()

        self.blackout1 = create_blackout(user = self.u,
                                         repeat = "Once",
                                         start = datetime(2009, 1, 1, 11),
                                         end = datetime(2009, 1, 3, 11))

        self.blackout2 = create_blackout(user = self.u,
                                         repeat = 'Weekly',
                                         start  = datetime(2009, 1, 4, 11),
                                         end    = datetime(2009, 1, 4, 13),
                                         until  = datetime(2009, 5, 4, 11))

        # create some project blackouts
        semester = Semester.objects.get(semester = "08C")
        ptype    = Project_Type.objects.get(type = "science")

        self.pcode = "GBT08C-01"
        self.project = Project(semester = semester
                             , project_type = ptype
                             , pcode = self.pcode
                               )
        self.project.save()

        self.blackout3 = create_blackout(project  = self.project,
                                         timezone = 'UTC',
                                         repeat   = 'Once',
                                         start    = datetime(2008, 10, 1, 11),
                                         end      = datetime(2008, 10, 3, 11))

    def test_eventjson(self):
        # user blackout
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        json = self.blackout1.eventjson(mktime(calstart.timetuple())
                                      , mktime(calend.timetuple()))
        event = {'className': 'blackout'
               , 'start': '2009-01-01T11:00:00'
               , 'end': '2009-01-03T11:00:00'
               , 'id': 1L
               , 'title': 'Test User: blackout'
               }
        self.assertEqual(event, json[0])

        # project blackout
        calstart = datetime(2008, 10, 1)
        calend   = datetime(2008, 10, 30)
        json = self.blackout3.eventjson(mktime(calstart.timetuple())
                                      , mktime(calend.timetuple()))
        event = {'className': 'blackout'
               , 'start': '2008-10-01T11:00:00'
               , 'end': '2008-10-03T11:00:00'
               , 'id': 3L
               , 'title': '%s: blackout' % self.pcode
               }
        self.assertEqual(event, json[0])

    def test_isActive(self):
        results = [(b.isActive(b.getStartDate() + timedelta(hours = 2))
                  , b.isActive(b.getEndDate() + timedelta(hours = 2)))
                   for b in Blackout.objects.all()]
        self.assertEqual(results, [(True, False), (True, True), (True, False)])

    def test_generateDates(self):

        # no repeats are easy ...
        dts = [(self.blackout1.getStartDate(), self.blackout1.getEndDate())]
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        gdts = self.blackout1.generateDates(calstart, calend)
        self.assertEquals(dts, gdts)

        # should be none in June.
        calstart = datetime(2009, 6, 1)
        calend   = datetime(2009, 6, 30)
        gdts = self.blackout1.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

        # repeats are more complicated
        # how does January look?
        calstart = datetime(2009, 1, 1)
        calend   = datetime(2009, 1, 30)
        start = self.blackout2.getStartDate()
        end = self.blackout2.getEndDate()
        dts = [(start, end)]
        for i in [1,2,3]:
            dts.append((start + timedelta(days = 7 * i)
                      , end   + timedelta(days = 7 * i)))
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(dts, gdts)

        # outside of calendar start/end, but weekly until May
        calstart = datetime(2009, 2, 1)
        calend   = datetime(2009, 2, 28)
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(4, len(gdts))

        # should be none in June.
        calstart = datetime(2009, 6, 1)
        calend   = datetime(2009, 6, 30)
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

        # should be none in previous June.
        calstart = datetime(2008, 6, 1)
        calend   = datetime(2008, 6, 30)
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

        # no repeats are easy ... even for project blackouts
        dts = [(self.blackout3.getStartDate(), self.blackout3.getEndDate())]
        calstart = datetime(2008, 10, 1)
        calend   = datetime(2008, 10, 30)
        gdts = self.blackout3.generateDates(calstart, calend)
        self.assertEquals(dts, gdts)

        # test filter outside of blackouts
        calstart = datetime(2011, 10, 1)
        calend   = datetime(211, 10, 30)
        gdts = self.blackout1.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))
        gdts = self.blackout2.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))
        gdts = self.blackout3.generateDates(calstart, calend)
        self.assertEquals(0, len(gdts))

    def test_projectBlackout(self):
        "Repeat some of the other tests, but for project blackouts"

        self.assertEquals(self.blackout3.forName(), self.project.pcode)
        self.assertEquals(self.blackout3.forUrlId(), self.project.pcode)

