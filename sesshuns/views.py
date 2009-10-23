from datetime                 import date, datetime, timedelta
from django.http              import HttpResponse
from models                   import Project, Sesshun, Period
from models                   import Receiver_Schedule, first
from tools                    import IcalMap, ScheduleTools, TimeAccounting
from settings                 import PROXY_PORT
from utilities.SchedulingNotifier import SchedulingNotifier

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
    elif mode == "session_names":
        ss = Sesshun.objects.order_by('name')
        pcode = request.GET.get("pcode", None)
        if pcode is not None:
            ss = [s for s in ss if s.project.pcode == pcode]
        return HttpResponse(json.dumps({'session names':
                                        ["%s" % s.name
                                         for s in ss
                                        ]})
                          , mimetype = "text/plain")
    elif mode == "periods":
        # return period descriptions for unique combo: pcode + sess name
        pcode = request.GET.get("pcode", None)
        name  = request.GET.get("session_name", None)
        ss = Sesshun.objects.filter(name = name)
        s = first([s for s in ss if s.project.pcode == pcode])
        periods = Period.objects.filter(session = s).order_by('start')
        return HttpResponse(json.dumps({'periods':
                                        ["%s" % p.__str__()
                                         for p in periods
                                        ]
                                      , 'period ids':
                                        ["%s" % p.id for p in periods]})
                          , mimetype = "text/plain")
    else:
        return HttpResponse("")

def get_ical(request, *args, **kws):
    response = HttpResponse(IcalMap().getSchedule())
    response['Content-Type'] = 'text/calendar'
    response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
    return response

def change_schedule(request, *args, **kws):
    "Replaces time period w/ new session, handling time accounting."
    # just have a lot of params to process
    startdate = request.POST.get("start", None)
    if startdate is not None:
        d, t      = startdate.split(' ')
        y, m, d   = map(int, d.split('-'))
        h, mm, ss = map(int, map(float, t.split(':')))
        startdate = datetime(y, m, d, h, mm, ss)
    duration = request.POST.get("duration", None)
    if duration is not None: 
        duration = float(duration) # hours!
    sess_handle = request.POST.get("session", "")
    sess_name = sess_handle.split("(")[0].strip()
    s = first(Sesshun.objects.filter(name = sess_name))
    reason = request.POST.get("reason", "other_session_other")
    desc = request.POST.get("description", "") 
    # this method handles the heavy lifting
    st = ScheduleTools()
    st.changeSchedule(startdate, duration, s, reason, desc)
    return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")
    
def time_accounting(request, *args, **kws):
    """
    POST: Sets Project time accounting.
    GET: Serves up json for time accounting from periods up to the project"
    """
    ta = TimeAccounting()
    pcode = args[0]
    project = first(Project.objects.filter(pcode = pcode))
    if request.method == 'POST':
        # set some project level time accounting info first
        # before returning the time accounting
        desc = request.POST.get("description", None)
        project.accounting_notes = desc
        # next: what grade is this for?
        grade = float(request.POST.get("grade", None))
        a = project.get_allotment(grade)
        a.total_time = float(request.POST.get("total_time", None))
        a.save()
        project.save()
    js = ta.jsondict(project)
    return HttpResponse(json.dumps(js), mimetype = "text/plain")

def session_time_accounting(request, *args, **kws):
    "Sets some time accounting variables for given period"

    name = args[0]
    s = first(Sesshun.objects.filter(name = name))
    s.allotment.total_time = request.POST.get("total_time", None)
    s.allotment.save()
    s.accounting_notes = request.POST.get("description", None)
    s.save()
    # now return the consequences this may have to the rest of the
    # project time accounting
    ta = TimeAccounting()
    js = ta.jsondict(s.project)
    return HttpResponse(json.dumps(js), mimetype = "text/plain")

def period_time_accounting(request, *args, **kws):
    "Sets some time accounting variables for given period"
    
    id = args[0]
    period = first(Period.objects.filter(id = id))
    a = period.accounting
    fields = ["scheduled"
            , "not_billable"
            , "short_notice"
            , "lost_time_weather"
            , "lost_time_rfi"
            , "lost_time_other"
            , "other_session_weather"
            , "other_session_rfi"
            , "other_session_other"
            ]
    for field in fields:
        value = float(request.POST.get(field, None))
        a.set_changed_time(field, value) #request.POST.get(field, None))
    a.description = request.POST.get("description", None)
    a.save()
    # now return the consequences this may have to the rest of the
    # project time accounting
    project = period.session.project
    ta = TimeAccounting()
    js = ta.jsondict(project)
    return HttpResponse(json.dumps(js), mimetype = "text/plain")

def scheduling_email(request, *args, **kwds):
    if request.method == 'GET':
        start    = datetime.utcnow()
        end      = start + timedelta(days = 2)
        periods  = Period.objects.filter(start__gt = start, start__lt = end)
        notifier = SchedulingNotifier([p for p in periods.all()])

        return HttpResponse(
            json.dumps({
                'emails' : notifier.getAddresses()
              , 'subject': notifier.getSubject()
              , 'body'   : notifier.getBody()
            })
          , mimetype = "text/plain")
    elif request.method == 'POST':
        notifier = SchedulingNotifier([])

        notifier.setAddresses(str(request.POST.get("emails", "")).replace(" ", "").split(","))
        notifier.setSubject(request.POST.get("subject", ""))
        notifier.setBody(request.POST.get("body", ""))

        notifier.notify()

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(json.dumps({'success':'error'})
                          , mimetype = "text/plain")
