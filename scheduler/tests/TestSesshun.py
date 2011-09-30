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

from datetime               import datetime, timedelta

from test_utils             import BenchTestCase, timeIt
from utilities              import TimeAgent
from scheduler.models       import *
from scheduler.httpadapters import *
from utils                  import create_sesshun, fdata, create_blackout

class TestSesshun(BenchTestCase):

    def setUp(self):
        super(TestSesshun, self).setUp()
        self.sesshun = create_sesshun()

    def test_usesDeletedReceiver(self):

        # setup
        L = Receiver.get_rcvr("L")
        S = Receiver.get_rcvr("S")
        X = Receiver.get_rcvr("X")
        rg = Receiver_Group(session = self.sesshun)
        rg.save()
        rg.receivers.add(L)
        rg.receivers.add(S)

        # start w/ no deleted rcvrs
        self.assertEqual(False, self.sesshun.usesDeletedReceiver())

        # delete a rcvr
        X.deleted = True
        X.save()
        self.assertEqual(False, self.sesshun.usesDeletedReceiver())

        # delete another rcvr
        S.deleted = True
        S.save()
        self.assertEqual(True, self.sesshun.usesDeletedReceiver())

        # clean up
        X.deleted = False
        X.save()
        S.deleted = False
        X.save()

    def test_create(self):
        expected = Sesshun.objects.get(id = self.sesshun.id)
        self.assertEqual(expected.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(expected.name, fdata["name"])

    def test_get_tracking_error_threshold(self):

        # should give the default value for a sparse array
        th = self.sesshun.get_tracking_error_threshold()
        self.assertEquals(0.2, th)

        # now make it use Mustang - a filled array
        rg =  Receiver_Group(session = self.sesshun)
        rg.save()
        mba = Receiver.objects.get(abbreviation = "MBA")
        rg.receivers.add(mba)
        rg.save()
        th = self.sesshun.get_tracking_error_threshold()
        self.assertEquals(0.4, th)

        # now give change it via the obs param
        parameter = Parameter.objects.get(name="Tr Err Limit")
        obs = Observing_Parameter(session = self.sesshun
                                , parameter = parameter)
        obs.setValue(0.5)
        obs.save()
        th = self.sesshun.get_tracking_error_threshold()
        self.assertEquals(0.5, th)


    @timeIt
    def test_init_from_post(self):
        s = Sesshun()
        fdata["receiver"] = "((K & Ku) & L)"
        SessionHttpAdapter(s).init_from_post(fdata)

        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target.source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.get_lst_string('LST Exclude'),fdata["lst_ex"])

        # does this still work if you requery the DB?
        ss = Sesshun.objects.all()
        self.assertEqual(2, len(ss))
        s = ss[1]
        # notice the change in type when we compare this way!
        self.assertEqual(s.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(s.target.source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])

    @timeIt
    def test_update_from_post(self):
        ss = Sesshun.objects.all()
        s = Sesshun()
        adapter = SessionHttpAdapter(s)
        adapter.init_from_post(fdata)

        self.assertEqual(s.frequency, fdata["freq"])
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target.source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.get_lst_string('LST Exclude'),fdata["lst_ex"])

        # change a number of things and see if it catches it
        ldata = dict(fdata)
        ldata["freq"] = "10"
        ldata["source"] = "new source"
        ldata["total_time"] = "99"
        ldata["enabled"] = "true"
        ldata["transit"] = "true"
        ldata["time_of_day"] = "RfiNight"
        ldata["lst_ex"] = "2.00-4.00"
        ldata["receiver"] = "(K & (X | (L | C)))"
        ldata["xi_factor"] = 1.76
        adapter.update_from_post(ldata)

        # now get this session from the DB
        ss = Sesshun.objects.all()
        s = ss[1]
        self.assertEqual(s.frequency, float(ldata["freq"]))
        self.assertEqual(s.allotment.total_time, float(ldata["total_time"]))
        self.assertEqual(s.target.source, ldata["source"])
        self.assertEqual(s.status.enabled, ldata["enabled"] == "true")
        self.assertEqual(s.transit(), ldata["transit"] == "true")
        self.assertEqual(s.time_of_day(), ldata["time_of_day"])
        self.assertEqual(s.get_lst_string('LST Exclude'), ldata["lst_ex"])
        self.assertEqual(s.get_min_eff_tsys_factor(), ldata["xi_factor"])
        self.assertEqual(s.get_elevation_limit(),fdata["el_limit"])
        rgs = s.receiver_group_set.all().order_by('id')
        self.assertEqual(2, len(rgs))
        self.assertEqual(['K']
                       , [r.abbreviation for r in rgs[0].receivers.all().order_by('id')])
        self.assertEqual(['L', 'C', 'X']
                       , [r.abbreviation for r in rgs[1].receivers.all().order_by('id')])

    def test_update_from_post2(self):
        ss = Sesshun.objects.all()
        s = Sesshun()
        adapter = SessionHttpAdapter(s)
        adapter.init_from_post(fdata)

        self.assertEqual(s.frequency, fdata["freq"])
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target.source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.original_id, int(fdata["orig_ID"]))

        # check to see if we can handle odd types
        ldata = dict(fdata)
        ldata["freq"] = "10.5"
        ldata["source"] = None
        ldata["total_time"] = "99.9"
        ldata["orig_ID"] = "0.0"
        ldata["enabled"] = "true"
        adapter.update_from_post(ldata)

        # now get this session from the DB
        ss = Sesshun.objects.all()
        s = ss[1]
        self.assertEqual(s.frequency, float(ldata["freq"]))
        self.assertEqual(s.allotment.total_time, float(ldata["total_time"]))
        self.assertEqual(s.target.source, ldata["source"])
        self.assertEqual(s.status.enabled, True) # "True" -> True
        self.assertEqual(s.original_id, 0) #ldata["orig_ID"]) -- "0.0" -> Int

    def test_get_receiver_blackout_ranges(self):
        # Schedule = 4/01/2009:   450,   600,  800
        #            4/06/2009:   600,   800, 1070
        #            4/11/2009:   800,  1070,  1_2
        #            4/16/2009:  1070,   1_2,  2_3
        #            4/21/2009:   1_2,   2_3,  4_6
        #            4/26/2009:   2_3,   4_6, 8_10
        #            5/01/2009:   4_6,  8_10, 12_18
        #            5/06/2009:  8_10, 12_18, 18_26
        #            5/11/2009: 12_18, 18_26, 26_40
        start   = datetime(2009, 4, 1, 0)
        end     = datetime(2009, 6, 1, 0)
        rcvr_id = 3
        for i in range(9):
            start_date = start + timedelta(5*i)
            for j in range(1, 4):
                rcvr_id = rcvr_id + 1
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = rcvr_id)
                rs.save()
            rcvr_id = rcvr_id - 2

        # no receivers
        blackouts = self.sesshun.get_receiver_blackout_ranges(start, end)
        self.assertEquals([], blackouts)

        # Now add some receivers to this session
        SessionHttpAdapter(self.sesshun).save_receivers('L | (X & S)')
        blackouts = self.sesshun.get_receiver_blackout_ranges(start, end)
        # No available receivers at these times:
        expected = [(datetime(2009, 4, 1), datetime(2009, 4, 11))
                  , (datetime(2009, 5, 1), None)]
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # No available receivers at these times:
        expected = [(datetime(2009, 4, 1), datetime(2009, 4, 26))
                  , (datetime(2009, 5, 1), datetime(2009, 5, 6))]
        SessionHttpAdapter(self.sesshun).save_receivers('K | (X & S)')

        blackouts = self.sesshun.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # No available receivers at these times:
        expected = [(datetime(2009, 4, 11), None)]
        SessionHttpAdapter(self.sesshun).save_receivers('600')

        blackouts = self.sesshun.get_receiver_blackout_ranges(start, end)
        self.assertEquals(expected, blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # Always an available receiver.
        SessionHttpAdapter(self.sesshun).save_receivers('(800 | S) | Ku')

        blackouts = self.sesshun.get_receiver_blackout_ranges(start, end)
        self.assertEquals([], blackouts)
        self.sesshun.receiver_group_set.all().delete()

        # Clean up.
        Receiver_Schedule.objects.all().delete()

    @timeIt
    def test_get_time_not_schedulable(self):
        "Test a number of overlapping bad things"

        # First bad thing: a receiver schedule that leaves out our rx
        # Schedule = 4/01/2009:   450,   600,  800
        #            4/06/2009:   600,   800, 1070
        #            4/11/2009:   800,  1070,  1_2
        #            4/16/2009:  1070,   1_2,  2_3
        #            4/21/2009:   1_2,   2_3,  4_6
        #            4/26/2009:   2_3,   4_6, 8_10
        #            5/01/2009:   4_6,  8_10, 12_18
        #            5/06/2009:  8_10, 12_18, 18_26
        #            5/11/2009: 12_18, 18_26, 26_40
        start   = datetime(2009, 4, 1, 0) # April 1
        end     = datetime(2009, 6, 1, 0) # June  1
        rcvr_id = 3
        for i in range(9):
            start_date = start + timedelta(5*i)
            for j in range(1, 4):
                rcvr_id = rcvr_id + 1
                rs = Receiver_Schedule()
                rs.start_date = start_date
                rs.receiver = Receiver.objects.get(id = rcvr_id)
                rs.save()
            rcvr_id = rcvr_id - 2

        # Now add some receivers to this session
        SessionHttpAdapter(self.sesshun).save_receivers('L | (X & S)')
        blackouts = self.sesshun.get_time_not_schedulable(start, end)

        # No available receivers at these times:
        exp = [(datetime(2009, 4, 1), datetime(2009, 4, 11))
             , (datetime(2009, 5, 1), end)
              ]
        expected = set(exp)
        self.assertEquals(exp, blackouts)

        # Now add a project w/ prescheduled times.
        otherproject = Project()
        pdata = {"semester"   : "09A"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
               , "notes"      : "notes"
               , "schd_notes" : "scheduler's notes"
        }
        adapter = ProjectHttpAdapter(otherproject)
        adapter.update_from_post(pdata)

        othersesshun = create_sesshun()
        othersesshun.project = otherproject
        othersesshun.save()

        fdata = {'session'  : othersesshun.id
               , 'date'     : '2009-04-20'
               , 'time'     : '13:00'
               , 'duration' : 1.0
               , 'backup'   : False}
        otherperiod = Period()
        adapter = PeriodHttpAdapter(otherperiod)
        adapter.init_from_post(fdata, 'UTC')
        otherperiod.state = Period_State.objects.filter(abbreviation = 'S')[0]
        otherperiod.save()

        #exp.append((datetime(2009, 4, 20, 13, 0), datetime(2009, 4, 20, 14, 0)))
        exp = [(datetime(2009, 4, 1), datetime(2009, 4, 11))
             , (datetime(2009, 4, 20, 13), datetime(2009, 4, 20, 14))
             , (datetime(2009, 5, 1), end)
              ]

        blackouts = self.sesshun.get_time_not_schedulable(start, end)
        self.assertEquals(exp, blackouts)

        # how much time is that?
        hrsNotSchedulable = sum([TimeAgent.timedelta2minutes(b[1] - b[0])/60.0\
            for b in blackouts])
        self.assertEquals(985.0, hrsNotSchedulable)

        # how does this work when limiting the range?
        newEnd = datetime(2009, 4, 3)
        blackouts = self.sesshun.get_time_not_schedulable(start, newEnd)
        self.assertEquals([(start, newEnd)], blackouts)

        # extend this with a Project Blackout
        blackout = create_blackout(project = self.sesshun.project,
                                   start   = datetime(2009, 4, 18, 12),
                                   end     = datetime(2009, 4, 23, 12),
                                   repeat  = 'Once')

        exp = [(datetime(2009, 4, 1), datetime(2009, 4, 11))
             , (datetime(2009, 4, 18, 12), datetime(2009, 4, 23, 12))
             , (datetime(2009, 5, 1), end)
              ]
        blackouts = self.sesshun.get_time_not_schedulable(start, end)
        self.assertEquals(exp, blackouts)


        # test the time available blacked out calculations
        # Calculate the expected result:
        # it turns out that the project blackout overlaps with all
        # schedulable time, except for one hour on 4/20
        hrsBlackedOut = (TimeAgent.timedelta2minutes(blackout.getEndDate()
                                                     - blackout.getStartDate()) / 60.0) - 1.0
        totalTime = TimeAgent.timedelta2minutes(end - start) / 60.0
        hrsSchedulable = totalTime - hrsNotSchedulable

        s, b, ss, bb = self.sesshun.getBlackedOutSchedulableTime(start, end)
        self.assertEquals(hrsSchedulable, s)
        self.assertEquals(hrsBlackedOut, b)

        # test it some more, but in different ranges
        start = datetime(2009, 5, 1)
        s, b, ss, bb = self.sesshun.getBlackedOutSchedulableTime(start, end)
        self.assertEquals(0.0, b)

        start = datetime(2009, 4, 22)
        end   = datetime(2009, 4, 26)
        totalTime = TimeAgent.timedelta2minutes(end - start) / 60.0
        s, b, ss, bb = self.sesshun.getBlackedOutSchedulableTime(start, end)
        self.assertEquals(totalTime, s)
        self.assertEquals(36.0, b)

        # cleanup
        self.sesshun.receiver_group_set.all().delete()

    # This test commented out simply because it takes soo long to create
    # and delete a sufficient number of sesshuns to see a timing difference
    # in first()
    #@timeIt
    #def run_first(self):
    #    s = Sesshun.objects.all()[0]

    #def test_first(self):
    #    ss = [create_sesshun() for i in range(10000)]
    #    self.run_first()
    #    for s in ss:
    #        s.delete()
