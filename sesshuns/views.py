from datetime                           import date, datetime, timedelta
from decorators                         import catch_json_parse_errors
from django.http                        import HttpResponse
from django.contrib.auth.models         import User as AuthUser
from httpadapters                       import PeriodHttpAdapter
from models                             import *
from models                             import User as NellUser
from nell.tools                         import IcalMap, ScheduleTools, TimeAccounting
from nell.utilities                     import TimeAgent
from nell.utilities.SchedulingNotifier  import SchedulingNotifier
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException, JSONExceptionInfo
from nell.utilities.Notifier            import Notifier
from nell.utilities.Email               import Email as EmailMessage  #name clash with models
from reversion                          import revision
from settings                           import PROXY_PORT, DATABASE_NAME
from utilities                          import *

import simplejson as json
import twitter

@revision.create_on_success
@catch_json_parse_errors
def receivers_schedule(request, *args, **kws):
    """
    For a given period, specified by a start date and duration, show
    all the receiver changes. Receiver changes are aligned with maintenance
    days.
    """
    startdate = request.GET.get("startdate", None)
    startdate = datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S') if startdate else None

    duration = request.GET.get("duration", None)
    duration = int(duration) if duration else duration

    schedule = Receiver_Schedule.extract_schedule(startdate, duration)
    diff     = Receiver_Schedule.diff_schedule(schedule)
    jsondiff = Receiver_Schedule.jsondict_diff(diff).get("diff_schedule", None)

    maintenance = [PeriodHttpAdapter(p).jsondict('UTC', 0.) \
                   for p in Period.objects.filter( 
                       session__name = "Maintenance").order_by("start")]

    rcvrs       = [r.jsondict() for r in Receiver.objects.all() \
                                if r.abbreviation != "NS"]
    return HttpResponse(
            json.dumps({"schedule" :   Receiver_Schedule.jsondict(schedule)
                      , "diff":        jsondiff
                      , "maintenance": maintenance
                      , "receivers" :  rcvrs})
          , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def change_rcvr_schedule(request, *args, **kws):
    """
    Updates the receiver schedule. Some receivers go 'up'. Others come 'down'.
    """
    startdate = request.POST.get("startdate", None)
    startdate = datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S') if startdate else None
    error     = "Error Changing Receiver Schedule"

    # Going up!
    upStr   = request.POST.get("up", None)
    upRcvrs = upStr.strip().split(" ") if upStr != "" else []
    e, up   = getReceivers(upRcvrs) 
    if e:
        return HttpResponse(json.dumps({'error': error, 'message': e})
                          , mimetype = "text/plain")

    # Coming down!
    downStr   = request.POST.get("down", None)
    downRcvrs = downStr.strip().split(" ") if downStr != "" else []
    e, down   = getReceivers(downRcvrs) 
    if e:
        return HttpResponse(json.dumps({'error': error, 'message': e})
                          , mimetype = "text/plain")

    # Update the schedule.
    success, msg = Receiver_Schedule.change_schedule(startdate, up, down)
    revision.comment = get_rev_comment(request, None, "change_rcvr_schedule")

    if success:
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(json.dumps({'error': error, 'message': msg})
                               , mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def shift_rcvr_schedule_date(request, *args, **kws):
    """
    Moves an existing receiver change to another date.
    """
    fromDt = datetime.strptime(request.POST.get("from", None)
                             , "%m/%d/%Y %H:%M:%S")
    toDt   = datetime.strptime(request.POST.get("to", None)
                             , "%m/%d/%Y %H:%M:%S")

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
def delete_rcvr_schedule_date(request, *args, **kws):
    """
    Removes an existing receiver change from the receiver schedule.
    """
    dateDt = datetime.strptime(request.POST.get("startdate", None)
                             , "%m/%d/%Y %H:%M:%S")

    success, msg = Receiver_Schedule.delete_date(dateDt)
    revision.comment = get_rev_comment(request, None, "delete_rcvr_schedule")

    if success:
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        error = "Error deleting date of Receiver Change."
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
        incomplete = request.GET.get('notcomplete', None)
        enabled    = request.GET.get('enabled')
        if incomplete is not None and enabled is not None:
            complete = not (incomplete.lower() == 'true', None)
            enabled  = enabled.lower() == 'true'
            ss = Sesshun.objects.filter(status__complete = complete).filter(status__enabled = enabled).order_by('name')
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
        ss      = Sesshun.objects.filter(name = name)
        s       = first([s for s in ss if s.project.pcode == pcode])
        periods = Period.objects.filter(session = s).order_by('start')
        return HttpResponse(
            json.dumps({'periods': ["%s" % p.__str__() for p in periods]
                      , 'period ids': ["%s" % p.id for p in periods]})
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
    s         = first(Sesshun.objects.filter(name = sess_name))

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
    period    = first(Period.objects.filter(id = period_id))

    original_time = period.start if start_boundary else period.end()
    ps = Period.get_periods(original_time - timedelta(minutes = 1), 15.0)
    neighbor = first([p for p in ps if p.id != period_id])

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
    project = first(Project.objects.filter(pcode = args[0]))
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
    s = first(Sesshun.objects.filter(name = args[0]))
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
    period = first(Period.objects.filter(id = args[0]))
    if request.method == 'POST':
        a = period.accounting
        a.description = request.POST.get("description", None)

        for field in ["scheduled", "not_billable", "short_notice"
                    , "lost_time_weather", "lost_time_rfi", "lost_time_other"
                    , "other_session_weather", "other_session_rfi"
                    , "other_session_other"]:
            a.set_changed_time(field, float(request.POST.get(field, None)))

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
        # Reuse code by using this periods time range
        p     = first(Period.objects.filter(id = int(args[0])))
        start = p.start
        # TBF: Kluge, we don't want to publish the next period as well,
        # so end a minute early to avoid picking it up.
        duration = int(p.duration * 60.0) # hrs to minutes
    else:
        startPeriods = request.POST.get("start", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        startPeriods = datetime.strptime(startPeriods, '%Y-%m-%d %H:%M:%S')

        start, duration = ScheduleTools().getSchedulingRange(
                              startPeriods
                            , request.POST.get("tz", "UTC")
                            , int(request.POST.get("duration", "1")) - 1)

    Period.publish_periods(start, duration)
    revision.comment = get_rev_comment(request, None, "publish_periods")

    if DATABASE_NAME == 'dss' and request.POST.get("tweet", "True") == "True":
        update = 'GBT Schedule Update - https://dss.gb.nrao.edu/schedule/public'
        try:
            twitter.Api(username = 'GrnBnkTelescope'
                      , password = 'dYN4m1(').PostUpdate(update)
        except: # That's ok, the world doesn't HAVE to know.
            formatExceptionInfo()

    return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")

@revision.create_on_success
@catch_json_parse_errors
def delete_pending(request, *args, **kwds):
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

    for p in Period.get_periods(start, duration):
        if p.isPending() and p.session.session_type.type == 'open':
            p.delete()

    revision.comment = get_rev_comment(request, None, "delete_pending")

    return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")

######################################################################
# Declaring 'notifier' as a global allows it to keep state between
# 'GET' and 'POST' calls of scheduling_email.
######################################################################

try:
    notifier = SchedulingNotifier()
except:
    printException(formatExceptionInfo())

@catch_json_parse_errors
def scheduling_email(request, *args, **kwds):
    address_key = ["observer_address", "deleted_address", "staff_address"]
    subject_key = ["observer_subject", "deleted_subject", "staff_subject"]
    body_key    = ["observer_body", "deleted_body", "staff_body"]
    email_key   = ["observer", "deleted", "staff"]

    if request.method == 'GET':
        # Show the schedule from now until 8am eastern 'duration' days from now.
        start    = datetime.utcnow()
        duration = int(request.GET.get("duration"))
        end      = TimeAgent.est2utc(TimeAgent.utc2est(start + timedelta(days = duration - 1))
                                     .replace(hour = 8, minute = 0, second = 0,
                                              microsecond = 0))

        notifier.setPeriods(list(Period.objects.filter(start__gt = start
                                                     , start__lt = end)))

        return HttpResponse(
            json.dumps({
                'observer_address' : notifier.getAddresses("observer"),
                'observer_subject' : notifier.getSubject("observer"),
                'observer_body'    : notifier.getBody("observer"),
                'deleted_address'  : notifier.getAddresses("deleted"),
                'deleted_subject'  : notifier.getSubject("deleted"),
                'deleted_body'     : notifier.getBody("deleted"),
                'staff_address'    : notifier.getAddresses("staff"),
                'staff_subject'    : notifier.getSubject("staff"),
                'staff_body'       : notifier.getBody("staff")
            })
          , mimetype = "text/plain")

    elif request.method == 'POST':
        # here we are overriding what/who gets sent for the first round
        # of emails, but because we setup the object with Periods (above)
        # we aren't controlling who gets the 'change schedule' emails (TBF)

        for i in xrange(3):
            addr = str(request.POST.get(address_key[i], "")).replace(" ", "").split(",")
            notifier.setAddresses(email_key[i], addr)
            notifier.setSubject(email_key[i], request.POST.get(subject_key[i], ""))
            notifier.setBody(email_key[i], request.POST.get(body_key[i], ""))

        notifier.notify()

        # Remember when we did this to allow time-tagging of the schedule
        sn = Schedule_Notification(date = datetime.utcnow())
        sn.save()

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(
                 json.dumps({'error': 'request.method is neither GET or POST!'})
               , mimetype = "text/plain")

@catch_json_parse_errors
def projects_email(request, *args, **kwds):
    if request.method == 'GET':
        pcodes = request.GET.get("pcodes", None)
        pcode_list = pcodes.split(" ") if pcodes is not None else getPcodesFromFilter(request)
        pi_list, pc_list, ci_list = getInvestigators(pcode_list)

        return HttpResponse(json.dumps({'PI-Addresses':   pi_list
                                      , 'PC-Addresses':   pc_list
                                      , 'CO-I-Addresses': ci_list
                                      , 'PCODES':         pcode_list})
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
    win = first(Window.objects.filter(id = int(args[0])))
    if win is None:
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

    period = first(Period.objects.filter(id = args[0]))
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
           '/investigators' : 'Investigator'
         , '/periods'       : 'Period'
         , '/projects'      : 'Project'
         , '/sessions'      : 'Session'
         , '/users'         : 'User'
         , '/windows'       : 'Window'
          }

def updateExplorerConfig(name, type, tab):
    ec = first(ExplorerConfiguration.objects.filter(name = name, type = type, tab  = tab))
    if ec is not None:
        # Clear out old values if we're updated an existing config
        for c in ec.column_set.all():
            c.delete()
        for f in ec.filter_set.all():
            f.delete()
    else:
        ec = ExplorerConfiguration(name = name
                                 , type = type
                                 , tab  = tab)
        ec.save()
    return ec

def deleteExplorerConfig(id):
    ec = first(ExplorerConfiguration.objects.filter(id = id))
    if ec is not None:
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
        config = first(ExplorerConfiguration.objects.filter(id = id
                                                          , type = EXPLORER_CONFIG_TYPE_COLUMN
                                                           ))
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
        config = first(ExplorerConfiguration.objects.filter(id = id
                                                          , type = EXPLORER_CONFIG_TYPE_FILTER
                                                           ))
        if config is not None:
            filters = {}
            for f in config.filter_set.all():
                filters.update({f.name : f.value})
            
            return HttpResponse(json.dumps({'filters' : filters})
                                          , mimetype = "text/plain")
