from django.http              import HttpResponse
from django_restapi.resource  import Resource
from server.sesshuns.models   import first, Project, Receiver, Sesshun, Window

from datetime import datetime
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
        s.init_from_post(request.POST)
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
        s.update_from_post(request.POST)

        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[0])
        s  = Sesshun.objects.get(id = id)
        s.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))

class WindowResource(NellResource):

    def create(self, request, *args, **kws):
        return super(WindowResource, self).create(request, *args, **kws)
    
    def create_worker(self, request, *args, **kws):
        s_id = int(request.POST["session_id"])
        s = first(Sesshun.objects.filter(id = s_id))
        w = Window(session = s)
        w.save()
        w.init_from_post(request.POST)
        
        # Query the database to insure data is in the correct data type
        w = first(Window.objects.filter(id = s.id))
        return HttpResponse(json.dumps(w.jsondict())
                          , mimetype = "text/plain")

    def read(self, request):
        windows = Window.objects.all()
        return HttpResponse(json.dumps({"windows":[w.jsondict() for w in windows]})
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        id    = int(args[0])
        w     = first(Window.objects.filter(id = id))
        w.update_from_post(request.POST)

        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[0])
        w  = first(Window.objects.filter(id = id))
        w.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))

def gen_opportunities(request, *args, **kws):
    now = request.GET.get("now", None)
    if now is not None:
        d, t      = now.split(' ')
        y, m, d   = map(int, d.split('-'))
        h, mm, ss = map(int, map(float, t.split(':')))
        now = datetime(y, m, d, h, mm, ss)
    if len(args) == 0:
        windows = Window.objects.all()
        return HttpResponse(json.dumps(
                {"windows":[w.jsondict(generate = True, now = now) for w in windows]})
                          , mimetype = "text/plain")
    else:
        id    = int(args[0])
        w     = first(Window.objects.filter(id = id))
        return HttpResponse(json.dumps(w.jsondict(generate = True, now = now))
                          , mimetype = "text/plain")

def get_options(request, *args, **kws):
    projects = Project.objects.order_by('pcode')
    return HttpResponse(json.dumps({'project codes' : [ p.pcode for p in projects]})
                      , mimetype = "text/plain")
