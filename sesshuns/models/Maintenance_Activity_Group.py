######################################################################
#
#  Maintenance_Activity_Group.py - defines the model classes for the
#  resource calendar.
#
#  Copyright (C) 2010 Associated Universities, Inc. Washington DC, USA.
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

from django.db        import models
from scheduler.models import Period, Window
from datetime         import datetime, timedelta
from nell.utilities   import TimeAgent

######################################################################
# Maintenance_Activity_Group is a collection points for all
# maintenance activities contemplated for a single maintenance period.
# When future maintenance periods take the form of pending periods or
# electives their exact date is not known.  It is not even known if
# one will precede another.  So the system creates as many
# Maintenance_Activity_Groups as there are possible maintenance
# activity dates for that week, labeling them 'A', 'B', etc.  It is
# guaranteed that 'A' will be then attached to the earliest
# maintenance date, 'B' to the next one, etc.
#
# The following is a use case, assuming 2 maintenance days denoted by
# equal electives (date range exactly the same: Tuesday-Friday).
#
#   1) The system sees the two electives for that week.  It then
#   creates (as needed) 2 Maintenance_Activity_Groups, labeling one
#   'A' and the other 'B'.  It does nothing if they are already
#   created.  It truncates the list if the number of elective
#   maintenance electives decreased, deleting the lowest rank ('A' is
#   highest).  It increases the list if the number of maintenance
#   electives increased.  Deletions of Maintenance_Activity_Groups are
#   'soft', enabling the administrators to restore them or the
#   activities attached to them.
#
#   2) These are now be displayed on the calendar in order, on the
#   Monday of the week, where maintenance personnel can attach
#   activities to them.  They are not attached to any periods yet.
#
#   3) The scheduler schedules one of the electives.
#
#   4) The calendar notes this and attaches group 'A' to the published
#   period.
#
#   5) The scheduler schedules the second one, at a date that comes
#   after the first one.
#
#   6) The calendar notes this and attaches group 'B' to the published
#   period.
#
#       ---OR---
#
#   5) The scheduler schedules the second one, but on a date that
#   comes before the first scheduled elective.
#
#   6) The calendar notes that 'B' will come before 'A', and swaps the
#   two.  Now 'A' is attached to the earlier date, and 'B' to the
#   later date.
#
#   7) Maintenance_Activity_Groups remain attached to periods even
#   after periods are published.  This allows the calendar to maintain
#   this 'A', 'B' ... ordering even if the scheduler alters the date
#   of an already published period.
######################################################################

class Maintenance_Activity_Group(models.Model):

    period  = models.ForeignKey(Period, null = True)
    rank    = models.CharField(max_length = 2)          # 'A', 'B', etc.
    deleted = models.BooleanField(default = False)
    # The Monday of the maintenance week.  This is here so that
    # maintenance activity groups can be queried by the week of
    # interest.
    week    = models.DateTimeField(null = True)
    
    class Meta:
        db_table  = "maintenance_activity_group"
        app_label = "sesshuns"

    def __unicode__(self):
        if self.maintenance_activity_set.count():
            sr = ", ".join([e.get_subject() for e in self.maintenance_activity_set.all()])
        else:
            sr = "Empty"
        return sr

    def get_week(self):
        return TimeAgent.truncateDt(self.week)

