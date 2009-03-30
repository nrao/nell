from django.http                   import HttpResponse
from django_restapi.resource       import Resource
from nell_server.sessions.models   import Project, Sessions

import simplejson as json

class SessionResource(Resource):
    def create(self, request, *args, **kws):
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args)
        elif method == "delete":
            return self.delete(request, *args)

        s = Sessions()
        s.init_from_json(request.POST)
        
        return HttpResponse(json.dumps(s.jsondict())
                          , mimetype = "text/plain")

    def read(self, request):
        sessions = Sessions.objects.all()
        return HttpResponse(json.dumps({"sessions":[s.jsondict() for s in sessions]})
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        id    = int(args[0])
        s     = Sessions.objects.get(id = id)
        s.update_from_json(request.POST)

        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[0])
        s  = Sessions.objects.get(id = id)
        print s
        #for f in s.fields_set.all():
        #    f.delete()
        #s.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))
