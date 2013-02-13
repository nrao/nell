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
from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import *

class WindowStatistics(object):

    """
    Simple class for reporting on how windows have been scheduled
    in the past.  This helps figure out how to prepare for the 
    next semester.

     We would like to update how we are distributing windowed observations and
maintenance days more effectively when making the LST pressures. We just
need a better idea of how to distribute the time amongst the weather categories.
First, what fraction of windows are observing on their default days - say
over the last two years? Is there a difference between June-August compared
to September-May?
Second, what fraction of maintenance days (the elective ones between
September and May) end up on poor weather, good weather and excellent
weather days?
I plan on asking Ron what fraction of the time is poor, good and excellent
weather from the entire history of his weather data so we can update those
ratios also.
    """

    def __init__(self):

        self.limit = 3 # days

    def countDefaults(self, ws):
        default = 0
        for w in ws:
            if w.default_period is not None \
                and w.default_period.state.abbreviation == 'S':
                    
                default += 1
        return default            

    def findDefaultCounts(self, shortWs, longWs):

        defaultShort = defaultLong = 0
        defaultShortPrt = defaultLongPrt = 0.0

        defaultShort = self.countDefaults(shortWs)
        if len(shortWs) > 0:
            defaultShortPrt = 100. * (float(defaultShort)/len(shortWs))

        defaultLong = self.countDefaults(longWs)
        if len(longWs) > 0:
             defaultLongPrt = 100. * (float(defaultLong)/len(longWs))
    
        return (defaultShort
              , defaultShortPrt
              , defaultLong
              , defaultLongPrt
               )
    
    def report(self, since = None):

        if since is not None:
            all = Window.objects.all()
            all = [w for w in all if w.start_datetime() > since]
            ws = [w for w in all if w.complete]
            print "Window Statistics since %s" % since
        else:    
            all = Window.objects.all()
            # get all complete windows
            ws = Window.objects.filter(complete = True)
            print "Window Statistics since the beginning of Time"
        

        shortWs, longWs = self.splitByLimit(ws)
        
        print "%d complete of %d Windows." % (len(ws), len(all))
        print "Short Windows are <= %d days long; Long are > %d days" % \
            (self.limit, self.limit)
        
        defaultShort, defaultShortPrt, defaultLong, defaultLongPrt = self.findDefaultCounts(shortWs, longWs)
        
        print "Defaults scheduled for %d of %d short windows (%f%%)." % \
            (defaultShort, len(shortWs), defaultShortPrt)    
        print "Defaults scheduled for %d of %d long windows (%f%%)" % \
            (defaultLong, len(longWs), defaultLongPrt) 

    def splitByLimit(self, ws):

        shortWs = [w for w in ws if w.duration() <= self.limit]
        longWs = [w for w in ws if w.duration() > self.limit]

        return (shortWs, longWs)

    def reportSeasonal(self):

        # Get the datranges for the seasons in question
        # June - August
        # Sep - May
        seasons = [(6, 9), (9, 6)]
        dts = []
        startYear = 2008
        now = datetime.now()
        lastYear = now.year
        tDay = timedelta(days = 1)
        for y in range(startYear, lastYear+1):
            for startMonth, endMonth in seasons:
                if startMonth > endMonth:
                    endY = y + 1
                else:
                    endY = y
                startY = y
                dtStart = datetime(startY, startMonth, 1)
                dtEnd   = datetime(endY, endMonth, 1) - tDay
                dts.append((dtStart, dtEnd))
        
        # now split up the windows by these ranges
        ws = Window.objects.filter(complete = True)

        frmt = "%Y-%m-%d"
        t = 0
        wids = []
        for dtStart, dtEnd in dts:
            wss = [w for w in ws if w.start_datetime() >= dtStart and w.start_datetime() < dtEnd]
            print "%s to %s: %d complete windows" % \
                (dtStart.strftime(frmt)
               , dtEnd.strftime(frmt)
               , len(wss)
                )
            t += len(wss)  

            # look for problems
            for w in wss:
                if w.id in wids:
                    print "seen this one already: ", w, w.id, w.start_datetime()
            wids.extend([w.id for w in wss])
            
            # calculate the default stats
            shortWs, longWs = self.splitByLimit(wss)
            defaultShort, defaultShortPrt, defaultLong, defaultLongPrt = self.findDefaultCounts(shortWs, longWs)
            print "    Defaults scheduled for %d of %d short windows (%f%%)." % \
            (defaultShort, len(shortWs), defaultShortPrt)    
            print "    Defaults scheduled for %d of %d long windows (%f%%)" % \
            (defaultLong, len(longWs), defaultLongPrt) 


if __name__ == '__main__':

    from datetime import datetime, timedelta            

    ws = WindowStatistics()
    ws.report()

    since = datetime.now() - timedelta(days = 365*2)

    print ""
    ws.report(since = since)

    print ""
    ws.reportSeasonal()
