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

from django.db         import models

from SessionSeparation import SessionSeparation
from pht.utilities     import *

class Monitoring(models.Model):

    # inner loop - also uses session's: repeat, separation, interval_time
    start_time           = models.DateTimeField(null = True) 
    window_size          = models.IntegerField(null = True) # days
    # outter loop
    # TBF: needed?
    #outer_start_time     = models.DateField(null = True) 
    outer_window_size    = models.IntegerField(null = True) # days
    outer_repeats        = models.IntegerField(null = True)
    outer_separation     = models.ForeignKey(SessionSeparation, null = True)
    outer_interval       = models.IntegerField(null = True)
    # comma-separated list of integers
    custom_sequence      = models.CharField(null = True, max_length = 2000) 

    class Meta:
        db_table  = "pht_monitoring"
        app_label = "pht"

    
