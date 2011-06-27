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

import TimeAgent

class VersionDiff():

    def __init__(self, dt = None, field = None, value1 = None, value2 = None):

        self.dt = dt # when the change was made from value1 to value2
        self.field = field
        self.value1 = value1  # original value
        self.value2 = value2  # new value

        self.dtFormat = "%Y-%m-%d %H:%M:%S"

    def timestamp(self, test):
        """
        The revision system stores everything in local time (est),
        but the DSS works in UT, so we must convert.
        However, why complicate setting up the unit tests?
        """
        if test:
           return self.dt
        else:
           return TimeAgent.est2utc(self.dt)

    def __str__(self):
        return  "(%s) field %s: %s -> %s" % (self.dt.strftime(self.dtFormat)
                                           , self.field
                                           , self.value1
                                           , self.value2
                                            )
        
