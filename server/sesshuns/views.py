from django.http              import HttpResponse
from django_restapi.resource  import Resource
from server.sesshuns.models   import *

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

    def read(self, request, *args, **kws):
        if len(args) == 0:
            total     = Sesshun.objects.count()
            sortField = jsonMap.get(request.GET.get("sortField", "id"), "id")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            sessions  = Sesshun.objects.order_by(order + sortField)
            start = int(request.GET.get("start", 0))
            limit = int(request.GET.get("limit", 50))
            sessions = sessions[start:start+limit]
            return HttpResponse(json.dumps(dict(total = total
                                              , sessions = [s.jsondict() for s in sessions]))
                              , content_type = "application/json")
        else:
            s_id  = args[0]
            s     = first(Sesshun.objects.filter(id = s_id))
            return HttpResponse(json.dumps(dict(session = s.jsondict())))

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

class CadenceResource(NellResource):

    def create(self, request, *args, **kws):
        return super(CadenceResource, self).create(request, *args, **kws)
    
    def create_worker(self, request, *args, **kws):
        s_id = args[0]
        s = first(Sesshun.objects.filter(id = s_id))
        c = s.get_cadence()
        c.init_from_post(s_id, request.POST)
        c.gen_windows()
        
        # Query the database to insure data is in the correct data type
        c = first(Cadence.objects.filter(id = c.id))
        return HttpResponse(json.dumps(c.jsondict())
                          , mimetype = "text/plain")

    def read(self, request, *args, **kws):
        s_id = args[0]
        s = first(Sesshun.objects.filter(id = s_id))
        c = first(s.cadence_set.all())
        jsonDict = c.jsondict() if c else {}
        return HttpResponse(json.dumps(jsonDict)
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        s_id = int(args[0])
        s    = first(Sesshun.objects.filter(id = s_id))
        c    = s.get_cadence()
        c.init_from_post(s_id, request.POST)
        c.gen_windows()

        # Query the database to insure data is in the correct data type
        c = first(Cadence.objects.filter(id = c.id))
        return HttpResponse(json.dumps(c.jsondict())
                          , mimetype = "text/plain")

    def delete(self, request, *args):
        id = int(args[0])
        s  = first(Sesshun.objects.filter(id = id))
        c  = s.get_cadence()
        c.delete()
        
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
        w = first(Window.objects.filter(id = w.id))
        return HttpResponse(json.dumps(w.jsondict())
                          , mimetype = "text/plain")

    def read(self, request, *args, **kws):
        s_id = args[0]
        windows = Window.objects.filter(session = s_id)
        return HttpResponse(json.dumps({"windows":[w.jsondict(generate = True) for w in windows]})
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

def receivers_schedule(request, *args, **kws):
    startdate = request.GET.get("startdate", None)
    if startdate is not None:
        d, t      = startdate.split(' ')
        y, m, d   = map(int, d.split('-'))
        h, mm, ss = map(int, map(float, t.split(':')))
        startdate = datetime(y, m, d, h, mm, ss)
    duration = request.GET.get("duration", None)
    if duration is not None:
        duration = int(duration)
    schedule = Receiver_Schedule.extract_schedule(startdate, duration)
    return HttpResponse(
            json.dumps({"schedule" : Receiver_Schedule.jsondict(schedule)})
          , mimetype = "text/plain")

def get_options(request, *args, **kws):
    projects = Project.objects.order_by('pcode')
    return HttpResponse(json.dumps({'project codes' : [ p.pcode for p in projects]})
                      , mimetype = "text/plain")

def get_selected(request):
    selected = Sesshun.objects.filter(selected = True)
    response = json.dumps(dict(sessions = [{'id': s.id, 'name': s.name} for s in selected]))
    return HttpResponse(response, content_type = "text/plain")
