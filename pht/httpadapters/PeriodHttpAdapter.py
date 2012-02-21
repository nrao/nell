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

def formatDate(dt):
    return str(dt.strftime('%m/%d/%Y'))

def cleanPostData(data):
    bad_keys = [k for k, v in data.iteritems() if v == '']
    for bk in bad_keys:
        data.pop(bk)
    return data

class PeriodHttpAdapter(object):

    def __init__(self, period = None):
        self.setPeriod(period)

    def setPeriod(self, period):
        self.period = period

    def jsonDict(self):

        return {'id'         : self.period.id
              , 'session'    : self.period.session.name
              , 'session_id' : self.period.session.id
              , 'start_date' : formatExtDate(self.period.start)
              , 'start_time' : t2str(self.period.start)
              , 'duration'   : self.period.duration
                }

    def initFromPost(self, data):
        self.period = Period()
        self.updateFromPost(cleanPostData(data))
        self.period.save()

    def updateFromPost(self, data):

        # we can change who this period belongs to
        name = data.get('session')
        # TBF: until we enforce session name uniqueness, we can't do this
        #session = Session.objects.get(name = name)
        session = Session.objects.filter(name = name).order_by('id')[0]
        self.period.session = session
        
        # the start datetime comes in two pieces
        date = data.get("start_date", "")
        time = data.get("start_time", "")
        date = date if date != "" else None
        time = time if time != "" else None
        if date is not None and time is not None:
            start = extDatetime2Datetime(date, time)
            self.period.start = start

        self.period.duration = self.getFloat(data, 'duration')

        self.period.save()



    # TBF: refactor this to a base class or utility
    def getType(self, data, key, fnc, default):
        "Entries for floats & ints can often be blank strings"
        value = None
        value = data.get(key, None)
        if value is None or value == '':
            return default
        else:
            try:
                value = fnc(value)
            except:
                value = default
            finally:
                return value

    def getInt(self, data, key, default = None):
        "Entries for integers can often be blank strings"
        return self.getType(data, key, int, default )

    def getFloat(self, data, key, default = None):
        "Entries for floats can often be blank strings"
        return self.getType(data, key, float, default )



