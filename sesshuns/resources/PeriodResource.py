from datetime                 import datetime, timedelta
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource    import NellResource
from sesshuns.models import Period, first, jsonMap, str2dt

import simplejson as json

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

