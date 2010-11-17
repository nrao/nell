from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from sesshuns.models       import Elective, first, str2dt
from sesshuns.httpadapters import ElectiveHttpAdapter
from datetime              import datetime, timedelta, date

import simplejson as json

jsonMap = { "id" : "id"
          , "handle" : "session__name"
          , "complete" : "complete"
          }
    
class ElectiveResource(NellResource):
    def __init__(self, *args, **kws):
        super(ElectiveResource, self).__init__(Elective, ElectiveHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(ElectiveResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):

        # one or many?
        if len(args) == 0:
            # many, use filters
            sortField = jsonMap.get(request.GET.get("sortField", "handle"), "id")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""             
            query_set = Elective.objects

            filterSession = request.GET.get("filterSession", None)
            if filterSession is not None:
                query_set = query_set.filter(session__name = filterSession)

            filterSessionId = request.GET.get("filterSessionId", None)
            if filterSessionId is not None:
                query_set = query_set.filter(session__id = filterSessionId)

            elecs = query_set.order_by(order + sortField)

            total = len(elecs)
            offset = int(request.GET.get("offset", 0))
            limit  = int(request.GET.get("limit", -1))
            if limit != -1:
                elecs = elecs[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                 , electives = [ElectiveHttpAdapter(e).jsondict() for e in elecs]))
            , content_type = "application/json")
        else:
            # one, identified by id in arg list
            e_id = args[0]
            elective = first(Elective.objects.filter(id = e_id))
            return HttpResponse(json.dumps(dict(elective = ElectiveHttpAdapter(elective).jsondict()))
                              , content_type = "application/json")


