from datetime                 import datetime, timedelta
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource    import NellResource
from sesshuns.models import Period, first, jsonMap, str2dt
from utilities       import TimeAgent
from utilities       import Score
#from utilities       import formatExceptionInfo

import simplejson as json

class PeriodResource(NellResource):
    def __init__(self, *args, **kws):
        super(PeriodResource, self).__init__(Period, *args, **kws)

    def read(self, request, *args, **kws):
        tz = args[0]
        score_period = Score()
        # one or many?
        if len(args) == 1:
            # we are getting periods from within a range of dates
            sortField = jsonMap.get(request.GET.get("sortField", "start"), "start")
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            startPeriods = request.GET.get("startPeriods"
                                         , datetime.now().strftime("%Y-%m-%d"))
            daysPeriods  = request.GET.get("daysPeriods", "1")
            dt = str2dt(startPeriods)
            start = dt if tz == 'UTC' else TimeAgent.est2utc(dt)
            duration = int(daysPeriods) * 24 * 60
            periods = Period.get_periods(start, duration)
            pids = [p.id for p in periods]
            sd = score_period.periods(pids)
            scores = [sd.get(pid, 0.0) for pid in pids]
            return HttpResponse(
                json.dumps(dict(total = len(periods)
                              , periods = [p.jsondict(tz, s)
                                               for (p, s) in zip(periods, scores)]))
              , content_type = "application/json")
        else:
            # we're getting a single period as specified by ID
            p_id  = int(args[1])
            p     = first(Period.objects.filter(id = p_id))
            score = score_period.periods([p_id]).get(p_id, 0.0)
            return HttpResponse(json.dumps(dict(period = p.jsondict(tz, score))))

    def create_worker(self, request, *args, **kws):
        o = self.dbobject()
        tz = args[0]
        score_period = Score()
        o.init_from_post(request.POST, tz)
        # Query the database to insure data is in the correct data type
        o = first(self.dbobject.objects.filter(id = o.id))
        score = score_period.periods([o.id]).get(o.id, 0.0)
        
        return HttpResponse(json.dumps(o.jsondict(tz, score))
                          , mimetype = "text/plain")

    def update(self, request, *args, **kws):
        tz    = args[0]
        id    = int(args[1])
        o     = self.dbobject.objects.get(id = id)
        o.update_from_post(request.POST, tz)

        return HttpResponse("")

    def delete(self, request, *args):
        id = int(args[1])
        o  = self.dbobject.objects.get(id = id)
        o.delete()
        
        return HttpResponse(json.dumps({"success": "ok"}))

