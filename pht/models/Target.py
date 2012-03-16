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

from mx                        import DateTime
from pht.utilities             import *
from pht.utilities.Conversions import Conversions
from pht.utilities.Horizon     import Horizon

class Target(models.Model):

    ra                = models.FloatField(null = True) # rads
    dec               = models.FloatField(null = True) # rads
    center_lst        = models.FloatField(null = True) # rads
    lst_width         = models.FloatField(null = True) # rads
    min_lst           = models.FloatField(null = True) # rads
    max_lst           = models.FloatField(null = True) # rads
    elevation_min     = models.FloatField(null = True) # rads
    solar_avoid       = models.FloatField(null = True) # rads
    # for storing the raw values from pst
    pst_min_lst       = models.CharField(null = True, max_length = 255)
    pst_max_lst       = models.CharField(null = True, max_length = 255)
    pst_elevation_min = models.CharField(null = True, max_length = 255)

    class Meta:
        db_table  = "pht_targets"
        app_label = "pht"

    def calcLSTrange(self):
        """
        Returns the minimum and maximum LST from the position
        and the minimum elevation (in radians).
        """

        if self.ra is None or self.dec is None:
            return (None, None)

        # our utility tool - it takes everything in degrees
        if self.elevation_min is not None:
            h = Horizon(rad2deg(self.elevation_min))
        else:
            h = Horizon()

        # and the tool returns DateTimeDelta's
        rise, set = h.riseSetLSTs(rad2deg(self.ra)
                                , rad2deg(self.dec))

        # unless this is a special case!
        if set is None:
            # our source never sets - it's always up!
            return (0.0, hr2rad(24.0))
        if rise is None:
            # our source never rises 
            return (0.0, 0.0)

        minLst = hr2rad(h.normalizeHours(rise))
        maxLst = hr2rad(h.normalizeHours(set))

        return (minLst, maxLst)

    def calcCenterWidthLST(self, minLst = None, maxLst = None):
        """
        Returns the center LST and LST width based off the min &
        max LST's (all in radians).
        """

        if minLst is None:
            minLst = self.min_lst
        if maxLst is None:
            maxLst = self.max_lst
        if minLst is None or maxLst is None:    
            return (None, None)

        # our utility tool - it takes everything in degrees
        if self.elevation_min is not None:
            h = Horizon(rad2deg(self.elevation_min))
        else:
            h = Horizon()

        
        # and the tool returns DateTimeDelta's
        minLst = DateTime.DateTimeDelta(0, rad2hr(minLst), 0, 0)
        maxLst = DateTime.DateTimeDelta(0, rad2hr(maxLst), 0, 0)
        center, width = h.riseSet2centerWidth(minLst, maxLst)

        return (hr2rad(center.hours), hr2rad(width.hours))
                                            
            
                           
        
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
