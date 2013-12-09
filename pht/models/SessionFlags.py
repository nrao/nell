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

from django.db                 import models

class SessionFlags(models.Model):

    """
    Most of the boolean fields here could be handled also as
    SessionParameters, but the logic for booleans in that table
    can be confusing, so we thought we'd take this more direct path.
    """
    
    # note that these are all False by default
    thermal_night = models.BooleanField(default = False)
    rfi_night     = models.BooleanField(default = False)
    optical_night = models.BooleanField(default = False)
    transit_flat  = models.BooleanField(default = False)
    guaranteed    = models.BooleanField(default = True)
    
    def __str__(self):

        return "Thermal: %s, Optical: %s, RFI: %s, Transit: %s, Guaranteed: %s" % \
            (self.thermal_night
           , self.optical_night
           , self.rfi_night
           , self.transit_flat
           , self.guaranteed
            )

    class Meta:
        db_table  = "pht_session_flags"
        app_label = "pht"


