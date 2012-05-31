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

from datetime import datetime

from utilities.TimeAgent import *
from pht.utilities       import *
#from pht.models          import *
from PhtHttpAdapter      import PhtHttpAdapter


class DssPeriodHttpAdapter(PhtHttpAdapter):

    """
    We only are reading the DSS periods in the PHT, so we must only
    support the jsondict method here.
    Also, we only need to know a little about these DSS periods,
    that's why we aren't getting the huge JSON from the DSS's
    http adapter.
    """

    def __init__(self, period):
        self.period = period

    def load(self, period):
        self.period = period

    def jsondict(self, tz):
        start = self.period.start if tz == 'UTC' else TimeAgent.utc2est(self.period.start)
        end   = self.period.end() if tz == 'UTC' else TimeAgent.utc2est(self.period.end())
        w = self.period.window

        sessionJson = {'science' : self.period.session.observing_type.type 
                     , 'receiver' : self.period.session.get_receiver_req() 
                     , 'type' : self.period.session.session_type.type
                      }

        js =   {"id"           : self.period.id
              , 'session'      : sessionJson
              , "handle"       : self.period.toHandle()
              , "date"         : d2str(start)
              , "time"         : t2str(start)
              , "duration"     : self.period.duration
              , "wdefault"     : self.period.is_windowed_default() \
                                     if w is not None else None
              , "wstart"       : d2str(w.start_date()) if w is not None else None
              , "wend"         : d2str(w.last_date()) if w is not None else None
                }

        return js                

