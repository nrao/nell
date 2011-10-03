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

from datetime                           import date, datetime, timedelta
from decorators                         import catch_json_parse_errors
from django.http                        import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models         import User as AuthUser
from django.contrib.auth.decorators     import login_required
from django.db.models                   import Q
from django.shortcuts               import render_to_response
from scheduler.httpadapters             import PeriodHttpAdapter
from scheduler.utilities                import ScheduleTools
from models                             import *
from utilities                          import *
from scheduler.models                   import User as NellUser
from nell.tools                         import IcalMap
from nell.utilities                     import TimeAccounting, TimeAgent
from users.utilities                 import get_requestor
from nell.utilities.notifiers           import SchedulingNotifier, Notifier, Email as EmailMessage
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException, JSONExceptionInfo
from reversion                          import revision
from settings                           import DATABASES, DEBUG

import simplejson as json
import twitter

@login_required
def load_nubbles(request):
    requestor = get_requestor(request)
    if requestor.isAdmin():
        return render_to_response("war/Nubbles.html", {})
    else:
        HttpResponseRedirect('/profile')

@revision.create_on_success
@catch_json_parse_errors
def receivers_schedule(request, *args, **kws):
    """
    For a given period, specified by a start date and duration, show
    all the receiver changes. Receiver changes are aligned with maintenance
    days.
    """

    # interpret the inputs
    startdate = request.GET.get("startdate", None)
    startdate = datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S') if startdate else None

    duration = request.GET.get("duration", None)
    duration = int(duration) if duration else duration

    # use the input to get the basic rx schedule
    schedule = Receiver_Schedule.extract_schedule(startdate, duration)
    jsonschd =  Receiver_Schedule.jsondict(schedule)

    # some clients also need the diff schedule
    diff     = Receiver_Schedule.diff_schedule(schedule)
    jsondiff = Receiver_Schedule.jsondict_diff(diff).get("diff_schedule", None)

    # get the dates for maintenace that cover from the start of this
    # rcvr schedule.
    maintenance = [TimeAgent.dt2str(p.start) for p in Period.objects.filter(
                       session__observing_type__type = "maintenance"
                     , start__gte = startdate).order_by("start")]

    # which receivers are temporarily unavailable?
    unavailable = [r.jsondict() for r in Receiver.objects.filter(available = False).order_by("freq_low")]

    # clients want to also know all the latest rcvrs
    rcvrs       = [r.jsondict() for r in Receiver.objects.all().order_by("freq_low") \
                       if r.abbreviation != "NS"]
    return HttpResponse(
            json.dumps({"schedule" :   jsonschd
                      , "diff":        jsondiff
                      , "maintenance": maintenance
                      , "unavailable": unavailable
                      , "receivers" :  rcvrs})
          , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def rcvr_available_toggle(request, *args, **kws):
    "Toggles the state of the given receiver's availability."

    try:
        rcvr = Receiver.get_rcvr(request.POST.get("rcvr", None))    
    except:    
        error = "Invalid Input."
        msg   = "Invalid input: %s" % request.POST.get("rcvr", None)
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

    # here comes the giant hit to the database; ready?
    rcvr.available = not rcvr.available
    rcvr.save()
    # how was that?

    revision.comment = get_rev_comment(request, None, "rcvr_available_toggle")

    return HttpResponse(json.dumps({'success':'ok'})
                      , mimetype = "text/plain")


@revision.create_on_success
@catch_json_parse_errors
def rcvr_schedule_toggle_rcvr(request, *args, **kws):
    """
    Toggles a rcvr on all the dates in the given date range.
    For a given date, if a rcvr is up, it goes down and vice versa.
    """
    try:
        fromDt = datetime.strptime(request.POST.get("from", None)
                                 , "%m/%d/%Y %H:%M:%S")
        toDt   = datetime.strptime(request.POST.get("to", None)
                                 , "%m/%d/%Y %H:%M:%S")
        rcvr = Receiver.get_rcvr(request.POST.get("rcvr", None))
    except:
        error = "Invalid Inputs."
        msg   = "One of the following are invalid inputs: %s, %s, %s" % \
            (request.POST.get("from", None)
           , request.POST.get("to", None)
           , request.POST.get("rcvr", None))
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

    success, msg = Receiver_Schedule.toggle_rcvr(fromDt, rcvr, endDt=toDt)
    revision.comment = get_rev_comment(request, None, "shift_rcvr_schedule")

    if success:
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        error = "Error Toggling Receiver."
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def rcvr_schedule_shift_date(request, *args, **kws):
    """
    Moves an existing receiver change to another date.
    """
    try:
        fromDt = datetime.strptime(request.POST.get("from", None)
                                 , "%m/%d/%Y %H:%M:%S")
        toDt   = datetime.strptime(request.POST.get("to", None)
                                 , "%m/%d/%Y %H:%M:%S")
    except:
        error = "Invalid Inputs."
        msg   = "One of the following are invalid inputs: %s, %s" % \
            (request.POST.get("from", None)
           , request.POST.get("to", None))
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

    success, msg = Receiver_Schedule.shift_date(fromDt, toDt)
    revision.comment = get_rev_comment(request, None, "shift_rcvr_schedule")

    if success:
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        error = "Error shifting date of Receiver Change."
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def rcvr_schedule_delete_date(request, *args, **kws):
    """
    Removes an existing receiver change from the receiver schedule.
    """
    try:
        dateDt = datetime.strptime(request.POST.get("startdate", None)
                                 , "%m/%d/%Y %H:%M:%S")
    except:
        error = "Invalid Inputs."
        msg   = "Invalid date: %s" % request.POST.get("startdate", None)
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

    success, msg = Receiver_Schedule.delete_date(dateDt)
    revision.comment = get_rev_comment(request, None, "delete_rcvr_schedule")

    if success:
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        error = "Error deleting date of Receiver Change."
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def rcvr_schedule_add_date(request, *args, **kws):
    """
    Adss a receiver change date to the receiver schedule.
    """
    try:
        dateDt = datetime.strptime(request.POST.get("startdate", None)
                                 , "%m/%d/%Y %H:%M:%S")
    except:
        error = "Invalid Inputs."
        msg   = "Invalid start date: %s" % request.POST.get("startdate", None)
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

    success, msg = Receiver_Schedule.add_date(dateDt)
    revision.comment = get_rev_comment(request, None, "add_rcvr_schedule")

    if success:
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        error = "Error adding date of Receiver Change."
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                           , mimetype = "text/plain")

def isFriend(user):
    au = user.auth_user
    return (au.is_staff if au is not None else False) and user.username != "dss"

@revision.create_on_success
@catch_json_parse_errors
def get_options(request, *args, **kws):
    mode = request.GET.get("mode", None)
    if mode == "project_codes":
        semesters   = request.GET.get("semesters")
        notcomplete = request.GET.get("notcomplete")
        if semesters is not None and notcomplete is not None:
            notcompleteFlt = notcomplete == 'Not Complete'
            semesters      = semesters.replace('[', '').replace(']', '').split(', ') 
            filter   = " | " .join(["Q(semester__semester = '%s')" % s for s in semesters])
            projects = Project.objects.filter(eval(filter))
            if notcomplete != 'All':
                projects = projects.filter(complete = not notcompleteFlt).order_by('pcode')
        else:
            projects = Project.objects.order_by('pcode')
        return HttpResponse(
            json.dumps({'project codes': [p.pcode for p in projects]
                      , 'project ids':   [p.id for p in projects]})
          , mimetype = "text/plain")

    elif mode == "users":
        users = User.objects.order_by('last_name')
        return HttpResponse(
            json.dumps({'users': ["%s, %s" % (u.last_name, u.first_name) \
                                  for u in users]
                      , 'ids': [u.id for u in users]})
          , mimetype = "text/plain")

    elif mode == "friends":
        users = [u for u in User.objects.all().order_by('last_name')
                   if isFriend(u)]
        return HttpResponse(
            json.dumps({'friends': ["%s, %s" % (u.last_name, u.first_name) \
                                  for u in users]
                      , 'ids': [u.id for u in users]})
          , mimetype = "text/plain")

    elif mode == "session_handles":
        semesters   = request.GET.get("semesters")
        enabled     = request.GET.get("enabled")
        notcomplete = request.GET.get("notcomplete")
        if semesters is not None and enabled is not None and notcomplete is not None:
            notcompleteFlt = notcomplete == 'Not Complete'
            enabledFlt  = enabled == 'Enabled'
            semesters   = semesters.replace('[', '').replace(']', '').split(', ') 
            filter      = " | " .join(["Q(project__semester__semester = '%s')" % s for s in semesters])
            ss = Sesshun.objects.filter(eval(filter))
            if notcomplete != 'All':
                ss = ss.filter(status__complete = not notcompleteFlt)
            if enabled != 'All':
                ss = ss.filter(status__enabled = enabledFlt)
            ss = ss.order_by('name')
        else:
            ss = Sesshun.objects.all().order_by('name')

        return HttpResponse(
            json.dumps({
                'session handles': ["%s (%s)" % (s.name, s.project.pcode) \
                                    for s in ss]
              , 'ids' : [s.id for s in ss]})
          , mimetype = "text/plain")

    elif mode == "windowed_session_handles":
        ss = Sesshun.objects.filter(session_type__type = "windowed").order_by('name')
        return HttpResponse(
            json.dumps({
                'session handles': ["%s (%s)" % (s.name, s.project.pcode) \
                                    for s in ss]
              , 'ids' : [s.id for s in ss]})
          , mimetype = "text/plain")

    elif mode == "session_names":
        ss    = Sesshun.objects.order_by('name')
        pcode = request.GET.get("pcode", None)
        if pcode:
            ss = [s for s in ss if s.project.pcode == pcode]
        return HttpResponse(
            json.dumps({'session names': ["%s" % s.name for s in ss]})
          , mimetype = "text/plain")

    elif mode == "periods":
        # return period descriptions for unique combo: pcode + sess name
        pcode   = request.GET.get("pcode", None)
        name    = request.GET.get("session_name", None)
        s       = Sesshun.objects.get(name = name, project__pcode = pcode)
        periods = Period.objects.filter(session = s).order_by('start')
        return HttpResponse(
            json.dumps({'periods': ["%s" % p.__str__() for p in periods]
                      , 'period ids': ["%s" % p.id for p in periods]})
          , mimetype = "text/plain")
    elif mode == "semesters":
        # return all the semester names
        semesters = Semester.objects.all().order_by("semester")
        return HttpResponse(
            json.dumps({'semesters': ["%s" % s.semester for s in semesters]}) 
          , mimetype = "text/plain")

    else:
        return HttpResponse("")

@catch_json_parse_errors
def get_ical(request, *args, **kws):
    """
    Returns the entire GBT calendar in iCalendar format.
    """
    response = HttpResponse(IcalMap().getSchedule(), mimetype='text/calendar')
    response['Content-Type'] = 'text/calendar'
    response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
    return response

@revision.create_on_success
@catch_json_parse_errors
def change_schedule(request, *args, **kws):
    """
    Replaces time period w/ new session, handling time accounting.
    Duration is in hours.
    """
    startdate = request.POST.get("start", None)
    startdate = datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S') if startdate else None

    duration = request.POST.get("duration", None)
    duration = float(duration) if duration else duration

    sess_name = request.POST.get("session", "").split("(")[0].strip()
    try:
        s         = Sesshun.objects.get(name = sess_name)
    except Sesshun.DoesNotExist:
        return HttpResponse(json.dumps({'error' : "Session not found."})
                          , mimetype = "text/plain")

    reason = request.POST.get("reason", "other_session_other")
    desc   = request.POST.get("description", "")

    success, msg = ScheduleTools().changeSchedule(startdate, duration, s, reason, desc)
    if success:
        revision.comment = get_rev_comment(request, None, "change_schedule")
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(
            json.dumps({'error':'Error Inserting Period', 'message':msg})
          , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def shift_period_boundaries(request, *args, **kws):
    """
    Moves boundary between two or more periods, handling time accounting.

    Note: When performing the shift, this function finds all periods within
    15 mins of the original boundary time. This will always give our specified
    period plus any neighbor to it.
    """
    time = request.POST.get("time", None)
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') if time else None

    start_boundary = bool(int(request.POST.get("start_boundary", 1)))
    reason         = request.POST.get("reason", "other_session_other")
    desc           = request.POST.get("description", "")

    period_id = int(request.POST.get("period_id", None))
    period    = Period.objects.get(id = period_id)

    original_time = period.start if start_boundary else period.end()
    for p in Period.get_periods(original_time - timedelta(minutes = 1), 15.0):
        if p.id != period_id:
            neighbor = p
            break

    success, msg = ScheduleTools().shiftPeriodBoundaries(period, start_boundary, time, neighbor, reason, desc)
    if success:
        revision.comment = get_rev_comment(request, None, "shift_period_boundaries")
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(
            json.dumps({'error':   'Error Shifting Period Boundary'
                      , 'message': msg})
          , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def time_accounting(request, *args, **kws):
    """
    POST: Sets Project time accounting.
    GET: Serves up json for time accounting from periods up to the project
    """
    project = Project.objects.get(pcode = args[0])
    if request.method == 'POST':
        a = project.get_allotment(float(request.POST.get("grade", None)))
        a.total_time = float(request.POST.get("total_time", None))
        a.save()

        project.accounting_notes = request.POST.get("description", None)
        project.save()

        revision.comment = get_rev_comment(request, None, "time_accounting")

    return HttpResponse(json.dumps(TimeAccounting().jsondict(project))
                      , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def session_time_accounting(request, *args, **kws):
    """
    Sets some time accounting variables for given period.
    """
    s = Sesshun.objects.get(name = args[0])
    if request.method == 'POST':
        s.allotment.total_time = request.POST.get("total_time", None)
        s.allotment.save()
        s.accounting_notes = request.POST.get("description", None)
        s.save()

        revision.comment = get_rev_comment(request, None, "session_time_accounting")

    return HttpResponse(json.dumps(TimeAccounting().jsondict(s.project))
                      , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def period_time_accounting(request, *args, **kws):
    "Sets some time accounting variables for given period"
    period = Period.objects.get(id = args[0])
    if request.method == 'POST':
        a = period.accounting
        a.description = request.POST.get("description", None)
        a.update_from_post(request.POST)
        valid, msg = a.validate()
        if not valid:
            title = "Error setting Period Time Accounting"
            return HttpResponse(json.dumps({'error': title, 'message': msg})
                              , mimetype = "text/plain")

        a.save()
        revision.comment = get_rev_comment(request, None, "period_time_accounting")
    return HttpResponse(
        json.dumps(TimeAccounting().jsondict(period.session.project))
      , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def publish_periods(request, *args, **kwds):
    """
    Publishes pending periods within a time range specified by a start time
    and duration.

    We tweet to let the world know we published. However, the default is to
    tweet unless we are using our sandboxes.

    Note: Supports publishing periods by time range, or a single one by id.
    """
    if len(args) == 1:
        # publish a single period specified in args by its ID
        p = Period.objects.get(id = int(args[0]))
        p.publish()
        p.save()
    else:
        # publish periods identified by time range
        startPeriods = request.POST.get("start", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        startPeriods = datetime.strptime(startPeriods, '%Y-%m-%d %H:%M:%S')

        start, duration = ScheduleTools().getSchedulingRange(
                              startPeriods
                            , request.POST.get("tz", "UTC")
                            , int(request.POST.get("duration", "1")) - 1)
        Period.publish_periods(start, duration)

    revision.comment = get_rev_comment(request, None, "publish_periods")

    if DATABASES['default']['NAME'] == 'dss' and request.POST.get("tweet", "True") == "True":
        update = 'GBT schedule updated. See https://dss.gb.nrao.edu/schedule/public for details.'
        try:
            twitter.Api(
                consumer_key        = settings.TWITTER['consumer_key']
              , consumer_secret     = settings.TWITTER['consumer_secret']
              , access_token_key    = settings.TWITTER['access_token_key']
              , access_token_secret = settings.TWITTER['access_token_secret']
            ).PostUpdate(update)
        except: # That's ok, the world doesn't HAVE to know.
            formatExceptionInfo()

    return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def restore_schedule(request, *args, **kwds):
    """
    Removes pending periods of open sessions for the specified time range,
    given by a start time and duration.
    """
    startPeriods = request.POST.get("start"
                                  , datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    startPeriods = datetime.strptime(startPeriods, '%Y-%m-%d %H:%M:%S')

    start, duration = ScheduleTools().getSchedulingRange(
                          startPeriods
                        , request.POST.get("tz", "UTC")
                        , int(request.POST.get("duration", "1")) - 1)
    # here's the steps we take to restore the schedule:
    # 1. get rid of most periods in the pending stat
    Period.delete_pending(start, duration)
    # 2. bring back any elective periods that may have been deleted
    Period.restore_electives(start, duration)
    # 3. bring back certain windowed periods that may have been deleted
    Period.restore_windows(start, duration)


    revision.comment = get_rev_comment(request, None, "restore_schedule")

    return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")

######################################################################
# Declaring 'notifier' as a global allows it to keep state between
# 'GET' and 'POST' calls of scheduling_email.
######################################################################

try:
    notifier = SchedulingNotifier()
except:
    if DEBUG:
        printException(formatExceptionInfo())


@catch_json_parse_errors
def scheduling_email(request, *args, **kwds):
    address_key = ["observer_address", "changed_address", "staff_address"]
    subject_key = ["observer_subject", "changed_subject", "staff_subject"]
    body_key    = ["observer_body", "changed_body", "staff_body"]
    email_key   = ["observer", "changed", "staff"]

    if request.method == 'GET':
        # Show the schedule from now until 8am eastern 'duration' days from now.
        start    = datetime.utcnow()
        duration = int(request.GET.get("duration"))
        end      = TimeAgent.est2utc(TimeAgent.utc2est(start + timedelta(days = duration - 1))
                                     .replace(hour = 8, minute = 0, second = 0,
                                              microsecond = 0))

        # The class that sets up the emails needs the periods in the
        # scheduling range, and all the periods in the future.
        currentPs = list(Period.objects.filter(start__gt = start
                                             , start__lt = end))
        futurePs  = list(Period.objects.filter(start__gte = start).order_by("start"))
        notifier.setPeriods(currentPs, futurePs)

        return HttpResponse(
            json.dumps({
                'observer_address' : notifier.getAddresses("observer"),
                'observer_subject' : notifier.getSubject("observer"),
                'observer_body'    : notifier.getBody("observer"),
                'changed_address'  : notifier.getAddresses("changed"),
                'changed_subject'  : notifier.getSubject("changed"),
                'changed_body'     : notifier.getBody("changed"),
                'staff_address'    : notifier.getAddresses("staff"),
                'staff_subject'    : notifier.getSubject("staff"),
                'staff_body'       : notifier.getBody("staff"),
                'obs_periods'      : [p.id for p in notifier.observingPeriods],
                'changed_periods'  : [p.id for p in notifier.changedPeriods]
            })
          , mimetype = "text/plain")

    elif request.method == 'POST':
        # here we are overriding what/who gets sent for the first round
        # of emails
        for i in xrange(3):
            addr = str(request.POST.get(address_key[i], "")).replace(" ", "").split(",")
            notifier.setAddresses(email_key[i], addr)
            notifier.setSubject(email_key[i], request.POST.get(subject_key[i], ""))
            notifier.setBody(email_key[i], request.POST.get(body_key[i], ""))

        notifier.notify()

        # Remember when we did this to allow time-tagging of the schedule
        sn = Schedule_Notification(date = datetime.utcnow())
        sn.save()

        # Emails for a given period shouldn't be sent more then is
        # necessary, so here we set the last_notification timestamp.
        # However, the client can change the recipients and text of the
        # 'changes' email - this ignores those changes.
        # See Story: https://www.pivotaltracker.com/story/show/14550249
        now = datetime.utcnow()
        set_periods_last_notification(now, request, "changed_periods")
        set_periods_last_notification(now, request, "obs_periods")

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(
                 json.dumps({'error': 'request.method is neither GET or POST!'})
               , mimetype = "text/plain")

def set_periods_last_notification(dt, request, key):
    pidsStr = request.POST.get(key, "")
    for pidStr in pidsStr.split(","):
        try:
            pid = int(pidStr.strip())
        except:
            pid = None
        if pid is not None:
            p = Period.objects.get(id = pid)
            p.last_notification = dt
            p.save()

@catch_json_parse_errors
def projects_email(request, *args, **kwds):
    if request.method == 'GET':
        pcodes = request.GET.get("pcodes", None)
        pcode_list = pcodes.split(" ") if pcodes is not None else getPcodesFromFilter(request)
        pi_list, pc_list, ci_list, ob_list, fs_list = getInvestigatorEmails(pcode_list)

        templates = EmailTemplate.get_templates(pcode_list)

        return HttpResponse(json.dumps({'PI-Addresses':   pi_list
                                      , 'PC-Addresses':   pc_list
                                      , 'CO-I-Addresses': ci_list
                                      , 'OBS-Addresses':  ob_list
                                      , 'Friend-Addresses':  fs_list
                                      , 'PCODES':         pcode_list
                                      , 'Templates':      templates})
                          , mimetype = "text/plain")

    elif request.method == 'POST':
        email_key = "projects_email"
        pe_notifier = Notifier()
        em_templ = EmailMessage("helpdesk-dss@gb.nrao.edu", "", "", "")
        pe_notifier.registerTemplate(email_key, em_templ)
        addr = str(request.POST.get("address", "")).replace(" ", "").split(",")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")

        email = pe_notifier.cloneTemplate(email_key)
        email.SetRecipients(addr)
        email.SetSubject(subject)
        email.SetBody(body)
        pe_notifier.post(email)
        pe_notifier.notify()

        return HttpResponse(json.dumps({'success':'ok'}),
                            mimetype = "text/plain")

    else:
        return HttpResponse(
                 json.dumps({'error': 'request.method is neither GET or POST!'})
               , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def window_assign_period(request, *args, **kwds):
    if len(args) != 2:
        return HttpResponse(json.dumps({'success':'error'})
                          , mimetype = "text/plain")

    # Get the window & assign the period
    try:
        win = Window.objects.get(id = int(args[0]))
    except Window.DoesNotExist:
        return HttpResponse(json.dumps({'success': 'error'})
                          , mimetype = "text/plain")
    win.assignPeriod(int(args[1]), request.POST.get("default", True))

    revision.comment = get_rev_comment(request, None, "window_assign_period")

    return HttpResponse(json.dumps({'success':'ok'})
                      , mimetype = "text/plain")

@catch_json_parse_errors
def toggle_moc(request, *args, **kwds):
    if len(args) != 1:
        return HttpResponse(json.dumps({'success':'error'})
                          , mimetype = "text/plain")

    period = Period.objects.get(id = args[0])
    period.moc_ack = not period.moc_ack
    period.save()

    revision.comment = get_rev_comment(request, None, "toggle_moc")

    return HttpResponse(json.dumps({'success':'ok'})
                      , mimetype = "text/plain")

def reservations(request, *args, **kws):
    start        = request.GET.get('start')
    days         = int(request.GET.get('days'))
    end          = (datetime.strptime(start, "%m/%d/%Y") + timedelta(days = days)).strftime("%m/%d/%Y")
    useBos       = True
    if useBos:
        reservations = getReservationsFromBOS(start, end)
    else:
        reservations = getReservationsFromDB(start, end)

    return HttpResponse(json.dumps({'reservations' : reservations
                                  , 'total'        : len(reservations)
                                   }))

tab_map = {
           '/scheduler/investigators' : 'Investigator'
         , '/scheduler/periods'       : 'Period'
         , '/scheduler/projects'      : 'Project'
         , '/scheduler/sessions'      : 'Session'
         , '/scheduler/users'         : 'User'
         , '/scheduler/windows'       : 'Window'
          }

def updateExplorerConfig(name, type, tab):
    ec, _ = ExplorerConfiguration.objects.get_or_create(name = name, type = type, tab  = tab)
    # Clear out old values if we're updated an existing config
    for c in ec.column_set.all():
        c.delete()
    for f in ec.filter_set.all():
        f.delete()
    return ec

def deleteExplorerConfig(id):
    try:
        ec = ExplorerConfiguration.objects.get(id = id)
    except ExplorerConfiguration.DoesNotExist:
        pass
    else:
        ec.delete()
    return HttpResponse(json.dumps({'success':'ok'})
                      , mimetype = "text/plain")

def column_configurations_explorer(request, *args, **kws):
    if request.method == 'POST':
        if request.POST.get("method_") == "DELETE":
            id, = args
            return deleteExplorerConfig(id)
        ec = updateExplorerConfig(request.POST.get('name')
                                , EXPLORER_CONFIG_TYPE_COLUMN
                                , tab_map.get(request.POST.get('explorer'), None))

        # Get all values that look like they might be true, hidden
        columns = [k for k, v in request.POST.iteritems() if v in ('true', ['true'] )]

        # Save the columns that belong to this configuration
        for name in columns:
            c = Column(name = name, explorer_configuration = ec)
            c.save()
        return HttpResponse(json.dumps({'success':'ok', 'id' : ec.id})
                          , mimetype = "text/plain")
    else:
        try:
            id, = args
        except ValueError:
            # If the id isn't there then get all configurations.
            tab     = tab_map.get(request.GET.get('explorer'))
            configs = [(ec.name, ec.id)
                 for ec in ExplorerConfiguration.objects.filter(tab = tab, type = EXPLORER_CONFIG_TYPE_COLUMN)]

            return HttpResponse(json.dumps({'configs' : configs})
                              , mimetype = "text/plain")
        config = ExplorerConfiguration.objects.get(id = id
                                                 , type = EXPLORER_CONFIG_TYPE_COLUMN
                                                   )
        if config is not None:
            return HttpResponse(json.dumps({'columns' : [c.name for c in config.column_set.all()]})
                                          , mimetype = "text/plain")

def filter_combinations_explorer(request, *args, **kws):
    if request.method == 'POST':
        if request.POST.get("method_") == "DELETE":
            id, = args
            return deleteExplorerConfig(id)
        ec = updateExplorerConfig(name = request.POST.get('name')
                                , type = EXPLORER_CONFIG_TYPE_FILTER
                                , tab = tab_map.get(request.POST.get('explorer'), None))

        # Save the filters that belong to this configuration
        for k, v in request.POST.iteritems():
            if k not in ('name', 'explorer'):
                f = Filter(name = k, value = v, explorer_configuration = ec)
                f.save()
        return HttpResponse(json.dumps({'success':'ok', 'id' : ec.id})
                          , mimetype = "text/plain")
    else:
        try:
            id, = args
        except ValueError:
            # If the id isn't there then get all configurations.
            tab     = tab_map.get(request.GET.get('explorer'))
            configs = [(ec.name, ec.id)
                 for ec in ExplorerConfiguration.objects.filter(tab = tab, type = EXPLORER_CONFIG_TYPE_FILTER)]

            return HttpResponse(json.dumps({'configs' : configs})
                              , mimetype = "text/plain")
        config = ExplorerConfiguration.objects.get(id = id
                                                 , type = EXPLORER_CONFIG_TYPE_FILTER
                                                  )
        if config is not None:
            filters = {}
            for f in config.filter_set.all():
                filters.update({f.name : f.value})

            return HttpResponse(json.dumps({'filters' : filters})
                                          , mimetype = "text/plain")

@catch_json_parse_errors
def window_copy(request, *args, **kwds):
    if len(args) != 1:
        return HttpResponse(json.dumps({'success':'error'})
                          , mimetype = "text/plain")
    # parse variables
    id = int(args[0])
    num = int(request.POST.get("number", 1))
    # copy the window
    copy_window(id, num)
    revision.comment = get_rev_comment(request, None, "window_copy")
    return HttpResponse(json.dumps({'success':'ok'})
                      , mimetype = "text/plain")

@catch_json_parse_errors
def elective_copy(request, *args, **kwds):
    if len(args) != 1:
        return HttpResponse(json.dumps({'success':'error'})
                          , mimetype = "text/plain")
    # parse variables
    id = int(args[0])
    num = int(request.POST.get("number", 1))
    # copy the elective
    copy_elective(id, num)
    revision.comment = get_rev_comment(request, None, "elective_copy")
    return HttpResponse(json.dumps({'success':'ok'})
                      , mimetype = "text/plain")
