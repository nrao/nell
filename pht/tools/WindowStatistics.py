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

from scheduler.models import *

class WindowStatistics(object):

    """
    Simple class for reporting on how windows have been scheduled
    in the past.  This helps figure out how to prepare for the 
    next semester.
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

    def report(self):

        all = Window.objects.all()

        ws = Window.objects.filter(complete = True)
        
        shortWs = [w for w in ws if w.duration() <= self.limit]
        longWs = [w for w in ws if w.duration() > self.limit]
        
        print "%d complete of %d Windows." % (len(ws), len(all))
        print "Short Windows are <= %d days long; Long are > %d days" % \
            (self.limit, self.limit)
        
        defaultShort = self.countDefaults(shortWs)
        defaultShortPrt = 100. * (float(defaultShort)/len(shortWs))
        defaultLong = self.countDefaults(longWs)
        defaultLongPrt = 100. * (float(defaultLong)/len(longWs))
        
        print "Defaults scheduled for %d of %d short windows (%f%%)." % \
            (defaultShort, len(shortWs), defaultShortPrt)    
        print "Defaults scheduled for %d of %d long windows (%f%%)" % \
            (defaultLong, len(longWs), defaultLongPrt) 
