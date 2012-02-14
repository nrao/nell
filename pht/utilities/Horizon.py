# Copyright (C) 2005 Associated Universities, Inc. Washington DC, USA.
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

# $Id: Horizon.py,v 1.6 2006/06/26 12:36:33 mclark Exp $

import math
from mx              import DateTime
from nell.utilities  import TimeAgent

class Horizon:

    """
    This class has been canabalized from the Horizon class in 
    sparrow's gbt/api/turtle/src/Horizon.py.
    It is primarily responsible for making calculations concering
    when a source may rise or set.
    """

    def __init__(self, physical_horizon = 5.25):
        "Takes the encoder elevation definition of horizon in degrees."
        assert physical_horizon < 90, \
               "Horizon's physical elevation must be less than 90 degrees."
        self.horizon = physical_horizon

    def riseSet2centerWidth(self, rise, set):
        """
        Convert endpoints to a center point and width.
        All in DateTimeDelta's.
        """

        # inputs are DateTimeDelta's
        # assuming hours are 0 - 24.
        if rise.hours < set.hours:
            width = set.hours - rise.hours
        else:
            width = (set.hours + 24.0) - rise.hours
        center = rise.hours + (width/2.0)
        if center > 24.0:
            center -= 24.0
        # so are the outputs
        return (DateTime.DateTimeDelta(0, center, 0, 0)
              , DateTime.DateTimeDelta(0, width, 0, 0))

    def getRightAscension(self, h):
        return TimeAgent.Degrees2RelativeTime(h).hours

    def riseSetLSTs(self, raDegress, decDegrees, now = None):
        """
        For a source at apparent location (ApparentRaDec), and for a
        horizon corrected for refraction (all in degrees), returns
        the next rise and set times in LST as a DateTimeDelta objects.
        For northern circumpolar objects rise is current time and set
        is None; for southern circumpolar objects rise is None and set
        is current time.
        """
        h = raDegress
        v = decDegrees
        if now is None:
            now = DateTime.gmt()
        ra = self.getRightAscension(h)
        dec = v 
        gblst = TimeAgent.Absolute2RelativeLST(now)
        current_ha = gblst - ra
        # HA must be between -12 and +12 hours.
        if current_ha < -12:
            current_ha = current_ha + 24.0
        elif current_ha > 12:
            current_ha = current_ha - 24.0

        horizon_ha = self.hourAngleIntersection(dec)

        # Does the source set?
        if horizon_ha >= 12.0:
            return (gblst, None) 
        # Does the source rise?
        elif horizon_ha <= 0:
            return (None, gblst)
        # So when?
        else:
            # Rise LST is when the HA = -horizon_ha
            # Set LST is when HA = +horizon_ha
            lstrise = ra - horizon_ha
            lstset = ra + horizon_ha
            # Keep it in the future.
            if lstrise < 0:
                lstrise += 24
            if lstset < 0:
                lstset += 24
            return (DateTime.DateTimeDelta(0, lstrise, 0, 0),
                    DateTime.DateTimeDelta(0, lstset, 0, 0))

    def hourAngleIntersection(self, declination):
        """
        Computes the absolute hour angle at which a source
        at the declination intersects the horizon corrected
        for refraction.
        Input values are in degrees, result is in hours.
        Non-rising sources return 0 and non-setting sources
        return 12.
        """
        _, gbtlat, _ = TimeAgent.GBT_LOCATION
        gbtlat = DateTime.DateTimeDeltaFrom(gbtlat).hours
        slat = math.sin(self.degrees2Radians(gbtlat))
        clat = math.cos(self.degrees2Radians(gbtlat))
        delev = self.refractionCorrection()
        e2 = self.horizon - delev
        sinelv = math.sin(self.degrees2Radians(e2))
        sdec = math.sin(self.degrees2Radians(declination))
        cdec = math.cos(self.degrees2Radians(declination))
        cosH = (sinelv - sdec*slat)/(cdec*clat)

        # Does the source rise?
        if cosH > 1.0:
            return 0.0
        # Does the source set?
        elif cosH < -1.0:
            return 12.0
        # So where?
        else:
            return abs(math.acos(cosH)*180.0/math.pi)/15

    def refractionCorrection(self):
        "Returns the approximate refraction correction using degrees."
        aa = self.horizon + (4.56934/(2.19001 + self.horizon))
        return (62.2/3600.0)/(math.tan(self.degrees2Radians(aa)))

    def degrees2Radians(self, degrees):
        "Utility function for trignometric function arguments."
        return degrees*math.pi/180.0
