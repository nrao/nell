######################################################################
#
#  Maintenance_Receivers_Swap.py - model for the
#  maintenance_receivers_swap table.  This table keeps track of
#  requests to change receivers as a maintenance activity.
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

#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

from django.db         import models
from scheduler.models  import Receiver

class Maintenance_Receivers_Swap(models.Model):

    down_receiver = models.ForeignKey(Receiver, related_name = "down_receiver_set")
    up_receiver   = models.ForeignKey(Receiver, related_name = "up_receiver_set")

    class Meta:
        db_table = "maintenance_receivers_swap"
        app_label = "users"

    def __unicode__(self):
        return "%s --> %s" % (self.down_receiver.name, self.up_receiver.name)
