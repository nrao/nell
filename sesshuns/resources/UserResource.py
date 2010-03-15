from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect
from django_restapi.resource  import Resource
from sesshuns.models       import User, first

import simplejson as json

class MethodException(Exception):

    def __init__(self, method):
        self.method = method

    def __str__(self):
        return "Method '%s' is invalid for UserResource." % self.method

class UserResource(Resource):

    def create(self, request, *args, **kws):
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args, **kws)
        else:
            raise MethodException(method)

    
    def read(self, request, *args, **kws):
        if len(args) == 0:
            # many, filtered by:
            sortField = request.GET.get("sortField", "id")
            sortField = "id" if sortField == "null" else sortField
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            query_set = User.objects
            filterText = request.GET.get("filterText")
            if filterText is not None:
                query_set = query_set.filter(
                     Q(first_name__icontains=filterText) |
                     Q(last_name__icontains=filterText) |
                     Q(username__icontains=filterText) |
                     Q(contact_instructions__icontains=filterText) 
                     )

            users     = query_set.order_by(order + sortField)
            total     = len(users)
            offset    = int(request.GET.get("offset", 0))
            limit     = int(request.GET.get("limit", 50))
            users     = users[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                                              , users = [u.jsondict() for u in users]))
                              , content_type = "application/json")
        else:
            # one, identified by id
            u_id, = args
            user  = first(User.objects.filter(id = u_id))
            return HttpResponse(json.dumps(dict(user = user.jsondict()))
                              , content_type = "application/json")

    def update(self, request, *args, **kws):
        id    = int(args[0])
        u     = User.objects.get(id = id)
        u.update_from_post(request.POST)

        # NOTE: this originally returned "", but if we want JSON callbacks
        # to work from GWT, need A response.  This change seems benign
        #return HttpResponse("")
        return HttpResponse(json.dumps({"success" : "ok"})
                          , mimetype = "text/plain")


