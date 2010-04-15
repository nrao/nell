from datetime                       import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import render_to_response
from models                   import *
from observers                import project_search
from sets                     import Set
from utilities                import gen_gbt_schedule
from utilities.TimeAgent      import EST
import calendar

@login_required
def moc_reschedule(request, *args, **kws):
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))
    p_id,     = args
    period    = first(Period.objects.filter(id = p_id))

    if requestor is None:
        requestor = create_user(loginUser)

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
        requestor = create_user(loginUser)

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
        requestor = create_user(loginUser)

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
        days      = 7 
        startDate = datetime.now()

    start = TimeAgent.truncateDt(startDate)
    end   = start + timedelta(days = days)

    # View is in ET or UTC, database is in UTC.
    pstart  = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend    = TimeAgent.est2utc(end) if timezone == 'ET' else end
    periods = Period.in_time_range(pstart, pend)

    # ignore pending periods!
    periods = [p for p in periods if p.state.abbreviation != 'P']

    schedule = gen_gbt_schedule(start, end, days, 'ET', periods)

    return render_to_response(
               'sesshuns/schedule.html'
             , {'calendar' : sorted(schedule.items())
              , 'day_list' : range(1, 32)
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

@login_required
def summary(request, *args, **kws):
    now        = datetime.now()
    last_month = now - timedelta(days = 31)

    if request.method == 'POST': 
        summary = request.POST.get('summary', 'schedule') 

        project = project_search(request.POST.get('project', ''))
        if isinstance(project, list) and len(project) == 1:
            project = project[0].pcode
        else:
            project = ''

        month   = request.POST.get('month', None) 
        year    = int(request.POST.get('year', None))
        if month and year:
            start = datetime(int(year)
                           , [m for m in calendar.month_name].index(month)
                           , 1)
        else: # Default to last month
            start = datetime(last_month.year, last_month.month, 1)
            month = calendar.month_name[start.month]
            year  = start.year
    else: # Default to last month
        summary    = 'schedule'
        project    = ''
        start      = datetime(last_month.year, last_month.month, 1)
        month      = calendar.month_name[start.month]
        year       = start.year

    end  = datetime(start.year
                  , start.month
                  , calendar.monthrange(start.year, start.month)[1]) + \
           timedelta(days = 1)

    # View is in ET, database is in UTC. Ignore pending periods.
    periods = Period.in_time_range(TimeAgent.est2utc(start)
                                 , TimeAgent.est2utc(end))
    periods = [p for p in periods if p.state.abbreviation != 'P']
    if project:
        periods = [p for p in periods if p.session.project.pcode == project]

    # Get schedule for this time.
    schedule = gen_gbt_schedule(start, end, (end - start).days, "ET", periods)

    if summary == "schedule":
        url      = 'sesshuns/schedule_summary.html'
        projects = []
        days     = {}
        hours    = {}
    else:
        url      = 'sesshuns/project_summary.html'
        projects = list(Set([p.session.project for p in periods]))
        projects.sort(lambda x, y: cmp(x.pcode, y.pcode))

        days  = {}
        hours = {}
        for p in periods:
            d = days.setdefault(p.session.project.pcode, [])
            days[p.session.project.pcode] = list(Set(d + [p.start.day]))

            h = hours.setdefault(p.session.project.pcode, 0)
            hours[p.session.project.pcode] = h + p.accounting.observed()

    return render_to_response(
               url
             , {'calendar' : sorted(schedule.items())
              , 'projects' : zip(projects
                               , [[str(d) for d in sorted(v)] \
                                          for v in days.values()]
                               , hours.values())
              , 'start'    : start
              , 'months'   : calendar.month_name 
              , 'month'    : month
              , 'years'    : [y for y in xrange(2009, now.year + 2, 1)]
              , 'year'     : year
              , 'summary'  : summary
              , 'project'  : project
              , 'is_logged_in': request.user.is_authenticated()})
