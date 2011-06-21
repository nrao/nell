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
from scheduler.models        import Window, Period, Sesshun, Period_State

class WindowRangeHttpAdapter (object):

    def __init__(self, windowRange):
        self.windowRange = windowRange

    def load(self, windowRange):
        self.windowRange = windowRange

    def jsondict(self):
        js = {"id"       : self.windowRange.id
            , "start"    : self.windowRange.start_date.strftime("%Y-%m-%d")
            , "end"      : self.windowRange.end().strftime("%Y-%m-%d")
            , "duration" : self.windowRange.duration
             }
        return js                     

    def init_from_post(self, fdata):
        self.from_post(fdata)

    def update_from_post(self, fdata):
        self.from_post(fdata)

    def from_post(self, fdata):
        w_id = fdata.get("window_id", None)
        if w_id is not None:
            window = Window.objects.get(id = int(w_id))
            self.windowRange.window = window
        else:
            # you HAVE to be assigned a window
            if self.windowRange.window_id is None:
                window = Window.objects.all()[0]
                self.windowRange.window = window
                


        date = fdata.get("start", datetime.utcnow().strftime("%Y-%m-%d"))
        self.windowRange.start_date = datetime.strptime(date, "%Y-%m-%d").date()

        self.windowRange.duration = int(float(fdata.get("duration", "1.0")))

        self.windowRange.save()        
