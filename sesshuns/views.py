from datetime                 import date, datetime, timedelta
from django.http              import HttpResponse
from models                   import Project, Receiver_Schedule, Sesshun
from tools                    import IcalMap
from settings                 import PROXY_PORT

import simplejson as json

ROOT_URL = "http://trent.gb.nrao.edu:%d" % PROXY_PORT

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
        return HttpResponse("")

def get_ical(request, *args, **kws):
    response = HttpResponse(IcalMap().getSchedule())
    response['Content-Type'] = 'text/calendar'
    response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
    return response

