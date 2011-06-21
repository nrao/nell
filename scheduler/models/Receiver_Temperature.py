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

from django.db  import models

from Receiver import Receiver

class Receiver_Temperature(models.Model):
    receiver    = models.ForeignKey(Receiver)
    frequency   = models.FloatField(help_text = "GHz")
    temperature = models.FloatField(help_text = "K")

    def __unicode__(self):
        return "%s at %f is %f" % \
          ( self.receiver.name
          , self.frequency
          , self.temperature)

    class Meta:
        db_table  = "receiver_temperatures"
        app_label = "scheduler"

    def jsondict(self):
        return {"id"            : self.id
              , "receiver"      : self.receiver.name
              , "frequency"     : self.frequency
              , "temperature"   : self.temperature
               }

