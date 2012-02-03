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

import MySQLdb as m
from pht.utilities import * 
import re

class Conversions(object):

    """
    Motivation for this class is all the string fields in the PST DB that hold float
    values.  This class provides ways to convert them to floats.
    """

    def __init__(self):

        # lists of regular expressions:

        # Hours:
        # Strict version of HH:MM:SS.S; w/ optional decimal place. ex: 10:00:00.0
        self.h1 = "(([0]?[0-9]|1[0-9]|2[0-4])(:)([0-5][0-9])?(:)?([0-5][0-9])?(.)(\d*))$"
        # Strict of HH MM SS.S; w/ optional decimal place 10 00 00.0
        self.h2 = "(([0]?[0-9]|1[0-9]|2[0-3])(\s)*([0-5][0-9])?(\s)*?([0-5][0-9])?(.)(\d*))$"
        # Strict Lettered format: 10h00m00s
        self.h3 = "(([0]?[0-9]|1[0-9]|2[0-3])([h,d])?\s*([0-5][0-9])(m)?\s*([0-5][0-9])?(.)(\d*)(s))$"

        # Degrees:
        # Strict version of DDD:MM:SS.S; w/ optional decimal place. ex: 10:00:00.0
        self.d1 = "([-+]([0]?[0-9][0-9]|36[0-5]|3[0-5][0-9]|[0-2][0-9][0-9])(:)([0-5][0-9])?(:)?([0-5][0-9])?(.)(\d*))$"
        # Strict of DDD MM SS.S; w/ optional decimal place 10 00 00.0
        self.d2 = "([-+]?([0]?[0-9][0-9]|36[0-5]|3[0-5][0-9]|[0-2][0-9][0-9])(\s)*([0-5][0-9])?(\s)*?([0-5][0-9])?(.)(\d*))$"
        # Strict Lettered format: 10d00m00s
        self.d3 = "([-+]?([0]?[0-9][0-9]|36[0-5]|3[0-5][0-9]|[0-2][0-9][0-9])([h,d])?\s*([0-5][0-9])(m)?\s*([0-5][0-9])?(.)(\d*)(s))$"

        # Desperation!  Will these work?
        # Anything with numbers and colons, plus spaces even
        self.r1 = '-?|\d*:\\s*\\d*:\\s*\\d*\\.?\\d*?$'
        # Simple float.  ex: 10.0
        self.r2 = "[-+]?[0-9]*\.?[0-9]"

        # how to use these?  Here we match up a regular expression, which if
        # a mathc is found, uses the conversion function given
        self.hourConversions = [(self.h1, sexigesimel2float)
                              , (self.h2, sexigesimelFormTwo2float)
                              , (self.h3, sexigesimelFormThree2float)
                              , (self.r1, sexigesimel2float)
                              , (self.r2, float)
                               ]

        self.degreeConversions = [(self.d1, sexigesimel2float)
                              , (self.d2, sexigesimelFormTwo2float)
                              , (self.d3, sexigesimelFormThree2float)
                              , (self.r1, sexigesimel2float)
                              , (self.r2, float)
                               ]

    def sexHrs2rad(self, str):
        "A string representing hours converted to float in radians"
        _, hrs = self.tryHourConversions(str)
        return hr2rad(hrs) if hrs is not None else None

    def sexDeg2rad(self, str):
        "A string representing degrees converted to float in radians"
        _, deg = self.tryDegreeConversions(str)
        return deg2rad(deg) if deg is not None else None

    def tryHourConversions(self, str):
        return self.tryConversions(str, 0.0, 24.0, self.hourConversions)

    def tryDegreeConversions(self, str):
        return self.tryConversions(str, -360.0, 360.0, self.degreeConversions)

    def tryConversions(self, str, minV, maxV, conversions):
        """
        Attempts to convert the given string using a number of pairs of 
        regular expressions and conversion methods.
        Also makes sure that the resultant float stays with the given bounds.
        """

        # clean it up first
        str = str.strip()
        str = str.replace(';', ':')

        anyMatch = False              
        match = False
        value = None
        for r, f in conversions:
            match, value = self.string2float(str, r, f)
            # do another check on value bounds        
            if value is not None:
                if value < minV or value > maxV:
                    value = None
            if match:
                anyMatch = True
            # quit as soon as we get a match
            if match and value is not None:
                break
        # If conversion works, this will be (True, float_value)        
        return anyMatch, value

    def string2float(self, str, rex, fn):
        """
        If the given string matches the regular expression, attempt
        to transform it to a float with the given function.
        Returns if the reg. expression was matched and the result
        of the transformation function.
        """

        p = re.compile(rex)
        matches = p.match(str)
        #print str, rex
        #print matches
        if matches is not None:
            # matches the reg expression, so try to transform it
            try:
                value = fn(str)
            except:
                value = None
            return (True, value)
        else:
            # does not match reg expression!
            return (False, None)
