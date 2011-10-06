# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from datetime                           import datetime, timedelta
from decorators                         import is_staff
from django.contrib.auth.decorators     import login_required
from django.http                        import HttpResponse, HttpResponseRedirect
from django.shortcuts                   import render_to_response
from scheduler.models                   import *
from models                             import *
from nell.utilities.TimeAgent           import EST, UTC
from observers                          import project_search
from utilities                          import get_requestor, acknowledge_moc
from utilities                          import get_rescal_supervisors, get_gbt_schedule_events
from utilities                          import TimeAgent
from django.contrib                     import messages

import calendar

@login_required
def remotely_qualified(request, *args, **kws):
    """
    Returns all remotely qualified observers.
    """
    requestor = get_requestor(request)
    qualified = User.objects.filter(sanctioned = True).order_by('last_name')

    return render_to_response('users/remotely_qualified.html'
                              , dict(requestor = requestor, q = qualified))

@login_required
def moc_reschedule(request, *args, **kws):
    """
    Allows an operator to acknowledge when the MOC is bad before an observation.
    """
    requestor = get_requestor(request)
    period    = Period.objects.get(id = args[0])

    acknowledge_moc(requestor, period)

    return render_to_response('users/moc_reschedule.html'
                            , dict(requestor = requestor, p = period))

@login_required
def moc_degraded(request, *args, **kws):
    """
    Allows an operator to acknowledge when the MOC is bad after an observation
    has begun.
    """
    requestor = get_requestor(request)
    period    = Period.objects.get(id = args[0])

    acknowledge_moc(requestor, period)

    return render_to_response('users/moc_degraded.html'
                            , dict(requestor = requestor, p = period))

@login_required
@is_staff
def gbt_schedule(request, *args, **kws):
    """
    Serves up a GBT schedule page tailored for Operations.

    Note: This view is in either ET or UTC, database is in UTC.
    """
    def cleanSD(startDate):
        try:
            return datetime.strptime(startDate, '%m/%d/%Y') if startDate else datetime.now() 
        except: # Bad input?
            return datetime.now()

    timezones = ['ET', 'UTC']

    # Note: we probably should have better error handling here,
    # but since the forms are Date Pickers and drop downs, it seems
    # difficult for the user to send us malformed params.

    # Default date, days, and timezone.  Loaded from the values
    # saved below, or from defaults if no values were saved.
    if request.method == 'POST':
        startDate, days, timezone = (None, 5, 'ET')
    else:
        startDate, days, timezone, _ = _get_calendar_defaults(request)
    data      = request.POST if request.method == 'POST' else request.GET
    timezone  = data.get('tz', timezone)
    days      = int(data.get('days', days))
    startDate = cleanSD(data.get('start', startDate))

    start   = TimeAgent.truncateDt(startDate)
    end     = start + timedelta(days = days)

    # save these values for use in 'GET' above.
    _save_calendar_defaults(request, start, days, timezone)
    requestor = get_requestor(request)
    supervisor_mode = True if (requestor in get_rescal_supervisors()) else False

    schedule = get_gbt_schedule_events(start, end, timezone)

    try:
        tzutc = Schedule_Notification.objects.latest('date').date.replace(tzinfo=UTC)
        pubdate = tzutc.astimezone(EST)
    except:
        pubdate = None

    printerFriendly = data.get('printerFriendly', None)
    template = 'users/schedules/schedule_friendly.html' if printerFriendly == '1' \
                   else 'users/schedule.html'
    return render_to_response(
        template,
        {'calendar'        : schedule,
         'day_list'        : range(1, 32),
         'tz_list'         : timezones,
         'timezone'        : timezone,
         'today'           : datetime.now(EST),
         'start'           : start,
         'startFmt'        : start.strftime('%m/%d/%Y'), 
         'days'            : days,
         'rschedule'       : Receiver_Schedule.extract_schedule(start, days),
         'requestor'       : requestor,
         'supervisor_mode' : supervisor_mode,
         'pubdate'         : pubdate,
         })

def rcvr_schedule(request, *args, **kwds):
    """
    Serves up a page showing the upcoming receiver change schedule, viewable
    by anyone.
    """
    receivers = [r for r in Receiver.objects.exclude(deleted = True) if r.abbreviation != 'NS']
    schedule  = {}
    rxSchedule = Receiver_Schedule.extract_schedule(datetime.utcnow(), 180)
    for day, rcvrs in rxSchedule.items():
        schedule[day] = [r in rcvrs for r in receivers]
    for day, ups, downs in Receiver_Schedule.diff_schedule(rxSchedule):
        schedule[day] = (schedule[day]
                       , ', '.join([up.abbreviation for up in ups])
                       , ', '.join([down.abbreviation for down in downs])
                         )

    schedule = sorted([(k, v[0], v[1], v[2]) for k, v in schedule.items()])
    return render_to_response(
               'users/receivers.html'
             , {'receivers': receivers
              , 'schedule' : schedule})

@login_required
def summary(request, *args, **kws):
    """
    Serves up a page that allows Operations to run reconcilation reports. There
    are two basic reports - schedule and project. Even though it is specifically
    for Operations, any logged in user may view it.
    """
    now        = datetime.now()
    last_month = now - timedelta(days = 31)
    psummary = []

    if request.method == 'POST':
        summary = request.POST.get('summary', 'schedule')

        project = project_search(request.POST.get('project', ''))
        if isinstance(project, list) and len(project) == 1:
            project = project[0].pcode
        else:
            project = ''

        month = request.POST.get('month', None)
        year  = request.POST.get('year', None)
        year  = int(year) if year else None
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
    if project:
        periods = [p for p in periods if p.isScheduled() and p.session.project.pcode == project]

    # Handle either schedule or project summaries.
    if summary == "schedule":
        schedule = get_gbt_schedule_events(start, end, "ET", True)
        url      = 'users/schedule_summary.html'
        projects = []
        receivers = {}
        days     = {}
        hours    = {}
        summary  = {}
    else:
        url      = 'users/project_summary.html'
        projects = list(set([p.session.project for p in periods]))
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

            # If just for one project, create a more detailed summary.
            if project:
                psummary.append((pstart, hrs, p.receiver_list))

    return render_to_response(
               url
             , {'calendar' : schedule
              , 'projects' : [(p
                             , sorted(list(set(receivers[p.pcode])))
                             , sorted(list(set(days[p.pcode]))
                                    , lambda x, y: cmp(int(x), int(y)))
                             , hours[p.pcode]) for p in projects]
              , 'start'    : start
              , 'months'   : calendar.month_name
              , 'month'    : month
              , 'years'    : [y for y in xrange(2009, now.year + 2, 1)]
              , 'year'     : year
              , 'summary'  : [(t, summary[t]) for t in sorted(summary)]
              , 'project'  : project
              , 'psummary' : psummary
              , 'is_logged_in': request.user.is_authenticated()})


######################################################################
# _get_calendar_defaults(request)
#
# Returns defaults for the GBT Schedule calendar: start date, number
# of days, and time zone.  The function tries to read it from the
# django message framework.  If that doesn't work, sets hard defaults
# of Today, 7, 'ET' for date, days, timezone.
#
# 'request' is the HttpRequest object.
#
# Returns date, days, timezone.
#
######################################################################

def _get_calendar_defaults(request):
    """
    Returns default date/time values for the GBT Schedule calendar:

    date, days, timezone = _get_calendar_defaults(request)

    where 'request' is a Django HttpRequest object.
    """

    date = datetime.now()
    day = 7
    tz_str = 'ET'
    storage = messages.get_messages(request)
    timestamp = datetime.now()

    for message in storage:
        if message.message.find('GBT_SCHEDULE_INFO') == 0:
            # message.message will be like this: 'GBT_SCHEDULE_INFO
            # 2011-03-22 7 ET (timestamp)', where (timestamp) is a
            # datetime printout, YYYY-MM-DD HH:MM:SS.ssssss.'  The
            # timestamp is used to put a freshness date on the
            # message.  Messages older than 12 hours are ignored,
            # allowing the calendar to track today's date.  If no time
            # limit were put on the message, the calendar would always
            # start with the last start day used, which could be
            # annoying as the days go by.
            part = message.message.split()
            date_parts = part[4].split('-')
            time_parts = part[5].split(':')
            seconds = time_parts[2].split('.')
            timestamp = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                                 int(time_parts[0]), int(time_parts[1]),
                                 int(seconds[0]), int(seconds[1]))
            delta = datetime.now() - timestamp
            day = int(part[2])
            tz_str = part[3]

            # if the message expired keep the user-selected days and
            # timezone, but use the default start date, which is
            # datetime.now().  This allows the calendar to advance
            # with the days.
            if delta.seconds < 43200:
                date_parts = part[1].split('-')
                date = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))

    return date, day, tz_str, timestamp

def _save_calendar_defaults(request, start, days, timezone):
    """
    Saves the start date, days, and timezone values using the Django
    message framework.  These can then be retrieved using
    _get_calendar_defaults().

    _save_calendar_defaults(request, start, days, timezone)
    """

     # NOTE: clear out old messages before adding new one.  According
     # to the Django docs, if the messages exceed 4096 bytes the
     # oldest messages will drop off the end.  Experience shows
     # however that instead you get a "ValueError: Not all temporary
     # messages could be stored." from
     # '"/home/dss/robin/django-1.2.3/django/contrib/messages/middleware.py",
     # line 25, in process_response'.
    old_start, old_days, old_tz, old_ts = _get_calendar_defaults(request)

    if old_start == start and old_days == days and old_tz == timezone:
        ts = old_ts  # preserve freshness dating if no change.
    else:
        ts = datetime.now()

    msg = "GBT_SCHEDULE_INFO %s %s %s %s" % (start.date(), days, timezone, ts)
    messages.add_message(request, messages.INFO, msg, fail_silently = True)
