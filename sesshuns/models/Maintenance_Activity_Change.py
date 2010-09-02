######################################################################
#
#  Maintenance_Activity_Change.py - defines model for the
#  maintenance_activity_change table, which lists names and timestamps
#  of users who created/modified/approved a maintenance activity.
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

from django.db                  import models
from django.contrib.auth.models import User as djangoUser

class Maintenance_Activity_Change(models.Model):

    responsible = models.TextField(null = True, blank = True)
    date = models.DateTimeField()

    class Meta:
        db_table  = "maintenance_activity_change"
        app_label = "sesshuns"

    def __unicode__(self):
                    
        date = str(self.date)
        return "%s -- %s" % (self.responsible, date)
