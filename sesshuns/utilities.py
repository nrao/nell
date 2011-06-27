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

from datetime                           import datetime, time, timedelta
from django.db.models                   import Q
from pytz                               import timezone
from copy                               import deepcopy
import pytz

from scheduler.models                   import *
from sesshuns.models                    import *
from scheduler.httpadapters             import *
from nell.utilities.database.external   import UserInfo
from nell.utilities                     import TimeAgent
from sesshuns.GBTCalendarEvent          import CalEventPeriod, CalEventFixedMaintenance
from sesshuns.GBTCalendarEvent          import CalEventFloatingMaintenance, CalEventIncidental
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException

import settings


def target_hv(value):
    t = value.getTarget()
    tag = "*" if t.isEphemeris() else ""
    return t.get_horizontal() + tag, t.get_vertical() + tag

def getReceivers(names):
    rcvrs = []
    error = None
    for name in [n for n in names if len(n) != 0]:
        r = Receiver.get_rcvr(name)
        if r is not None:
            rcvrs.append(r)
        else:
            error = 'Unrecognized receiver: %s' % name
    return error, rcvrs

def acknowledge_moc(requestor, period):
    """
    Sets acknowledge flag for periods which fail MOC.
    """
    if requestor.isOperator(): # Only operators can acknowledge MOC failures.
        period.moc_ack = True
        period.save()

def create_user(username):
    """
    If the DSS doesn't know about the user, but the User Portal does,
    then add them to our database so they can at least see their profile.
    """
    info = UserInfo().getStaticContactInfoByUserName(username
                                                   , use_cache = False)
    user = User(pst_id     = info['person_id']
              , first_name = info['first_name']
              , last_name  = info['last_name']
              , role       = Role.objects.get(role = "Observer"))
    user.save()

    p = Preference(user = user, timeZone = "UTC")
    p.save()

    return user

def get_requestor(request):
    """
    Gets login name; and if we don't have a user with that name,
    creates one before returning the user.

    Note: CAS (used by PST) has case-insensitive usernames.
    """
    loginUser = request.user.username
    if loginUser is None or loginUser == '':
        return
    pst_id = UserInfo().getIdFromUsername(loginUser)

    try:
        requestor = User.objects.get(pst_id = pst_id)
    except User.DoesNotExist:
        requestor = create_user(loginUser)

    return requestor

def get_blackout_form_context(b_id, fdata, user, requestor, errors):
    "Returns dictionary for populating blackout form"
    return {
        'u'        : user
      , 'requestor': requestor
      , 'b_id'   : b_id
      , 'b'        : fdata # b's dates in DB are UTC
      , 'tzs'      : TimeZone.objects.all()
      , 'timezone' : 'UTC' # form always starts at UTC
      , 'repeats'  : Repeat.objects.all()
      , 'times'    : [time(h, m).strftime("%H:%M") \
                      for h in range(0, 24) for m in range(0, 60, 15)]
      , 'errors'   : errors
    }

def adjustDate(tz_pref, dt, to_utc = False):
    if dt is None:
        return
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    tz  = timezone(tz_pref)
    utc = pytz.utc
    if to_utc:
        return tz.localize(dt).astimezone(utc)
    else:
        return utc.localize(dt).astimezone(tz)

def parse_datetime(fdata, dateName, timeName, tz):
    "Extract the date & time from the form values to make a datetime obj"
    dt    = None
    error = None
    try:
        if fdata[dateName] != '':
            dt = adjustDate(tz, datetime.strptime(
                                 "%s %s" % (fdata[dateName], fdata[timeName])
                               , "%m/%d/%Y %H:%M")
                          , to_utc = True)

    except:
        error = "ERROR: malformed %s date" % dateName
    return (dt, error)

def project_search(value):
    projects = Project.objects.filter(
        Q(pcode__icontains = value) | \
            Q(name__icontains = value) | \
            Q(semester__semester__icontains = value.upper()))
    projects = [p for p in projects]

    # Search for project by short code.
    for p in Project.objects.all():
        code = p.pcode.replace("TGBT", "")
        code = code.replace("GBT", "")
        code = code.replace("_0", "")
        code = code.replace("-0", "")
        code = code.replace("_", "")
        code = code.replace("-", "")

        code = code[1:] if len(code) > 2 and code[0] == "0" else code

        if code == value.upper() and p not in projects:
            projects.append(p)

    return projects

######################################################################
# Creates a list of events for the date range provided. First, gets
# all the scheduled periods.  Next, gets the pending maintenance
# periods.  Finally, collects the non-maintenance-period maintenance
# events for each day. These are then sorted and added to the day's
# activities.  For every day there will be a tuple consisting of the
# datetime for that day, and a list of that day's events.
######################################################################

def get_gbt_schedule_events(start, end, timezone, get_moc = False,
                            ignore_non_maint_period_maint_events = False):
    """
    Generate a list of schedule events.  The list returned consists of
    tuples: first element is a datetime, the second element is the
    list of events for that date.
    """
    days = (end - start).days
    calendar = []
    one_day = timedelta(days = 1)
    utc_start  = TimeAgent.est2utc(start) if timezone == 'ET' else start
    # find ids of all periods that failed the MOC criteria
    # in the scheduling range
    if get_moc:
        moc_failures = Period.moc_failures(utc_start - one_day, days + 1)
    else:
        moc_failures = []
    old_monday = None

    for i in range(0, days):
        daily_events = []

        # must use UTC equivalents for database lookups if times given
        # in Eastern Time
        today = start + timedelta(days = i)
        utc_today  = TimeAgent.est2utc(today) if timezone == 'ET' else today
        utc_yesterday = utc_today - one_day
        utc_tomorrow = utc_today + one_day
        
        # get the Monday for the week.  The maintenance activity
        # groups are retrieved for the entire week, so we do this only
        # once per week.
        monday = utc_today - timedelta(utc_today.weekday())

        if monday != old_monday:
            mags = Maintenance_Activity_Group.get_maintenance_activity_groups(monday)
            old_monday = monday

        # Include previous day's periods because last one may end
        # today.  Perhaps there is a way to do this exclusively via
        # query, but there aren't that many periods in a day.  Exclude
        # the maintenance periods, because they are obtained above.
        ps = Period.objects.filter(start__gte = utc_yesterday)\
            .filter(start__lt = utc_tomorrow).filter(state__name = "Scheduled")\
            .exclude(session__observing_type__type = "maintenance")

        for p in ps:
            if p.end() > utc_today:
                # periods can be everything non-maintenance
                ev = CalEventPeriod(p
                                  , p.start < utc_today
                                  , p.end() > utc_tomorrow
                                  , p.id not in moc_failures
                                  , timezone)
                daily_events.append(ev)

        daily_events += _get_fixed_maint_events(mags, today, timezone)

        # if today is monday, get floating maintenance events for the week
        if today.weekday() == 0:
            daily_events += _get_floating_maint_events(mags, timezone)

        # finally gather up the non-maintenance-period maintenance events
        if not ignore_non_maint_period_maint_events:
            daily_events += _get_incidental_events(today, timezone)

        # now sort the events and add to the calendar list
        daily_events.sort()
        calendar.append((today, daily_events))

    return calendar

######################################################################
# This helper returns this day's fixed maintenance periods.
######################################################################

def _get_fixed_maint_events(mags, day, timezone):
    """
    _get_fixed_maint_events(mags, day, timezone)

    Takes a set of maintenance activity groups and returns the one for
    'day' if there is a fixed one for 'day'.
    """

    evs = []
    day = TimeAgent.truncateDt(day)
    tomorrow = day + timedelta(1)

    for mag in mags:
        if mag.period:        # fixed if period is set
            if TimeAgent.truncateDt(mag.get_start(timezone)) == day or \
                    TimeAgent.truncateDt(mag.get_end(timezone)) == day:
                ev = CalEventFixedMaintenance(mag, mag.get_start(timezone) < day,
                                              mag.get_end(timezone) >= tomorrow,
                                              True, timezone)
                evs.append(ev)
    return evs

######################################################################
# This helper returns the floating maintenance activities.
######################################################################

def _get_floating_maint_events(mags, timezone):
    """
    _get_floating_maint_events(mags, timezone)

    Given a list of maintenance groups, returns CalEvents for the
    floating ones.
    """

    evs = []

    for mag in mags:
        if not mag.period:
            ev = CalEventFloatingMaintenance(contained = mag, TZ = timezone)
            evs.append(ev)

    return evs

######################################################################
# Finds any non-maintenance-period maintenance activities and places
# them in a CalEvent object.  This object is returned as a list of one
# CalEvent object, to make it easier to add to other lists of CalEvent
# objects.
######################################################################

def _get_incidental_events(today, timezone):
    """
    Gathers up all the non-maintenance-period maintenance activities,
    and returns them in a list of CalEvent objects.
    """

    utc_today = TimeAgent.est2utc(today) if timezone == 'ET' else today

    mas = Maintenance_Activity.objects.filter(_start__gte = utc_today) \
        .filter(_start__lt = utc_today + timedelta(days = 1)) \
        .filter(group = None) \
        .filter(deleted = False) \
        .order_by('_start')

    if mas.exists():
        ev = CalEventIncidental(mas, TZ = timezone)
        return [ev]

    return []

def get_rescal_supervisors():
    # TBF: when roles done, will get these by visiting the roles.
    s = []

    # don't spam supervisors from test setups
    if settings.DEBUG == True:
        s += User.objects.filter(auth_user__username = 'rcreager')
    else:
        s += User.objects.filter(auth_user__username = 'rcreager')
        s += User.objects.filter(auth_user__username = 'banderso')
        s += User.objects.filter(auth_user__username = 'mchestnu')

    return s
