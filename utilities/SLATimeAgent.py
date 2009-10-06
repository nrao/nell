# Copyright (C) 2006 Associated Universities, Inc. Washington DC, USA.
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

# $Id: TimeAgent.py,v 1.4 2007/06/21 14:20:47 mclark Exp $

from TimeAgent  import *
import slalib

def dt2tlst(dt):
    "Translates from UT datetime to LST time."
    relative_hours = Absolute2RelativeLST(dt)
    lst_hours = int(relative_hours)
    fractional_minutes = (relative_hours - lst_hours)*60.0
    lst_minutes = int(fractional_minutes)
    fractional_seconds =(fractional_minutes - lst_minutes)*60.0
    lst_seconds = int(round(fractional_seconds)) % 60
    return datetime.time(lst_hours, lst_minutes, lst_seconds)

def GbtLatitudeInRadians():
    """
    Translates GBT latitude from degrees, minutes, and seconds to radians
    """
    return GBTLAT

def Absolute2RelativeLST(absolute):
    "Returns LST as hours given UTC as a datetime."
    absolute = dt2mxDT(absolute)
    gmst = (180.0/math.pi)*slalib.sla_gmst(absolute.mjd)
    gbls = (gmst + GBTLONG)/15.0
    if gbls < 0:
        gbls = 24 + gbls
    return gbls

def RelativeLST2AbsoluteTime(lst, now = None):
    """
    Returns today's DateTime in UTC, defined as first corresponding
    time after now, from given LST in hours.
    """
    lst = DateTime.DateTimeDelta(0, lst, 0, 0)
    if now is None:
        now = DateTime.gmt()
    else:
        now = dt2mxDT(now)

    # Now's mjd at 0h
    mjd0 = int(now.mjd)

    # Convert requested LST to degrees
    requested_lst = 15*lst.hours

    # Local LMST for 0h UT in degrees
    lst0 = (180.0/math.pi)*slalib.sla_gmst(mjd0) + GBTLONG

    # LST difference between 0h UT and requested LST
    lst_offset = requested_lst - lst0

    solar_sidereal_ratio = (365.25/366.25)

    # options for solar time at 1 day sidereal intervals
    options = []
    for cycle in range(720, -1080, -360):
        solar_time = ((lst_offset-cycle)/15.0)*solar_sidereal_ratio
        mjd = mjd0 + solar_time/24
        options.append(DateTime.DateTimeFromMJD(mjd))

    # Select the time following the target time
    target = DateTime.DateTimeFromMJD(now.mjd)
    for option in options:
        if target < option:
            return mxDT2dt(option)
    return mxDT2dt(option[-1])

