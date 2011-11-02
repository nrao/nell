######################################################################
#
#  TestMaintenanceActivityGroup.py
#
#  Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

from test_utils            import NellTestCase
from users.models          import *
from scheduler.models      import *
from scheduler.tests.utils import create_maintenance_period
from scheduler.tests.utils import create_maintenance_elective
from users.tests.utils     import create_maintenance_activity
from datetime              import datetime, timedelta

class TestMaintenanceActivityGroup(NellTestCase):
    def setUp(self):
        super(TestMaintenanceActivityGroup, self).setUp()
        self.week = datetime(2011, 04, 11)
        per_data = ((datetime(2011, 04, 12, 8), 8),
                    (datetime(2011, 04, 13, 8), 8),
                    (datetime(2011, 04, 14, 8), 8),
                    (datetime(2011, 04, 15, 8), 8))
        self.me1 = create_maintenance_elective(per_data)
        self.me2 = create_maintenance_elective(per_data)
        self.mp1 = create_maintenance_period(datetime(2011, 04, 11, 8), 8,
                                             'Pending')
        self.deleted = Period_State.objects.get(name = 'Deleted')
        self.pending = Period_State.objects.get(name = 'Pending')
        self.scheduled = Period_State.objects.get(name = 'Scheduled')


    def tearDown(self):
        super(TestMaintenanceActivityGroup, self).tearDown()


    def test_maintenance_groups(self):
        # get the maintenance groups for the week of April 11, 2011
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        # there should be 2 maintenance groups: 2 electives
        # we don't pick up the pending period from the fixed session

        self.assertEqual(len(mags), 2)

        # mag should have period set to None if elective.  Elective
        # not scheduled yet.  Pending period should be set and is the
        # last one in the list.
        for i in range(0, len(mags) - 1):
            mag = mags[i]
            self.assertEqual(mag.period, None)
            self.assertEqual(mag.rank, chr(65 + i))
            self.assertEqual(mag.get_week(), self.week)
            # not scheduled electives, so mag get_start() should be
            # the same as mag.get_week()
            self.assertEqual(mag.get_start(), mag.get_week())

        self.mp1.state = self.deleted
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week,
                                                                          include_deleted = True)
        # there should still be 2 maintenance groups, the two electives.
        self.assertEqual(len(mags), 2)

        # delete one of the electives.
        self.me1.setComplete(True)
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week,
                                                                          include_deleted = True)
        # there should be 2 maintenance groups, but one deleted.
        self.assertEqual(len(mags), 2)
        self.assertEqual(mags[1].deleted, True)

        # now only return non-deleted ones.
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 1)
        
        # restore the period.
        self.mp1.state = self.pending
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 1)

        # restore the elective.
        self.me1.setComplete(False)
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 2)
        
        # now publish the fixed session's period
        self.mp1.state = self.scheduled
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 3)

    ######################################################################
    # This tests the assignemnt of groups to scheduled periods.  The
    # results should be:
    #
    # 1st scheduled elective, no matter when, should get 'A'
    #
    # 2nd scheduled elective should get 'B' if later than 'A', but 'A'
    # if earlier and other period should then get 'B'
    #
    # 3d scheduled period should get 'x' to denote a fixed maintenance
    # period.  It should be independend of the other two, regardless
    # of scheduled date.
    #
    # Subsequent changes to the scheduled periods (new dates,
    # deletions, etc.) should continue to be accounted for.
    ######################################################################
        
    def test_maintenance_assignment(self):

        # publish the fixed session's period
        self.mp1.state = self.scheduled
        self.mp1.save()

        # publish the first elective, publishing its Friday period.
        pds = self.me1.periods.all().order_by('start')
        p1 = pds[pds.count() - 1] # get last one, Friday.
        p1.publish()
        self.me1.setComplete(True)
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 3)
        
        # 0 is 'A', and period should be the recently scheduled
        # period.  'B'should be unassigned.  'x' should remain
        # unaffected.
        
        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p1.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period, None)
        # this is considered a fixed maintenance activity; should have a period.
        self.assertEqual('x', mags[2].rank)
        self.assertEqual(mags[2].period, self.mp1)
       
        # publish the second elective, for Tuesday
        
        pds = self.me2.periods.all().order_by('start')
        p2 = pds[0]
        p2.publish()
        self.me2.setComplete(True)
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 3)

        # 'A' now should point to 'p2', since it comes earlier in the
        # week. 'B' now should point to 'p1' (which used to have 'A'),
        # since it comes later in the week.  'C' should remain
        # unassigned.

        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p2.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period.id, p1.id)
        self.assertEqual('x', mags[2].rank)
        self.assertEqual(mags[2].period, self.mp1)

        # now schedule the pending non-elective period Monday.  This
        # period will still have 'x'; A will still be p2, and B will
        # still be p1.  (mags come back sorted by rank, with
        # non-elective ('x') last, sorted by start date.)
        
        self.mp1.publish()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(len(mags), 3)
        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p2.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period.id, p1.id)
        self.assertEqual('x', mags[2].rank)
        self.assertEqual(mags[2].period.id, self.mp1.id)

        # Now move the already scheduled non-elective self.mp1 to
        # Wednesday. Nothing should change!  A will still be p2, and B
        # will still be p1.
        
        self.mp1.start = datetime(2011, 04, 13, 8)
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p2.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period.id, p1.id)
        self.assertEqual('x', mags[2].rank)
        self.assertEqual(mags[2].period.id, self.mp1.id)

        # Now delete the middle period 'self.mp1'.  'A' and 'B' should
        # remain the same.

        self.mp1.state = self.deleted
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week,
                                                                          include_deleted = True)
        self.assertEqual(2, len(mags)) # only the two electives.
        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p2.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period.id, p1.id)
        
        # now revive 'self.mp1'.  C should reappear.
        self.mp1.state = self.scheduled 
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(3, len(mags)) # 'x' should reappear
        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p2.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period.id, p1.id)
        self.assertEqual('x', mags[2].rank)
        self.assertEqual(mags[2].deleted, False)
        self.assertEqual(mags[2].period.id, self.mp1.id)

        # and finally re-schedule 'self.mp1'. The two elective
        # activities should yet again remain unchanged.
        self.mp1.state = self.scheduled
        self.mp1.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        self.assertEqual(3, len(mags))
        self.assertEqual('A', mags[0].rank)
        self.assertEqual(mags[0].period.id, p2.id)
        self.assertEqual('B', mags[1].rank)
        self.assertEqual(mags[1].period.id, p1.id)
        self.assertEqual('x', mags[2].rank)
        self.assertEqual(mags[2].deleted, False)
        self.assertEqual(mags[2].period.id, self.mp1.id)


    def test_get_maintenance_activity_set(self):

        # publish the fixed sessions period
        self.mp1.state = self.scheduled
        self.mp1.save()

        # get the maintenance groups for the week of April 11, 2011
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        # there should be 3 maintenance groups: 2 electives, one pending period
        self.assertEqual(len(mags), 3)

        # there should be no activiites
        for mag in mags:
            self.assertEqual([], mag.get_maintenance_activity_set())

        # now there should be one each
        for i in range(3):
            ma = create_maintenance_activity()
            ma.set_description(str(i))
            ma.group = mags[i]
            ma.save()
        mags = Maintenance_Activity_Group.get_maintenance_activity_groups(self.week)
        for i, mag in enumerate(mags):
            self.assertEqual(str(i), mag.get_maintenance_activity_set()[0].description)

    def test_get_maintenance_activity_set_2(self):

        # returns true if a maintenance activity group contains an
        # instance derived from template 'templ'.
        def has_template_instance(templ, mas):
            for i in mas:
                if i.is_repeat_activity():
                    if i.repeat_template == templ:
                        return True
            return False

        def add_template(start, interval, end):
            t = create_maintenance_activity()
            t.repeat_interval = interval
            t._start = start
            t.repeat_end = end
            t.save()
            return t

        # simple case: a repeating activity, no published periods.
        # Daily activity should wind up on both 'A' and 'B', and
        # weekly/monthly only on 'A'.

        week = datetime(2011, 04, 11)
        t_daily = add_template(datetime(2011, 04, 01),
                               1,
                               datetime(2011, 04, 22))

        # get the maintenance activity groups.  Should be 2, one for
        # me1, one for me2.

        mags = Maintenance_Activity_Group\
            .get_maintenance_activity_groups(week)
        self.assertEqual(2, len(mags))
        mags.sort(key = lambda x: x.rank)
        masA = mags[0].get_maintenance_activity_set2()
        masB = mags[1].get_maintenance_activity_set2()

        # each of 'masA' and 'masB' should have an instance of
        # template 'ma':
        self.assertTrue(has_template_instance(t_daily, masA))
        self.assertTrue(has_template_instance(t_daily, masB))

        # Now create a weekly template:
        t_weekly = add_template(datetime(2011, 4, 6),
                                7,
                                datetime(2011, 4, 22))

        masA = mags[0].get_maintenance_activity_set2()
        masB = mags[1].get_maintenance_activity_set2()

        # 'A' should have a daily and a weekly, 'B' only the daily.
        self.assertTrue(has_template_instance(t_daily, masA))
        self.assertTrue(has_template_instance(t_daily, masB))
        self.assertTrue(has_template_instance(t_weekly, masA))
        self.assertFalse(has_template_instance(t_weekly, masB))

        self.assertEqual(len(masA), 2)
        self.assertEqual(len(masB), 1)

        # Now add a monthly but not due.  Should not show up.
        t_monthly_not_due = add_template(datetime(2011, 4, 6),
                                         30,
                                         datetime(2011, 7, 1))

        masA = mags[0].get_maintenance_activity_set2()
        masB = mags[1].get_maintenance_activity_set2()

        # Nothing should change.
        self.assertTrue(has_template_instance(t_daily, masA))
        self.assertTrue(has_template_instance(t_weekly, masA))
        self.assertFalse(has_template_instance(t_monthly_not_due, masA))
        self.assertTrue(has_template_instance(t_daily, masB))
        self.assertFalse(has_template_instance(t_weekly, masB))
        self.assertFalse(has_template_instance(t_monthly_not_due, masB))

        self.assertEqual(len(masA), 2)
        self.assertEqual(len(masB), 1)

        # Add a monthly, due the 14th, this week.
        t_monthly = add_template(datetime(2011, 3, 14),
                                 30,
                                 datetime(2011, 7, 1))

        masA = mags[0].get_maintenance_activity_set2()
        masB = mags[1].get_maintenance_activity_set2()

        # 'A' should carry 1 daily, 1 weekly and 1 monthly
        # 'B' should carry only 1 daily
        self.assertTrue(has_template_instance(t_daily, masA))
        self.assertTrue(has_template_instance(t_weekly, masA))
        self.assertTrue(has_template_instance(t_monthly, masA))
        self.assertTrue(has_template_instance(t_daily, masB))
        self.assertFalse(has_template_instance(t_weekly, masB))
        self.assertFalse(has_template_instance(t_monthly, masB))

        self.assertEqual(len(masA), 3)
        self.assertEqual(len(masB), 1)
