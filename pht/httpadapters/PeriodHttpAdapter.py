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
from pht.models          import *
from PhtHttpAdapter      import PhtHttpAdapter


#from pht.httpadapters import SessionHttpAdapter
from SessionHttpAdapter import SessionHttpAdapter

class PeriodHttpAdapter(PhtHttpAdapter):

    def __init__(self, period = None):
        self.setPeriod(period)

    def setPeriod(self, period):
        self.period = period

    def jsonDict(self):

        observingType = self.period.session.observing_type.type \
            if self.period.session.observing_type is not None else None
        sessType = self.period.session.session_type.type \
            if self.period.session.session_type is not None else None
        sessionJson = {'receivers' : self.period.session.get_receivers() 
                     , 'observing_type' : observingType
                     , 'type' : sessType}
        handle = "%s (%s)" % (self.period.session.name
                            , self.period.session.proposal.pcode)
        sessTypeCode = self.period.session.session_type.abbreviation if self.period.session.session_type is not None else None
        return {'id'         : self.period.id
              , 'session'    : self.period.session.name
              , 'session_json' : sessionJson # TBF: align this with DSS Periods
              , 'session_id' : self.period.session.id
              , 'pcode'      : self.period.session.proposal.pcode
              , 'handle'     : handle
              , 'date' : formatExtDate(self.period.start)
              , 'time' : t2str(self.period.start)
              , 'duration'   : self.period.duration
              , 'window_size'             : self.period.session.monitoring.window_size
              , 'session_type_code'       : sessTypeCode
                }

    def initFromPost(self, data):
        self.period = Period()
        self.updateFromPost(self.cleanPostData(data))
        self.period.save()
        self.notify(self.period.session.proposal)

    def updateFromPost(self, data):

        # we can change who this period belongs to: sessions
        # are uniquely identified by their 'name (project)' handle
        handle = data.get('handle')
        demarker = handle.rfind('(')
        name = handle[0:(demarker-1)]
        pcode = handle[(demarker+1):-1]
        session = Session.objects.filter(name = name, proposal__pcode = pcode)[0]
        self.period.session = session
        
        # the start datetime comes in two pieces
        date = data.get("date", "")
        time = data.get("time", "")
        date = date if date != "" else None
        time = time if time != "" else None
        if date is not None and time is not None:
            start = extDatetime2Datetime(date, time)
            self.period.start = start

        self.period.duration = self.getFloat(data, 'duration')

        self.period.save()

        self.notify(self.period.session.proposal)
