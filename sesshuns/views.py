from django.template          import Context, loader
from django.http              import HttpResponse
from django_restapi.resource  import Resource
from django.shortcuts         import render_to_response
from models                   import *
from utilities                import TimeAgent
from settings                 import PROXY_PORT

from datetime import date, datetime, timedelta
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

def get_schedule(request, *args, **kws):
    #  This:
    # static two-day display
    now = TimeAgent.quarter(datetime.utcnow())
    periods = Period.objects.filter(start__gte=now).filter(start__lte=(now+timedelta(days=2))).order_by('start')
    end = now
    #   Or:
    # for now, show all periods so we can see affect of calling antioch
    #periods = Period.objects.all()
    #end = datetime(2009, 6, 1, 0, 0, 0)

    pfs = []
    for p in periods:
        if end < p.start:   # hole
            # within a day?
            if p.start.day == end.day:
                dur = p.start - end
                pfs.append(
                    createPeriodDict(end, 24*dur.days + dur.seconds/3600.))
            # spanning over midnight?
            else:
                # need total time before and after midnight!!
                p_start_end = TimeAgent.truncateDt(p.start)
                pfs.append(
                    createPeriodDict(end,
                                     TimeAgent.timedelta2minutes(p_start_end - end)/60.))
                pfs.append(
                    createPeriodDict(p_end_start,
                                     TimeAgent.timedelta2minutes(p.start - p_start_end)/60.))
        elif p.start < end: #overlap
            pass
        # within a day?
        p_end = p.start + timedelta(hours=p.duration)
        if p.start.day == p_end.day:
            pfs.append(createPeriodDict(p.start, p.duration, p))
        else:
            # need total time before and after midnight!!
            p_end_start = TimeAgent.truncateDt(p_end)
            pfs.append(createPeriodDict(p.start,
                                        TimeAgent.timedelta2minutes(p_end_start - p.start)/60.,
                                        p))
            pfs.append(createPeriodDict(p_end_start,
                                        TimeAgent.timedelta2minutes(p_end - p_end_start)/60.,
                                        p,
                                        " (cont)"))
        end = p.start + timedelta(hours=p.duration)
    proxyPort = PROXY_PORT 
    action = "http://trent.gb.nrao.edu:%d/schedule_algo" % proxyPort
    return render_to_response('sessions/schedule/index.html'
                            , {'periods': periods
                            ,  'pfs': pfs
                            ,  'action' : action})

def createPeriodDict(start, dur, per = None, suffix = ""):
    strt = start - datetime(year = start.year, month=start.month, day=start.day)
    day  = date(year = start.year, month=start.month, day=start.day)
    nqtr = int(round(60*dur)/15)
    return dict(
        sname = "" if per is None else per.session.name + suffix
      , stype = "" if per is None else per.session.observing_type.type
      , date  = str(day)
      , start = str(strt)[:-3]
      , dur   = str(nqtr)
      , durs  = [str(strt + timedelta(minutes=q))[:-3] for q in range(15, 15*nqtr, 15)]
      , freq  = "" if per is None else str(per.session.frequency) if per.session.observing_type.type != 'maintenance' else "&nbsp;"
      , notes = "" if per is None else 'backup' if per.backup else "&nbsp;"
                   )
