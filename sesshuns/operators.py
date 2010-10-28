from datetime                       import datetime, timedelta
from decorators                     import is_operator
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse, HttpResponseRedirect
from django.shortcuts               import render_to_response
from models                         import *
from nell.utilities                 import gen_gbt_schedule
from nell.utilities.TimeAgent       import EST, UTC
from observers                      import project_search
from sets                           import Set
from utilities                      import get_requestor, acknowledge_moc
import calendar

@login_required
def remotely_qualified(request, *args, **kws):
    """
    Returns all remotely qualified observers.
    """
    requestor = get_requestor(request)
    qualified = User.objects.filter(sanctioned = True).order_by('last_name')

    return render_to_response('sesshuns/remotely_qualified.html'
                            , dict(requestor = requestor, q = qualified))

@login_required
def moc_reschedule(request, *args, **kws):
    """
    Allows an operator to acknowledge when the MOC is bad before an observation.
    """
    requestor = get_requestor(request)
    period    = first(Period.objects.filter(id = args[0]))

    acknowledge_moc(requestor, period)

    return render_to_response('sesshuns/moc_reschedule.html'
                            , dict(requestor = requestor, p = period))

@login_required
def moc_degraded(request, *args, **kws):
    """
    Allows an operator to acknowledge when the MOC is bad after an observation
    has begun.
    """
    requestor = get_requestor(request)
    period    = first(Period.objects.filter(id = args[0]))

    acknowledge_moc(requestor, period)

    return render_to_response('sesshuns/moc_degraded.html'
                            , dict(requestor = requestor, p = period))

@login_required
@is_operator
def gbt_schedule(request, *args, **kws):
    """
    Serves up a GBT schedule page tailored for Operations.

    Note: This view is in either ET or UTC, database is in UTC.
    """
    timezones = ['ET', 'UTC']

    # TBF: error handling
    if request.method == 'POST':
        timezone  = request.POST.get('tz', 'ET')
        days      = int(request.POST.get('days', 5))
        startDate = request.POST.get('start', None)
        startDate = datetime.strptime(startDate, '%m/%d/%Y') if startDate else datetime.now()
    else: # default time range
        timezone  = 'ET'
        days      = 7
        startDate = datetime.now()

    start   = TimeAgent.truncateDt(startDate)
    end     = start + timedelta(days = days)
    pstart  = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend    = TimeAgent.est2utc(end) if timezone == 'ET' else end

    periods  = [p for p in Period.in_time_range(pstart, pend) \
                if not p.isPending()]
    maintenance_activities = {}

    for i in range(0, len(periods)):
        if periods[i].session.observing_type.type == "maintenance":
            mas = Maintenance_Activity.get_maintenance_activity_set(periods[i])
        else:
            if i < len(periods) - 1:
                mas = Maintenance_Activity.objects\
                      .filter(start__gte = periods[i].start)\
                      .filter(start__lt = periods[i + 1].start)\
                      .filter(period = None)\
                      .filter(deleted = False)
            else:
                mas = Maintenance_Activity.objects\
                      .filter(start__gte = periods[i].start)\
                      .filter(start__lt = periods[i].end())\
                      .filter(period = None)\
                      .filter(deleted = False)

        maintenance_activities[periods[i]] = mas

    schedule = gen_gbt_schedule(start, end, days, 'ET', periods, maintenance_activities)

    try:
        s_n = Schedule_Notification.objects.all()
        tzutc = s_n[len(s_n)-1].date.replace(tzinfo=UTC)
        pubdate = tzutc.astimezone(EST)
    except:
        pubdate = None

    # need this for resource calendar use
    maprj = Project.objects.filter(pcode = "Maintenance")[0]

    return render_to_response(
               'sesshuns/schedule.html',
               {'calendar'        : sorted(schedule.items()),
                'day_list'        : range(1, 32),
                'tz_list'         : timezones,
                'timezone'        : timezone,
                'today'           : datetime.now(EST),
                'start'           : start,
                'days'            : days,
                'rschedule'       : Receiver_Schedule.extract_schedule(start, days),
                'timezone'        : timezone,
                'requestor'       : get_requestor(request),
                'pubdate'         : pubdate,
                'maintenance_prj' : maprj
               })

def rcvr_schedule(request, *args, **kwds):
    """
    Serves up a page showing the upcoming receiver change schedule, viewable
    by anyone.
    """
    receivers = [r for r in Receiver.objects.all() if r.abbreviation != 'NS']
    schedule  = {}
    for day, rcvrs in Receiver_Schedule.extract_schedule(datetime.utcnow(), 180).items():
        schedule[day] = [r in rcvrs for r in receivers]

    return render_to_response(
               'sesshuns/receivers.html'
             , {'receivers': receivers
              , 'schedule' : sorted(schedule.items())})

@login_required
def summary(request, *args, **kws):
    """
    Serves up a page that allows Operations to run reconcilation reports. There
    are two basic reports - schedule and project. Even though it is specifically
    for Operations, any logged in user may view it.
    """
    now        = datetime.now()
    last_month = now - timedelta(days = 31)

    if request.method == 'POST':
        summary = request.POST.get('summary', 'schedule')

        project = project_search(request.POST.get('project', ''))
        if isinstance(project, list) and len(project) == 1:
            project = project[0].pcode
        else:
            project = ''

        month = request.POST.get('month', None)
        year  = int(request.POST.get('year', None))
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

    end = datetime(start.year
                 , start.month
                 , calendar.monthrange(start.year, start.month)[1]) + \
          timedelta(days = 1)

    # View is in ET, database is in UTC. Only use scheduled periods.
    periods = Period.in_time_range(TimeAgent.est2utc(start)
                                 , TimeAgent.est2utc(end))
    periods = [p for p in periods if p.isScheduled()]
    if project:
        periods = [p for p in periods if p.session.project.pcode == project]

    # Handle either schedule or project summaries.
    if summary == "schedule":
        schedule = gen_gbt_schedule(start
                                  , end
                                  , (end - start).days
                                  , "ET"
                                  , periods)
        url      = 'sesshuns/schedule_summary.html'
        projects = []
        receivers = {}
        days     = {}
        hours    = {}
        summary  = {}
    else:
        url      = 'sesshuns/project_summary.html'
        projects = list(Set([p.session.project for p in periods]))
        projects.sort(lambda x, y: cmp(x.pcode, y.pcode))

        receivers = {}
        for p in periods:
            rxs = receivers.get(p.session.project.pcode, [])
            rxs.extend([r.abbreviation for r in p.receivers.all()])
            receivers[p.session.project.pcode] = rxs

        schedule = {}
        days     = dict([(p.pcode, []) for p in projects])
        hours    = dict([(p.pcode, 0) for p in projects])
        summary  = dict([(c, 0) for c in Sesshun.getCategories()])
        for p in periods:
            pstart = TimeAgent.utc2est(p.start)
            pend   = TimeAgent.utc2est(p.end())

            # Find the days this period ran within the month.
            day = pstart.day if pstart >= start else pend.day
            days[p.session.project.pcode].append(str(day))
            if day != pend.day: # For multi-day periods
                days[p.session.project.pcode].append(str(pend.day))

            # Find the duration of this period within the month.
            duration = min(pend, end) - max(pstart, start)
            hrs = duration.seconds / 3600. + duration.days * 24.
            hours[p.session.project.pcode] += hrs

            # Tally hours for various categories important to Operations.
            summary[p.session.getCategory()] += hrs

    return render_to_response(
               url
             , {'calendar' : sorted(schedule.items())
              , 'projects' : [(p
                             , sorted(list(Set(receivers[p.pcode])))
                             , sorted(list(Set(days[p.pcode]))
                                    , lambda x, y: cmp(int(x), int(y)))
                             , hours[p.pcode]) for p in projects]
              , 'start'    : start
              , 'months'   : calendar.month_name
              , 'month'    : month
              , 'years'    : [y for y in xrange(2009, now.year + 2, 1)]
              , 'year'     : year
              , 'summary'  : [(t, summary[t]) for t in sorted(summary)]
              , 'project'  : project
              , 'is_logged_in': request.user.is_authenticated()})
