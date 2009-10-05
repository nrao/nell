from datetime                       import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import render_to_response
from models                   import *
from sets                     import Set
from utilities                import gen_gbt_schedule
from utilities.TimeAgent      import EST

@login_required
def moc_reschedule(request, *args, **kws):
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))
    p_id,     = args
    period    = first(Period.objects.filter(id = p_id))

    if requestor is None:
        create_user(loginUser)

    if requestor.isOperator():
        # Only operators can acknowledge MOC failures.
        period.moc_ack = True 
        period.save()

    return render_to_response(
        'sesshuns/moc_reschedule.html'
      , {'requestor': requestor
       , 'p'        : period}
    )

@login_required
def moc_degraded(request, *args, **kws):
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))
    p_id,     = args
    period    = first(Period.objects.filter(id = p_id))

    if requestor is None:
        create_user(loginUser)

    if requestor.isOperator():
        # Only operators can acknowledge MOC failures.
        period.moc_ack = True 
        period.save()

    return render_to_response(
        'sesshuns/moc_degraded.html'
      , {'requestor': requestor
       , 'p'        : period}
    )

@login_required
def gbt_schedule(request, *args, **kws):
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        create_user(loginUser)

    if not requestor.isOperator() and not requestor.isAdmin():
        return HttpResponseRedirect("/schedule/public")

    # serve up the GBT schedule
    timezones = ['ET', 'UTC']

    # TBF: error handling
    if request.method == 'POST': 
        timezone  = request.POST.get('tz', 'ET')
        days      = int(request.POST.get('days', 5))    
        startDate = request.POST.get('start', None) 
        startDate = datetime.strptime(startDate, '%m/%d/%Y') if startDate else datetime.now() 
    else:
        # default time range
        timezone  = 'ET'
        days      = 14 
        startDate = datetime.now()

    start = TimeAgent.truncateDt(startDate)
    end   = start + timedelta(days = days)

    # View is in ET or UTC, database is in UTC.
    pstart  = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend    = TimeAgent.est2utc(end) if timezone == 'ET' else end
    periods = Period.in_time_range(pstart, pend)

    calendar = gen_gbt_schedule(start, end, days, 'ET', periods)

    return render_to_response(
               'sesshuns/schedule.html'
             , {'calendar' : sorted(calendar.items())
              , 'day_list' : range(1, 15)
              , 'tz_list'  : timezones
              , 'timezone' : timezone
              , 'today'    : datetime.now(EST)
              , 'start'    : start
              , 'days'     : days
              , 'rschedule': Receiver_Schedule.extract_schedule(start, days)
              , 'timezone' : timezone
              , 'requestor': requestor})

def rcvr_schedule(request, *args, **kwds):
    receivers = [r for r in Receiver.objects.all() if r.abbreviation != 'NS']
    schedule  = {}
    for day, rcvrs in Receiver_Schedule.extract_schedule(datetime.utcnow(), 90).items():
        schedule[day] = [r in rcvrs for r in receivers]

    return render_to_response(
               'sesshuns/receivers.html'
             , {'receivers': receivers
              , 'schedule' : sorted(schedule.items())})
