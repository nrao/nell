from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect, Http404

from NellResource import NellResource
from sesshuns.models       import Investigator, first

import simplejson as json

class InvestigatorResource(NellResource):
    def __init__(self, *args, **kws):
        super(InvestigatorResource, self).__init__(Investigator, *args, **kws)

    def create(self, request, *args, **kws):
        return super(InvestigatorResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        try:
            p_id, = args
        except:
            raise Http404

        sortField = request.GET.get("sortField", "id")
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
        return HttpResponse(json.dumps(dict(total = total
                                          , investigators = [i.jsondict() for i in investigators]))
                          , content_type = "application/json")
