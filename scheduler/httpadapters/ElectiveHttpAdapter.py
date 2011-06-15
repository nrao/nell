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
from SessionHttpAdapter     import SessionHttpAdapter
from scheduler.models        import Period, Sesshun
from utilities.TimeAgent     import *

class ElectiveHttpAdapter (object):

    def __init__(self, elective):
        self.elective = elective

    def load(self, elective):
        self.elective = elective

    def jsondict(self):
        minMax = self.elective.periodDateRange()
        js = {  "id"             : self.elective.id
              , "handle"         : self.elective.toHandle()
              , "complete"       : self.elective.complete
              , "firstPeriod"    : dt2str(minMax[0])
              , "lastPeriod"     : dt2str(minMax[1])
              # Note: these aren't being currently used by a client
              # but taking them out doesn't speed up current clients
              , "session"        : SessionHttpAdapter(self.elective.session).jsondict()
              , "periods"        : [PeriodHttpAdapter(p).jsondict('UTC', 0.0) for p in self.elective.periods.all()]
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
            self.elective.session = Sesshun.handle2session(handle)
        else:
            try:
                maintenance = Project.objects.get(pcode='Maintenance')
                self.elective.session = Sesshun.objects.get(project=maintenance)
            except:
                self.elective.session  = Sesshun.objects.get(id=fdata.get("session", 1))


        self.elective.setComplete(fdata.get("complete", "false") == "true")

        self.elective.save()                
