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

from pht.utilities import *
from pht.utilities.Conversions import Conversions

class Target(models.Model):

    ra                = models.FloatField(null = True) # rads
    dec               = models.FloatField(null = True) # rads
    center_lst        = models.FloatField(null = True) # rads
    lst_width         = models.FloatField(null = True) # rads
    min_lst           = models.FloatField(null = True) # rads
    max_lst           = models.FloatField(null = True) # rads
    elevation_min     = models.FloatField(null = True) # rads
    # for storing the raw values from pst
    pst_min_lst       = models.CharField(null = True, max_length = 255)
    pst_max_lst       = models.CharField(null = True, max_length = 255)
    pst_elevation_min = models.CharField(null = True, max_length = 255)

    class Meta:
        db_table  = "pht_targets"
        app_label = "pht"

    @staticmethod
    def createFromSqlResult(result):
        """
        Creates a new Target instance initialized using the request from
        an SQL query.
        """
 
        c = Conversions()

        target = Target(min_lst = c.sexHrs2rad(result['MINIMUM_LST'])
                      , max_lst = c.sexHrs2rad(result['MAXIMUM_LST'])
                      # TBF: why bother importing?  It is soooo FUBAR!
                      #, elevation_min = result['ELEVATION_MINIMUM']      
                      , pst_max_lst = result['MAXIMUM_LST']
                      , pst_min_lst = result['MINIMUM_LST']
                      , pst_elevation_min = result['ELEVATION_MINIMUM']
                       )
        target.save()
        return target
