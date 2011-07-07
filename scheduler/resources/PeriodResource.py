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

from datetime                 import datetime, timedelta
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import get_object_or_404

from NellResource    import NellResource
from scheduler.models import Period
from scheduler.utilities    import jsonMap
from scheduler.httpadapters import PeriodHttpAdapter
from nell.utilities        import TimeAgent

import simplejson as json
import reversion
from reversion import revision

import sys
import traceback

def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
        excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)


class PeriodResource(NellResource):
    def __init__(self, *args, **kws):
        super(PeriodResource, self).__init__(Period, PeriodHttpAdapter, *args, **kws)

    def read(self, request, *args, **kws):

        tz = args[0]
        # one or many?
        if len(args) == 1:
            # we are getting periods from within a range of dates
            sortField    = jsonMap.get(request.GET.get("sortField", "start"), "start")
            order        = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""

            # Either filter by date, or by something else.
            filterWnd = request.GET.get("filterWnd", None)

            # make sure we have defaults for dates
            defStart = datetime.now().strftime("%Y-%m-%d") if filterWnd is None else None
            defDays = "1" if filterWnd is None else None

            # Filtering by date involves a pair of keywords
            filterWnd = request.GET.get("filterWnd", None)
            filterElc = request.GET.get("filterElc", None)

            # make sure we have defaults for dates
            defStart = datetime.now().strftime("%Y-%m-%d") \
                if filterWnd is None and filterElc is None else None
            defDays = "1" if filterWnd is None and filterElc is None else None
            
            startPeriods = request.GET.get("startPeriods", defStart)
            daysPeriods  = request.GET.get("daysPeriods",  defDays)

            if startPeriods is not None and daysPeriods is not None:
                if startPeriods is None:
                    startPeriods = datetime.now().strftime("%Y-%m-%d")
                if daysPeriods is None:
                    daysPeriods = "1"        
                dt           = TimeAgent.str2dt(startPeriods)
                start        = dt if tz == 'UTC' else TimeAgent.est2utc(dt)
                duration     = int(daysPeriods) * 24 * 60
                periods      = Period.get_periods(start, duration)
            else:
                # filter by something else
                query_set = Period.objects

                # window id
                #filterWnd = request.GET.get("filterWnd", None)
                if filterWnd is not None:
                    wId = int(filterWnd)
                    query_set = query_set.filter(window__id = wId)

                # elective id
                #filterElc = request.GET.get("filterElc", None)
                if filterElc is not None:
                    eId = int(filterElc)
                    query_set = query_set.filter(elective__id = eId)

                periods = query_set.order_by(order + sortField)    


            return HttpResponse(
                json.dumps(dict(total   = len(periods)
                              , periods = [PeriodHttpAdapter(p).jsondict(tz) for p in periods]
                              , success = 'ok'))
              , content_type = "application/json")
        else:
            # we're getting a single period as specified by ID
            p_id    = int(args[1])
            #p       = Period.objects.get(id = p_id)
            p       = get_object_or_404(Period, id = p_id)
            adapter = PeriodHttpAdapter(p)
            return HttpResponse(
                json.dumps(dict(period  = adapter.jsondict(tz)
                              , success = 'ok'))
              , content_type = "application/json")

    @revision.create_on_success
    def create_worker(self, request, *args, **kws):
        o = self.dbobject()
        tz = args[0]
        adapter = PeriodHttpAdapter(o)
        adapter.init_from_post(request.POST, tz)
        # Query the database to insure data is in the correct data type
        o = self.dbobject.objects.get(id = o.id)
        
        revision.comment = self.get_rev_comment(request, o, "create_worker")

        return HttpResponse(json.dumps(adapter.jsondict(tz))
                          , mimetype = "text/plain")

    @revision.create_on_success
    def update(self, request, *args, **kws):
        tz    = args[0]
        id    = int(args[1])
        o     = self.dbobject.objects.get(id = id)
        adapter = PeriodHttpAdapter(o)
        adapter.update_from_post(request.POST, tz)

        revision.comment = self.get_rev_comment(request, o, "update")

        return HttpResponse(json.dumps({"success": "ok"})
                          , mimetype = "text/plain")

    @revision.create_on_success
    def delete(self, request, *args):
        id = int(args[1])
        o  = self.dbobject.objects.get(id = id)
        revision.comment = self.get_rev_comment(request, o, "delete")        
        o.delete()

        return HttpResponse(json.dumps({"success": "ok"})
                          , mimetype = "text/plain")

