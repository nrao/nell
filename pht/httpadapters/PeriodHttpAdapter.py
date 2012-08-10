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
import settings, pg, psycopg2

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
        
    @staticmethod
    def jsonDictHP(curr, keys, values):
        data = dict(zip(keys, values))

        # split up the start datetime into a date and time
        dt = data['start_datetime']
        data['date'] = formatExtDate(dt)
        data['time'] = t2str(dt)

        # original start datetime is not in JSON format, so either
        # get rid of it or format it
        data['start_datetime'] = formatExtDate(dt)

        # construct the handle
        data['handle'] = "%s (%s)" % (data['session'], data['pcode'])

        # get the period's session's receivers, 
        query = """
          SELECT
            r.abbreviation
          FROM
            pht_sessions as s
            left outer join pht_sessions_receivers as rs on rs.session_id = s.id
            left outer join pht_receivers as r on r.id = rs.receiver_id 
          WHERE
            s.id = %s
        """ % data['session_id']
        curr.execute(query)
        rx = ",".join([r[0] for r in curr.fetchall()])

        # and construct the session's json
        sessionJson = {'type' : data['session_type'] 
                     , 'observing_type' : data['observing_type'] 
                     , 'receivers' : rx
                      }
        data['session_json'] = sessionJson

        return data

    @staticmethod
    def jsonDictAllHP():
        conn = psycopg2.connect(host   = settings.DATABASES['default']['HOST']
                              , user   = settings.DATABASES['default']['USER']
                              , password = settings.DATABASES['default']['PASSWORD']
                              , database = settings.DATABASES['default']['NAME']
                            )
        curr = conn.cursor()
        query = """
        SELECT 
          p.id,
          s.name as session,
          s.id as session_id,
          s.dss_session_id,
          pr.pcode,
          p.start as start_datetime,
          p.duration,
          st.abbreviation as session_type_code,
          st.type as session_type,
          ob.type as observing_type,
          m.window_size
        FROM (((((
          pht_periods as p
          left outer join pht_sessions as s on s.id = p.session_id)
          left outer join pht_proposals as pr on pr.id = s.proposal_id)
          left outer join pht_session_types as st on st.id = s.session_type_id)
          left outer join observing_types as ob on ob.id = s.observing_type_id)
          left outer join pht_monitoring as m on m.id = s.monitoring_id)

        ORDER BY p.start 
        """
        curr.execute(query)
        keys = [d.name for d in curr.description]
        return [PeriodHttpAdapter.jsonDictHP(curr, keys, values) for values in curr.fetchall()]
        
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
