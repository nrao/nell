from django.template          import Context, loader
from django.http              import HttpResponse, HttpResponseRedirect
from django_restapi.resource  import Resource
from django.db.models         import Q
from django.shortcuts         import render_to_response
from django.forms             import ModelForm, TimeField
from models                   import *
from utilities                import TimeAgent
from settings                 import PROXY_PORT

from datetime import date, datetime, timedelta
import simplejson as json

ROOT_URL = "http://trent.gb.nrao.edu:%d" % PROXY_PORT

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

class PeriodResource(NellResource):
    def __init__(self, *args, **kws):
        super(PeriodResource, self).__init__(Period, *args, **kws)

    def read(self, request, *args, **kws):
        # one or many?
        if not args:
            # we are getting periods from within a range of dates
            sortField = jsonMap.get(request.GET.get("sortField", "start"), "start")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            startPeriods = request.GET.get("startPeriods"
                                         , datetime.now().strftime("%Y-%m-%d"))
            daysPeriods  = request.GET.get("daysPeriods", "1")
            start = str2dt(startPeriods)
            days = int(daysPeriods)
            end = start + timedelta(days = days)
            periods = Period.objects.filter(
                                start__gte=start
                              , start__lte=end).order_by(order + sortField)
            return HttpResponse(
                        json.dumps(dict(total = len(periods)
                                      , periods = [p.jsondict() for p in periods]))
                      , content_type = "application/json")
        else:
            # we're getting a single period as specified by ID
            p_id  = args[0]
            p     = first(Period.objects.filter(id = p_id))
            return HttpResponse(json.dumps(dict(period = p.jsondict())))

class ProjectResource(NellResource):
    def __init__(self, *args, **kws):
        super(ProjectResource, self).__init__(Project, *args, **kws)

    def create(self, request, *args, **kws):
        return super(ProjectResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        sortField = request.GET.get("sortField", "id")
        sortField = "pcode" if sortField == "null" or \
                               sortField == "pi" or \
                               sortField == "co_i" \
                            else sortField
        order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
        query_set = Project.objects

        filterClp = request.GET.get("filterClp", None)
        if filterClp is not None:
            query_set = query_set.filter(
                complete = (filterClp.lower() == "true"))

        filterType = request.GET.get("filterType", None)
        if filterType is not None:
            query_set = query_set.filter(project_type__type = filterType.lower())

        filterSem = request.GET.get("filterSem", None)
        if filterSem is not None:
            query_set = query_set.filter(semester__semester__icontains = filterSem)

        filterText = request.GET.get("filterText", None)
        if filterText is not None:
            query_set = query_set.filter(
                    Q(name__icontains=filterText) |
                    Q(pcode__icontains=filterText) |
                    Q(semester__semester__icontains=filterText) |
                    Q(project_type__type__icontains=filterText) |
                    Q(investigators__user__first_name__icontains = filterText) |
                    Q(investigators__user__last_name__icontains = filterText)
                    )
        projects = query_set.order_by(order + sortField)
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
            sortField = jsonMap.get(request.GET.get("sortField", "pcode"), "project__pcode")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            query_set = Sesshun.objects

            filterEnb = request.GET.get("filterEnb", None)
            if filterEnb is not None:
                query_set = query_set.filter(
                    status__enabled = (filterEnb.lower() == "true"))

            filterClp= request.GET.get("filterClp", None)
            if filterClp is not None:
                query_set = query_set.filter(
                    status__complete = (filterClp.lower() == "true"))

            filterType = request.GET.get("filterType", None)
            if filterType is not None:
                query_set = query_set.filter(session_type__type = filterType.lower())

            filterSci = request.GET.get("filterSci", None)
            if filterSci is not None:
                query_set = query_set.filter(observing_type__type = filterSci.lower())

            filterSem = request.GET.get("filterSem", None)
            if filterSem is not None:
                query_set = query_set.filter(project__semester__semester__icontains = filterSem)

            filterRcvr = request.GET.get("filterRcvr", None)
            if filterRcvr is not None:
                query_set = query_set.filter(receiver_group__receivers__abbreviation = filterRcvr)

            filterFreq = request.GET.get("filterFreq", None)
            if filterFreq is not None:
                query_set = query_set.filter(frequency__gt = float(filterFreq))

            filterText = request.GET.get("filterText", None)
            if filterText is not None:
                query_set = query_set.filter(
                    Q(name__icontains=filterText) |
                    Q(project__pcode__icontains=filterText) |
                    Q(project__semester__semester__icontains=filterText) |
                    Q(session_type__type__icontains=filterText) |
                    Q(observing_type__type__icontains=filterText))
            sessions = query_set.order_by(order + sortField)
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
    mode = request.GET.get("mode", None)
    if mode == "project_codes":
        projects = Project.objects.order_by('pcode')
        return HttpResponse(json.dumps({'project codes':
                                        [ p.pcode for p in projects]})
                          , mimetype = "text/plain")
    elif mode == "session_handles":
        ss = Sesshun.objects.order_by('name')
        return HttpResponse(json.dumps({'session handles':
                                        ["%s (%s)" % (s.name, s.project.pcode)
                                         for s in ss
                                        ]})
                          , mimetype = "text/plain")
    else:
        print "RETURNING NOTHING"
        return HttpResponse("")
