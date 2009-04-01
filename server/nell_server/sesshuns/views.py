from django.http                   import HttpResponse
from django_restapi.resource       import Resource
from nell_server.sesshuns.models   import first, Project, Sesshun

import simplejson as json

class NellResource(Resource):

    def create(self, request, *args, **kws):
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args, **kws)
        elif method == "delete":
            return self.delete(request, *args, **kws)
        else:
            return self.create_worker(request, *args, **kws)

class SessionResource(NellResource):
    
    def create(self, request, *args, **kws):
        return super(SessionResource, self).create(request, *args, **kws)
    
    def create_worker(self, request, *args, **kws):
        s = Sesshun()
        s.init_from_json(request.POST)
        # Query the database to insure data is in the correct data type
        s = first(Sesshun.objects.filter(id = s.id))
        
        return HttpResponse(json.dumps(s.jsondict())
                          , mimetype = "text/plain")

    def read(self, request):
        sessions = Sesshun.objects.all()
        return HttpResponse(json.dumps({"sessions":[s.jsondict() for s in sessions]})
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        id    = int(args[0])
        s     = Sesshun.objects.get(id = id)
        s.update_from_json(request.POST)

        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[0])
        s  = Sesshun.objects.get(id = id)
        s.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))

