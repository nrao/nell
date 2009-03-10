from django.http                   import HttpResponse
from django_restapi.resource       import Resource
from nell_server.sessions.models   import Sessions, Fields

import simplejson as json

class SessionResource(Resource):

    def create(self, request, *args, **kws):
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args)
        elif method == "delete":
            return self.delete(request, *args)

        fData = request.POST
        s     = Sessions()
        s.save()
        for (k, v) in fData.items():
            if k != "_method":
                f = Fields(session = s, key = k, value = v)
                f.save()
        
        return HttpResponse(json.dumps(self.build_dict(s)))

    def read(self, request):
        sessions = Sessions.objects.all()
        return HttpResponse(json.dumps({"sessions":[self.build_dict(s) for s in sessions]})
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        id    = int(args[0])
        fData = request.POST
        s     = Sessions.objects.get(id = id)
        for k, v in fData.items():
            if k != "_method":
                result_set = Fields.objects.filter(session = s, key = k)
                if len(result_set) == 0:
                    f = Fields(session = s, key = k, value = v)
                    f.save()
                else:
                    f       = result_set[0]
                    f.value = v
                    f.save()
        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[0])
        s  = Sessions.objects.get(id = id)
        for f in s.fields_set.all():
            f.delete()
        s.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))

    def build_dict(self, s):
        d = {"id":s.id}
        for f in s.fields_set.all():
            if f.key != "id":
                d[f.key] = f.value
        return d


class PerspectiveResource(Resource):

    def create(self, request, *args, **kws):
        # TBF:  duplicate code
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args)
        elif method == "delete":
            return self.delete(request, *args)

        print "create: ", request.POST
        return HttpResponse("")

    def read(self, request):
        return HttpResponse("")

    def update(self, request, *args, **kws):
        print "update: ", request.POST
        return HttpResponse("")

    def delete(self, request, *args):
        return HttpResponse("")
