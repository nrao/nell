from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from sesshuns.models       import Window, first, str2dt
from datetime              import datetime, timedelta, date

import simplejson as json

jsonMap = { "id" : "id"
          , "handle" : "session__name"
          , "start"  : "start_date"
          , "duration" : "duration"
          , "last" : "start_date"
          , "default_date" : "default_period__start"
          , "default_time" : "default_period__start"
          , "default_duration" : "default_period__duration"
          , "default_state" : "default_period__state"
          , "choosen_date" : "choosen_period__start"
          , "choosen_time" : "choosen_period__start"
          , "choosen_duration" : "choosen_period__duration"
          , "choosen_state" : "choosen_period__state"
          }
    
class WindowResource(NellResource):
    def __init__(self, *args, **kws):
        super(WindowResource, self).__init__(Window, *args, **kws)

    def create(self, request, *args, **kws):
        return super(WindowResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):

        # one or many?
        if len(args) == 0:
            # many, use filters
            sortField = jsonMap.get(request.GET.get("sortField", "handle"), "start_date")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""             
            query_set = Window.objects

            filterSession = request.GET.get("filterSession", None)
            if filterSession is not None:
                query_set = query_set.filter(session__name = filterSession)

            # time range filters come as a pair
            filterByDateRange = False
            filterStart = request.GET.get("filterStartDate", None)
            filterDur   = request.GET.get("filterDuration", None)
            if filterStart is not None and filterDur is not None:
                start = datetime.strptime(filterStart, "%Y-%m-%d").date() 
                days = int(filterDur)
                days = days if days >= 1 else 1
                last_day = (start + timedelta(days = days -1))
                # We really want all the overlapping windows w/ this 
                # time range, not just the ones that start w/ in it.
                # So we only do part of the query here, and finish at (2)
                query_set = query_set.filter(start_date__lte = last_day)
                filterByDateRange = True
            windows = query_set.order_by(order + sortField)
            # We can't get overlaps from a pure database query, so 
            # must finish what we started here (part (2)).
            if filterByDateRange:
                windows = [w for w in windows if w.last_date() >= start]
            total = len(windows)
            offset = int(request.GET.get("offset", 0))
            limit  = int(request.GET.get("limit", 50))
            windows = windows[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                 , windows = [w.jsondict() for w in windows]))
            , content_type = "application/json")
        else:
            # one, identified by id in arg list
            w_id = args[0]
            window = first(Window.objects.filter(id = w_id))
            return HttpResponse(json.dumps(dict(window = window.jsondict()))
                              , content_type = "application/json")


