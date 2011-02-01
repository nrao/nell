from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect, Http404

from NellResource          import NellResource
from sesshuns.models       import Friend, first
from sesshuns.httpadapters import FriendHttpAdapter

import simplejson as json

class FriendResource(NellResource):
    def __init__(self, *args, **kws):
        super(FriendResource, self).__init__(Friend, FriendHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(FriendResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        try:
            # using brakets because we want a key error if its not there
            p_id = request.GET["project_id"]
        except:
            return HttpResponse(json.dumps(dict(total = 0
                                              , friends = []))
                          , content_type = "application/json")

        sortField = request.GET.get("sortField", "id")
        sortField = "id" if sortField == "null" else sortField
        order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
        query_set = Friend.objects.filter(project__id = p_id)
    
        filterText = request.GET.get("filterText", None)
        if filterText is not None:
            query_set = query_set.filter(
                    Q(user__last_name__icontains=filterText) |
                    Q(user__first_name__icontains=filterText) 
                    )
        friends = query_set.order_by(order + sortField)
        total         = len(friends)
        offset        = int(request.GET.get("offset", 0))
        limit         = int(request.GET.get("limit", 50))
        friends = friends[offset:offset+limit]
        return HttpResponse(json.dumps(
              dict(total = total
                , friends = [FriendHttpAdapter(f).jsondict() for f in friends]))
            , content_type = "application/json")
