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
from time                import mktime

from test_utils          import NellTestCase
from scheduler.models    import *
from utils               import create_blackout
from utilities.TimeAgent import dst_boundaries, tz_to_tz

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

    def test_ut_dst(self):
        blackout = create_blackout(user     = self.u,
                                   repeat   = 'Weekly',
                                   start    = datetime(2011, 1, 1, 11),
                                   end      = datetime(2011, 1, 4, 13),
                                   until    = datetime(2011, 12, 4, 11),
                                   timezone = 'UTC')

        # This is a UTC blackout.  Every start time and end time
        # generated should equal the start and end times above, 11:00
        # and 13:00.

        dates = blackout.generateDates(blackout.getStartDate(), blackout.getUntil())
        start_time = blackout.getStartDate().time()
        end_time = blackout.getEndDate().time()

        for i in dates:
            self.assertEquals(i[0].time(), start_time)
            self.assertEquals(i[1].time(), end_time)

    def test_pt_dst(self):
        # dates are given as UTC dates even though the timezone is
        # given as a local timezone.  This is the way the blackout
        # view works. :/

        localstart = datetime(2011, 1, 1, 11)
        localend = datetime(2011, 1, 4, 13)
        localuntil = datetime(2011, 12, 4, 11)
        utcstart = tz_to_tz(localstart, 'US/Pacific', 'UTC', naive = True)
        utcend = tz_to_tz(localend, 'US/Pacific', 'UTC', True)
        utcuntil = tz_to_tz(localuntil, 'US/Pacific', 'UTC', True)
        spring, fall = dst_boundaries('US/Pacific', utcstart, utcuntil)

        my_bo = create_blackout(user     = self.u,
                                repeat   = 'Weekly',
                                start    = utcstart,
                                end      = utcend,
                                until    = utcuntil,
                                timezone = 'US/Pacific')

        # generate 'UTC' sequence of blackout dates for standard time
        # until spring transition.
        dates = my_bo.generateDates(utcstart,
                                    spring,
                                    local_timezone = False)
        self.assertNotEquals(len(dates), 0)

        # All the dates except the last one are in standard time.
        for i in range(0, len(dates) - 1):
            self.assertEquals(dates[i][0].time(), utcstart.time())
            self.assertEquals(dates[i][1].time(), utcend.time())
        # the last one straddles DST, so end should be an hour earlier in UTC.
        self.assertEquals(dates[-1][0].time(), utcstart.time())
        self.assertEquals(dates[-1][1].time(), (utcend - timedelta(hours = 1)).time())

        # generate 'UTC' sequence of blackout dates for spring DST
        # transition until fall transition.  This sequence will
        # include 2 transition blackouts over both DST transitions:
        one_hour = timedelta(hours = 1)
        dates = my_bo.generateDates(spring,
                                    fall,
                                    local_timezone = False)
        self.assertNotEquals(len(dates), 0)

        self.assertEquals(dates[0][0].time(), utcstart.time())
        self.assertEquals(dates[0][1].time(), (utcend - one_hour).time())

        for i in range(1, len(dates) - 1):
            self.assertEquals(dates[i][0].time(), (utcstart - one_hour).time())
            self.assertEquals(dates[i][1].time(), (utcend - one_hour).time())

        self.assertEquals(dates[-1][0].time(), (utcstart - one_hour).time())
        self.assertEquals(dates[-1][1].time(), utcend.time())

        # generate 'UTC' sequence of blackout dates from fall
        # transition until the 'until' time.  Back to standard time.
        # The first blackout in the range will be a transition
        # blackout.
        dates = my_bo.generateDates(fall,
                                    utcuntil,
                                    local_timezone = False)
        self.assertNotEquals(len(dates), 0)

        self.assertEquals(dates[0][0].time(), (utcstart - one_hour).time())
        self.assertEquals(dates[0][1].time(), utcend.time())

        for i in range(1, len(dates)):
            self.assertEquals(dates[i][0].time(), utcstart.time())
            self.assertEquals(dates[i][1].time(), utcend.time())

        # generate local timezone sequence of blackout dates for the
        # entire range.  Despite the complexity of the underlying UTC
        # representation, the local times should all be the same.
        dates = my_bo.generateDates(utcstart,
                                    utcuntil,
                                    local_timezone = True)
        self.assertNotEquals(len(dates), 0)

        for i in dates:
            self.assertEquals(i[0].time(), localstart.time())
            self.assertEquals(i[1].time(), localend.time())
