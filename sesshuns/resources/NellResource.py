from django_restapi.resource  import Resource
from django.http              import HttpResponse, HttpResponseRedirect

from sesshuns.models          import first

import simplejson as json

class NellResource(Resource):
    def __init__(self, dbobject, *args, **kws):
        self.dbobject = dbobject
        super(NellResource, self).__init__(*args, **kws)

    def create(self, request, *args, **kws):
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args, **kws)
        elif method == "delete":
            return self.delete(request, *args, **kws)
        else:
            return self.create_worker(request, *args, **kws)

    def create_worker(self, request, *args, **kws):
        o = self.dbobject()
        o.init_from_post(request.POST)
        # Query the database to insure data is in the correct data type
        o = first(self.dbobject.objects.filter(id = o.id))
        
        return HttpResponse(json.dumps(o.jsondict())
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        id    = int(args[0])
        o     = self.dbobject.objects.get(id = id)
        o.update_from_post(request.POST)

        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[0])
        o  = self.dbobject.objects.get(id = id)
        o.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))

