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

from datetime               import datetime
from PeriodHttpAdapter      import PeriodHttpAdapter
from WindowRangeHttpAdapter import WindowRangeHttpAdapter
from SessionHttpAdapter     import SessionHttpAdapter
from scheduler.models        import Period, Sesshun, Period_State

class WindowHttpAdapter (object):

    def __init__(self, window):
        self.window = window

    def load(self, window):
        self.window = window

    def jsondict(self):
        if len(self.window.ranges()) == 0:
            start = last_date = duration = None
        else:    
            start = self.window.start_date().strftime("%Y-%m-%d")
            last_date = self.window.last_date().strftime("%Y-%m-%d")
            duration = self.window.duration()
        
        sponsor = ''
        if self.window.session.project.is_sponsored():
            sponsor = self.window.session.project.sponsor.abbreviation

        js = {  "id"             : self.window.id
              , "handle"         : self.window.toHandle()
              , "sponsor"        : sponsor
              , "start"          : start
              , "end"            : last_date
              , "duration"       : duration
              , "total_time"     : self.window.total_time
              , "time_billed"    : self.window.timeBilled()
              , "time_remaining" : self.window.timeRemaining()
              , "complete"       : self.window.complete
              , "contigious"     : self.window.isContigious()
              , "num_periods"    : self.window.periods.count()
              , "periods"        : [PeriodHttpAdapter(p).jsondict('UTC') for p in self.window.periods.all()]
              , "ranges"         : [WindowRangeHttpAdapter(wr).jsondict() for wr in self.window.ranges()]
              , "errors"         : self.window.errors()
              }
        return js    

    def init_from_post(self, fdata):
        self.from_post(fdata)

    def update_from_post(self, fdata):
        self.from_post(fdata)

    def from_post(self, fdata):

        # most likely, we'll be specifying sessions for windows in the same
        # manner as we do for periods
        handle = fdata.get("handle", "")
        if handle:
            self.window.session = Sesshun.handle2session(handle)
        else:
            try:
                maintenance = Project.objects.get(pcode='Maintenance')
                self.window.session = Sesshun.objects.get(project=maintenance)
            except:
                self.window.session  = Sesshun.objects.get(id=fdata.get("session", 1))

        self.window.total_time = float(fdata.get("total_time", "0.0"))
        complete = fdata.get("complete", "false")
        self.window.setComplete(complete == "true" or complete == True)

        self.window.save()
