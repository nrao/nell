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

from django.db import models

from Sesshun  import Sesshun
from Receiver import Receiver

class Receiver_Group(models.Model):
    session        = models.ForeignKey(Sesshun)
    receivers      = models.ManyToManyField(
                                  Receiver
                                , db_table = "receiver_groups_receivers")

    class Meta:
        db_table  = "receiver_groups"
        app_label = "scheduler"

    def __unicode__(self):
        return "Rcvr Group for Sess: (%s): %s" % \
               (self.session.id,
                " ".join([r.abbreviation for r in self.receivers.all()]))

    def __str__(self):
        return "(%s)" % \
               " OR ".join([r.abbreviation for r in self.receivers.all()])

