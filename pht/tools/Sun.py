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

from utilities.TimeAgent import GBT_LOCATION

from datetime import date, datetime, timedelta
import ephem

class Sun(object):

    def __init__(self):

        self.lat = GBT_LOCATION[1]
        self.long = GBT_LOCATION[0]
        self.sun = ephem.Sun()
        self.gbt = ephem.Observer()
        self.gbt.lat = self.lat
        self.gbt.long = self.long

        self.ephemDateFrmt = '%Y/%m/%d'
        self.datetimeFrmt = '%Y/%m/%d %H:%M:%S' # '2007/10/1 05:59:29'

    def getSunRise(self, date):
        "Returns datetime for sun rise for given date."

        # convert back and forth between our given datetime object
        # and ephem's date string format
        self.gbt.date = date.strftime(self.ephemDateFrmt)
        rise = self.gbt.next_rising(self.sun)
        return datetime.strptime(rise.__str__(), self.datetimeFrmt)

    def getSunSet(self, date):
        """
        ephem returns setting time for the given date ON THE SAME
        DATE if setting for our location happens after midnight
        UT.  This make our life hard, so push it ahead a day if this
        is the case.
        """

        # convert back and forth between our given datetime object
        # and ephem's date string format
        self.gbt.date = date.strftime(self.ephemDateFrmt)
        rise = self.gbt.next_rising(self.sun)
        riseDt = datetime.strptime(rise.__str__(), self.datetimeFrmt)
        set = self.gbt.next_setting(self.sun)
        setDt = datetime.strptime(set.__str__(), self.datetimeFrmt)
        # set after midnight UT?
        if setDt < riseDt:
            setDt = setDt + timedelta(days = 1)
        return setDt

    def getRiseSet(self, date):
        "Returns datetime for sun rise & set for given date."

        # convert back and forth between our given datetime object
        # and ephem's date string format
        self.gbt.date = date.strftime(self.ephemDateFrmt)
        rise = self.gbt.next_rising(self.sun)
        riseDt = datetime.strptime(rise.__str__(), self.datetimeFrmt)
        set = self.gbt.next_setting(self.sun)
        setDt = datetime.strptime(set.__str__(), self.datetimeFrmt)
        # set after midnight UT?
        if setDt < riseDt:
            setDt = setDt + timedelta(days = 1)
        return (riseDt, setDt)    

    def getPTCSRiseSet(self, date):
        "PTCS defines night time using a buffer with sun rise/set"
        
        rise, set = self.getRiseSet(date)
        # 0 hrs at sun rise, 3 hrs after sunset
        return (rise, set + timedelta(hours = 3))


