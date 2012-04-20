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

from django.http import HttpResponse
import simplejson as json
from datetime import datetime

from Resource               import Resource
from scheduler.httpadapters import PeriodHttpAdapter
from scheduler.models       import Period
from nell.utilities         import TimeAgent

class DssPeriodResource(Resource):

    def __init__(self):
        self.root    = 'periods'
        self.adapter = PeriodHttpAdapter(None)

    def create(self, request, *args, **kws):
        tz, = args
        p   = Period()
        self.adapter.load(p)
        self.adapter.init_from_post(json.loads(request.raw_post_data), tz)
        # Query the database to insure data is in the correct data type
        p = Period.objects.get(id = p.id)
        self.adapter.load(p)
    
        #revision.comment = self.get_rev_comment(request, p, "create_worker")
        return HttpResponse(json.dumps(self.adapter.jsondict(tz))
                          , mimetype = "text/plain")

    def read(self, request, *args, **kws):
        if len(args) == 1:
            tz,          = args
            startPeriods = request.GET.get("startPeriods", datetime.now().strftime("%Y-%m-%d"))
            daysPeriods  = request.GET.get("daysPeriods",  '14')

            dt           = TimeAgent.str2dt(startPeriods)
            start        = dt if tz == 'UTC' else TimeAgent.est2utc(dt)
            duration     = int(daysPeriods) * 24 * 60
            periods      = Period.get_periods(start, duration)
            return HttpResponse(
                json.dumps(dict(total   = len(periods)
                              , periods = [PeriodHttpAdapter(p).jsondict(tz) for p in periods]
                              , success = 'ok'))
              , content_type = "application/json")
        else:
            tz, id = args
            p      = Period.objects.get(id = id)
            return HttpResponse(
                json.dumps(dict(PeriodHttpAdapter(p).jsondict(tz)
                              , success = 'ok'))
              , content_type = "application/json")

    def update(self, request, *args, **kws):
        tz, id,  = args
        adapter  = PeriodHttpAdapter(Period.objects.get(id = id))
        data     = json.loads(request.raw_post_data)
        m, d, y  = data.get('date').split('/')
        data['date'] = '%s-%s-%s' % (y, m, d)
        adapter.update_from_post(data, tz)
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')

    def delete(self, request, *args, **kws):
        tz, id, = args
        period  = Period.objects.get(id = id)
        period.delete()
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')
