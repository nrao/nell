from datetime                           import datetime, timedelta
from decorators                         import is_staff
from django.contrib.auth.decorators     import login_required
from django.http                        import HttpResponse, HttpResponseRedirect
from django.shortcuts                   import render_to_response
from models                             import *
from nell.utilities                     import gen_gbt_schedule
from nell.utilities.TimeAgent           import EST, UTC
from observers                          import project_search
from sets                               import Set
from utilities                          import get_requestor, acknowledge_moc
from GBTCalendarEvent                   import CalEventPeriod, CalEventElective, CalEventMaintenanceActivity
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException

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
@is_staff
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

    requestor = get_requestor(request)

    # Ensure only operators or admins trigger costly MOC calculations
    if requestor.isOperator() or requestor.isAdmin():
        get_moc = True
    else:
        get_moc = False

    schedule = _get_gbt_schedule_events(start, end, timezone, get_moc)

    try:
        tzutc = Schedule_Notification.objects.latest('date').date.replace(tzinfo=UTC)
        pubdate = tzutc.astimezone(EST)
    except:
        pubdate = None

    return render_to_response(
        'sesshuns/schedule.html',
        {'calendar'        : schedule,
         'day_list'        : range(1, 32),
         'tz_list'         : timezones,
         'timezone'        : timezone,
         'today'           : datetime.now(EST),
         'start'           : start,
         'days'            : days,
         'rschedule'       : Receiver_Schedule.extract_schedule(start, days),
         'requestor'       : requestor,
         'pubdate'         : pubdate,
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


######################################################################
# Creates a list of events for the date range provided. First, gets
# all the scheduled periods.  Next, gets the pending maintenance
# periods.  Finally, collects the non-maintenance-period maintenance
# events for each day. These are then sorted and added to the day's
# activities.  For every day there will be a tuple consisting of the
# datetime for that day, and a list of that day's events.
######################################################################

def _get_gbt_schedule_events(start, end, timezone, get_moc):
    """
    Generate a list of schedule events.  The list returned consists of
    tuples: first element is a datetime, the second element is the
    list of events for that date.
    """

    days = (end - start).days
    calendar = []

    for i in range(0, days):
        daily_events = []
        today = start + timedelta(days = i)
        delta = timedelta(days = 1)
        yesterday = today - delta
        tomorrow = today + delta

        # must use UTC equivalents for database lookups if times given
        # in Eastern Time
        utc_today  = TimeAgent.est2utc(today) if timezone == 'ET' else today
        utc_yesterday = utc_today - delta
        utc_tomorrow = utc_today + delta
        
        # include previous day's periods because last one may end
        # today.  Perhaps there is a way to do this exclusively via
        # query, but there aren't that many periods in a day.
        ps = Period.objects.filter(start__gte = utc_yesterday)\
            .filter(start__lt = utc_tomorrow).filter(state__name = "Scheduled")

        for p in ps:
            if p.end() > utc_today:
                ev = CalEventPeriod(p, p.start < utc_today, p.end() > utc_tomorrow,
                                    p.moc_met() if get_moc else True, timezone)
                daily_events.append(ev)

        # if today is monday, get floating maintenance events for the week
        if today.weekday() == 0:
            daily_events += _get_floating_maint_events(today, timezone)

        # finally gather up the non-maintenance-period maintenance events
        daily_events += _get_non_maint_period_maint_events(today, timezone)

        # now sort the events and add to the calendar list
        daily_events.sort()
        calendar.append((today, daily_events))

    return calendar

######################################################################
# This helper gathers up all the floating maintenance activities
# Floating activities may come as pending periods, or incomplete
# electives and have a session type of 'maintenance'.  This helper
# fetches the pending periods (if any) and the incomplete events (if
# any) in the date range, packages them in a list of CalEvents, sorts
# the list and labels each event appropriately ('A', 'B', etc.) and
# returns the list.
######################################################################

def _get_floating_maint_events(day, timezone):
    """
    _get_floating_maint_events(day, timezone)
    
    Takes the day (assumes it is Monday) and finds the maintenance
    periods for that week.  Returns a list of CalEvent objects
    consisting of all the floating activities for that Monday's week.
    """

    pend = []
    utc_day = TimeAgent.est2utc(day) if timezone == 'ET' else day

    try:
        delta = timedelta(days = 7)
        # get maintenance periods for the date span
        mp = Period.objects\
            .filter(session__observing_type__type = "maintenance")\
            .filter(start__gte = utc_day)\
            .filter(start__lt = utc_day + delta)\
            .filter(elective = None)\
            .exclude(state__abbreviation = 'D')

        # get maintenance electives for the date span
        me = Elective.objects\
            .filter(session__observing_type__type = 'maintenance')\
            .filter(periods__start__gte = utc_day)\
            .filter(periods__start__lt = utc_day + delta)\
            .distinct()

        # combine both kinds of maintenance events (elective provides
        # first period as representative), then sort the events by
        # underlying period's start datetime.
        maint_events = []
        next_day = utc_day + timedelta(days = 1)

        for p in mp:
            ev = CalEventPeriod(p, p.start < utc_day, p.end() >= next_day, True, timezone)
            maint_events.append(ev)

        for i in me:
            ev = CalEventElective(i, TZ = timezone)
            maint_events.append(ev)

        maint_events.sort()

        # ensure that first one gets 'A', second 'B', etc.
        for i in range(0, len(maint_events)):
            maint_events[i].set_fm_name(chr(i + 65))

        # now remove those that are scheduled.  Including scheduled
        # non-elective periods and completed electives in the above
        # queries ensures that if 'A' has been scheduled, 'B' still
        # appears as 'B' and not the new 'A', which would happen if we
        # only consider pending periods or non-complete electives.
        maint_events = [e for e in maint_events if e.is_floating_maintenance()] 
    except:
        if settings.DEBUG == True:
            printException(formatExceptionInfo())

        maint_events = []

    return maint_events

######################################################################
# Finds any non-maintenance-period maintenance activities and places
# them in a CalEvent object.  This object is returned as a list of one
# CalEvent object, to make it easier to add to other lists of CalEvent
# objects.
######################################################################

def _get_non_maint_period_maint_events(today, timezone):
    """
    Gathers up all the non-maintenance-period maintenance activities,
    and returns them in a list of CalEvent objects.
    """

    utc_today = TimeAgent.est2utc(today) if timezone == 'ET' else today

    mas = Maintenance_Activity.objects.filter(_start__gte = utc_today) \
        .filter(_start__lt = utc_today + timedelta(days = 1)) \
        .filter(period = None) \
        .filter(deleted = False) \
        .order_by('_start')

    if mas.exists():
        ev = CalEventMaintenanceActivity(mas, TZ = timezone)
        return [ev]

    return []
