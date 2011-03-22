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

from django.db         import models
from scheduler.models  import Period, Window

class Maintenance_Activity_Group(models.Model):

    period = models.ForeignKey(Period, null = True)
    window = models.ForeignKey(Window, null = True)

    class Meta:
        db_table  = "maintenance_activity_group"
        app_label = "sesshuns"

    def __unicode__(self):
        if self.maintenance_activity_set.count():
            sr = ", ".join([e.get_subject() for e in self.maintenance_activity_set.all()])
        else:
            sr = "Empty"
        return sr

    def get_start(self):
        period = self._get_period()

        if period:
            return period.start
        else:
            return None

    def get_duration(self):
        period = self._get_period()
        
        if period:
            return period.duration
        else:
            return None

    def get_time_sorted_set(self):
        return self.maintenance_activity_set.order_by('start')

    def _get_period(self):
        if self.period:
            return self.period
        elif self.window:
            return self.window.period if self.window.period else self.window.default_period
        else:
            return None
