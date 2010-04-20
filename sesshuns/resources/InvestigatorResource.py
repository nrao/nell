from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect, Http404

from NellResource          import NellResource
from sesshuns.models       import Investigator, first
from sesshuns.httpadapters import InvestigatorHttpAdapter

import simplejson as json

class InvestigatorResource(NellResource):
    def __init__(self, *args, **kws):
        super(InvestigatorResource, self).__init__(Investigator, InvestigatorHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(InvestigatorResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        try:
            # using brakets because we want a key error if its not there
            p_id = request.GET["project_id"]
        except:
            return HttpResponse(json.dumps(dict(total = 0
                                              , investigators = []))
                          , content_type = "application/json")

        sortField = request.GET.get("sortField", "id")
        sortField = "id" if sortField == "null" else sortField
        order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
        query_set = Investigator.objects.filter(project__id = p_id)
        if sortField == "pi":
            sortField = "investigator__user__last_name"
            query_set = query_set.filter(Q(investigator__principal_investigator = True))
    
        filterText = request.GET.get("filterText", None)
        if filterText is not None:
            query_set = query_set.filter(
                    Q(user__last_name__icontains=filterText) |
                    Q(user__first_name__icontains=filterText) 
                    )
        investigators = query_set.order_by(order + sortField)
        total         = len(investigators)
        offset        = int(request.GET.get("offset", 0))
        limit         = int(request.GET.get("limit", 50))
        investigators = investigators[offset:offset+limit]
        return HttpResponse(json.dumps(
              dict(total = total
                , investigators = [InvestigatorHttpAdapter(i).jsondict() for i in investigators]))
            , content_type = "application/json")
