from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from scheduler.models       import WindowRange
from scheduler.httpadapters import WindowRangeHttpAdapter
from datetime              import datetime, timedelta, date

import simplejson as json

jsonMap = { "id" : "id"
          , "start"  : "start_date"
          , "duration" : "duration"
          }

class WindowRangeResource(NellResource):
    def __init__(self, *args, **kws):
        super(WindowRangeResource, self).__init__(WindowRange, WindowRangeHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(WindowRangeResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):

        # one or many?
        if len(args) == 0:
            # many, use filters
            sortField = jsonMap.get(request.GET.get("sortField", "start_date"), "start_date")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""             
            query_set = WindowRange.objects


            # filter by window id?
            filterWindowId = request.GET.get("filterWindowId", None)
            if filterWindowId is not None:
                query_set = query_set.filter(window__id = filterWindowId)

            winRanges = query_set.order_by(order + sortField)

            total = len(winRanges)
            offset = int(request.GET.get("offset", 0))
            limit  = int(request.GET.get("limit", -1))
            if limit != -1:
                winRanges = winRanges[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                 , windowRanges = [WindowRangeHttpAdapter(w).jsondict() for w in winRanges]))
            , content_type = "application/json")
        else:
            # one, identified by id in arg list
            wr_id = args[0]
            winRange = WindowRange.objects.get(id = wr_id)
            return HttpResponse(json.dumps(dict(windowRange = WindowRangeHttpAdapter(winRange).jsondict()))
                              , content_type = "application/json")        
