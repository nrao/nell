from django.http              import HttpResponse
from django_restapi.resource  import Resource
from django.db.models         import Q
from models                   import *
from datetime import datetime
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

class ProjectResource(NellResource):
    def __init__(self, *args, **kws):
        super(ProjectResource, self).__init__(Project, *args, **kws)

    def create(self, request, *args, **kws):
        return super(ProjectResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        sortField = request.GET.get("sortField", "id")
        sortField = "id" if sortField == "null" else sortField
        order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""

        projects = Project.objects.order_by(order + sortField)
        total    = len(projects)
        offset   = int(request.GET.get("offset", 0))
        limit    = int(request.GET.get("limit", 50))
        projects = projects[offset:offset+limit]
        return HttpResponse(json.dumps(dict(total = total
                                          , projects = [p.jsondict() for p in projects]))
                          , content_type = "application/json")

class SessionResource(NellResource):
    def __init__(self, *args, **kws):
        super(SessionResource, self).__init__(Sesshun, *args, **kws)
 
    def create(self, request, *args, **kws):
        return super(SessionResource, self).create(request, *args, **kws)

    def read(self, request, *args, **kws):
        if len(args) == 0:
            sortField = jsonMap.get(request.GET.get("sortField", "id"), "id")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""

            filterText = request.GET.get("filterText", None)
            if filterText is None:
                sessions = Sesshun.objects.order_by(order + sortField)
            else:
                sessions = Sesshun.objects.filter(Q(name__contains=filterText) |\
                    Q(project__pcode__contains=filterText) |\
                    Q(project__semester__semester__contains=filterText) |
                    Q(session_type__type__contains=filterText) |
                    Q(observing_type__type__contains=filterText)).\
                    order_by(order + sortField)
            total  = len(sessions)
            offset = int(request.GET.get("offset", 0))
            limit  = int(request.GET.get("limit", 50))
            sessions = sessions[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                                              , sessions = [s.jsondict() for s in sessions]))
                              , content_type = "application/json")
        else:
            s_id  = args[0]
            s     = first(Sesshun.objects.filter(id = s_id))
            return HttpResponse(json.dumps(dict(session = s.jsondict())))

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
