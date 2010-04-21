from datetime                      import date, datetime, timedelta
from django.http                   import HttpResponse
from django.db.models              import Q
from models                        import Project, Sesshun, Period, Receiver
from models                        import Receiver_Schedule, first, str2dt
from models                        import Window
from models                        import User
from tools                         import IcalMap, ScheduleTools, TimeAccounting
from utilities                     import TimeAgent
from settings                      import PROXY_PORT, DATABASE_NAME
from utilities.SchedulingNotifier  import SchedulingNotifier
from utilities.FormatExceptionInfo import formatExceptionInfo, printException
from utilities.FormatExceptionInfo import JSONExceptionInfo
from utilities.Notifier            import Notifier
from utilities.Email               import Email
from reversion                     import revision
from httpadapters                  import PeriodHttpAdapter

import simplejson as json
# TBF: get this back in once we figure out the deployment issues.
import twitter

ROOT_URL = "http://trent.gb.nrao.edu:%d" % PROXY_PORT

def get_rev_comment(request, obj, method):

    className = obj.__class__.__name__ if obj is not None else ""
    where = "%s %s" % (className, method)
    who = request.user.username
    return "WHO: %s, WHERE: %s" % (who, where)

@revision.create_on_success
def receivers_schedule(request, *args, **kws):
    try:
        # get the schedule
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
        # get the alternative view of the schedule
        diff = Receiver_Schedule.diff_schedule(schedule)
        jsondiff = Receiver_Schedule.jsondict_diff(diff).get("diff_schedule", None)
        # get all the maintanence days on the schedule
        # (these are days that rcvr changes *can* happen)
        maintenance = Period.objects.filter(session__name = "Maintenance").order_by("start")
        # get the list of all receivers
        rcvrs = [r.jsondict() for r in Receiver.objects.all() \
            if r.abbreviation != "NS"]
        return HttpResponse(
                json.dumps({"schedule" : Receiver_Schedule.jsondict(schedule)
                          , "diff"     : jsondiff
                          , "maintenance": [PeriodHttpAdapter(p).jsondict('UTC', 0.0) for p in maintenance]
                          , "receivers" : rcvrs})
              , mimetype = "text/plain")
    except ValueError:
        return JSONExceptionInfo()

@revision.create_on_success
def change_rcvr_schedule(request, *args, **kws):
    try:
        # on a given date, some rcvrs are going up and coming down:
        startdate = request.POST.get("startdate", None)
        # TBF: use datetime.strptime
        #startdate = datetime.strptime(startdateStr, "%m/%d/%Y")
        if startdate is not None:
            d, t      = startdate.split(' ')
            y, m, d   = map(int, d.split('-'))
            h, mm, ss = map(int, map(float, t.split(':')))
            startdate = datetime(y, m, d, h, mm, ss)

        upStr   = request.POST.get("up", None)
        downStr = request.POST.get("down", None)
        error = "Error Changing Receiver Schedule"

        # translate the up & down rcvrs; TBF: refactor to method
        up = []
        upStr = upStr if upStr != "" else None
        if upStr is not None:
            upNames = upStr.strip().split(" ")
            for abbr in upNames:
                r = Receiver.get_rcvr(abbr)
                if r is not None:
                    up.append(r)
                else:
                    msg = "Unrecognized receiver: %s" % abbr
                    return HttpResponse(json.dumps({'error': error
                                                  , 'message': msg})
                                      , mimetype = "text/plain")
        down = []
        downStr = downStr if downStr != "" else None
        if downStr is not None:
            downNames = downStr.strip().split(" ")
            for abbr in downNames:
                r = Receiver.get_rcvr(abbr)
                if r is not None:
                    down.append(r)
                else:
                    msg = "Unrecognized receiver: %s" % abbr
                    return HttpResponse(json.dumps({'error': error
                                                  , 'message': msg})
                                      , mimetype = "text/plain")

        # finally, try and change the rcvr scheudle
        success, msg = Receiver_Schedule.change_schedule(startdate, up, down)

        revision.comment = get_rev_comment(request, None, "change_rcvr_schedule")

        if success:
            return HttpResponse(json.dumps({'success':'ok'})
                              , mimetype = "text/plain")
        else:
            return HttpResponse(json.dumps({'error': error
                                          , 'message': msg})
                               , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def shift_rcvr_schedule_date(request, *args, **kws):
    try:
        fromStr = request.POST.get("from", None)
        toStr   = request.POST.get("to", None)
        fromDt = datetime.strptime(fromStr, "%m/%d/%Y %H:%M:%S")
        toDt   = datetime.strptime(toStr, "%m/%d/%Y %H:%M:%S")
        success, msg = Receiver_Schedule.shift_date(fromDt, toDt)
        revision.comment = get_rev_comment(request, None, "shift_rcvr_schedule")
        if success:
            return HttpResponse(json.dumps({'success':'ok'})
                              , mimetype = "text/plain")
        else:
            error = "Error shifting date of Receiver Change."
            return HttpResponse(json.dumps({'error': error
                                          , 'message': msg})
                               , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()

@revision.create_on_success
def delete_rcvr_schedule_date(request, *args, **kws):
    try:
        dateStr = request.POST.get("startdate", None)
        dateDt = datetime.strptime(dateStr, "%m/%d/%Y %H:%M:%S")
        success, msg = Receiver_Schedule.delete_date(dateDt)
        revision.comment = get_rev_comment(request, None, "delete_rcvr_schedule")
        if success:
            return HttpResponse(json.dumps({'success':'ok'})
                              , mimetype = "text/plain")
        else:
            error = "Error deleting date of Receiver Change."
            return HttpResponse(json.dumps({'error': error
                                          , 'message': msg})
                               , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def get_options(request, *args, **kws):
    try:
        mode = request.GET.get("mode", None)
        if mode == "project_codes":
            projects = Project.objects.order_by('pcode')
            return HttpResponse(json.dumps({'project codes':
                                            [ p.pcode for p in projects]
                                          , 'project ids':
                                            [ p.id for p in projects]})
                              , mimetype = "text/plain")
        elif mode == "users":
            users = User.objects.order_by('last_name')
            return HttpResponse(json.dumps(
               {'users' : ["%s, %s" % (u.last_name, u.first_name) for u in users]
              , 'ids'   : [u.id for u in users]
               })
             , mimetype = "text/plain")

        elif mode == "session_handles":
            ss = Sesshun.objects.order_by('name')
            return HttpResponse(json.dumps({'session handles':
                                            ["%s (%s)" % (s.name, s.project.pcode)
                                             for s in ss
                                            ]
                                          , 'ids' : [s.id for s in ss]})
                              , mimetype = "text/plain")
        elif mode == "windowed_session_handles":
            ss = Sesshun.objects.filter(session_type__type = "windowed").order_by('name')
            return HttpResponse(json.dumps({'session handles':
                                            ["%s (%s)" % (s.name, s.project.pcode)
                                             for s in ss
                                            ]
                                          , 'ids' : [s.id for s in ss]})
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
    except:
        return JSONExceptionInfo()


def get_ical(request, *args, **kws):
    try:
        response = HttpResponse(IcalMap().getSchedule())
        response['Content-Type'] = 'text/calendar'
        response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
        return response
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def change_schedule(request, *args, **kws):
    "Replaces time period w/ new session, handling time accounting."

    try:
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
        revision.comment = get_rev_comment(request, None, "change_schedule")
        return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def shift_period_boundaries(request, *args, **kws):
    "moves boundray between two or more periods, handling time accounting."
    try:
        # just have a lot of params to process
        time = request.POST.get("time", None)
        if time is not None:
            d, t      = time.split(' ')
            y, m, d   = map(int, d.split('-'))
            h, mm, ss = map(int, map(float, t.split(':')))
            time      = datetime(y, m, d, h, mm, ss)
        period_id = int(request.POST.get("period_id", None))
        period = first(Period.objects.filter(id = period_id))
        start_boundary = bool(int(request.POST.get("start_boundary", 1)))
        reason = request.POST.get("reason", "other_session_other")
        desc = request.POST.get("description", "")
        # now, what is the neighbor to this boundary?
        original_time = period.start if start_boundary else period.end()
        # many ways to do this. one way is to find all periods w/ in 15 mins
        # of the original boundary time: this will always give our specified period
        # plus any neighbor to it.
        ps = Period.get_periods(original_time - timedelta(minutes = 1)
                              , 15.0)
        neighbors = [p for p in ps if p.id != period_id]
        if len(neighbors) == 0:
            neighbor = None
        else:
            neighbor = neighbors[0]
        # this method handles the heavy lifting
        st = ScheduleTools()
        success, msg = st.shiftPeriodBoundaries(period, start_boundary, time, neighbor, reason, desc)
        revision.comment = get_rev_comment(request, None, "shift_period_boundaries")
        if success:
            return HttpResponse(json.dumps({'success':'ok'}), mimetype = "text/plain")
        else:
            return HttpResponse(json.dumps({'error':'Error Shifting Period Boundary', 'message':msg}), mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def time_accounting(request, *args, **kws):
    """
    POST: Sets Project time accounting.
    GET: Serves up json for time accounting from periods up to the project
    """

    try:
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
            revision.comment = get_rev_comment(request, None, "time_accounting")
        js = ta.jsondict(project)
        return HttpResponse(json.dumps(js), mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def session_time_accounting(request, *args, **kws):
    "Sets some time accounting variables for given period"

    try:
        name = args[0]
        s = first(Sesshun.objects.filter(name = name))
        s.allotment.total_time = request.POST.get("total_time", None)
        s.allotment.save()
        s.accounting_notes = request.POST.get("description", None)
        s.save()
        revision.comment = get_rev_comment(request, None, "session_time_accounting")
        # now return the consequences this may have to the rest of the
        # project time accounting
        ta = TimeAccounting()
        js = ta.jsondict(s.project)
        return HttpResponse(json.dumps(js), mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def period_time_accounting(request, *args, **kws):
    "Sets some time accounting variables for given period"

    try:
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

        # validate the new time accounting
        valid, msg = a.validate()
        if not valid:
            # don't save this, and notify the user
            title = "Error setting Period Time Accounting"
            return HttpResponse(json.dumps({'error':title, 'message':msg})
                              , mimetype = "text/plain")

        a.save()
        revision.comment = get_rev_comment(request, None, "period_time_accounting")
        # now return the consequences this may have to the rest of the
        # project time accounting
        project = period.session.project
        ta = TimeAccounting()
        js = ta.jsondict(project)
        return HttpResponse(json.dumps(js), mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


#@transaction.commit_on_success
@revision.create_on_success
def publish_periods(request, *args, **kwds):
    try:
        # support publishing periods by time range, or a single one by id
        if len(args) == 1:
            # reuse code by using this periods time range
            pid = int(args[0])
            p = first(Period.objects.filter(id = pid))
            start = p.start
            # TBF: kluge, we don't want to publish the next period as well,
            # so end a minute early to avoid picking it up.
            duration = int(p.duration * 60.0) # hrs to minutes
        else:
            # from the time range passed in, get the periods to publish
            startPeriods = request.POST.get("start"
                                     , datetime.now().strftime("%Y-%m-%d"))
            daysPeriods  = request.POST.get("duration", "1")
            tz           = request.POST.get("tz", "UTC")
            dt = str2dt(startPeriods)
            start = dt if tz == 'UTC' else TimeAgent.est2utc(dt)
            duration = int(daysPeriods) * 24 * 60

        Period.publish_periods(start, duration)

        revision.comment = get_rev_comment(request, None, "publish_periods")

        # Let the world know if we so desire. Default is to tweet unless we
        # are using our sandboxes.
        if DATABASE_NAME == 'dss' and request.POST.get("tweet", "True") == "True":
            update = 'GBT Schedule Update - https://dss.gb.nrao.edu/schedule/public'
            try:
                twitter.Api(username = 'GrnBnkTelescope'
                          , password = 'dYN4m1(').PostUpdate(update)
            except: # That's ok, the world doesn't HAVE to know.
                formatExceptionInfo()

        # Ok, we're done.
        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


@revision.create_on_success
def delete_pending(request, *args, **kwds):
    "Removes pending periods of open sessions"

    try:
        # from the time range passed in, get the pending periods to delete
        startPeriods = request.POST.get("start"
                                     , datetime.now().strftime("%Y-%m-%d"))
        daysPeriods  = request.POST.get("duration", "1")
        tz           = request.POST.get("tz", "UTC")
        dt = str2dt(startPeriods)
        start = dt if tz == 'UTC' else TimeAgent.est2utc(dt)
        duration = int(daysPeriods) * 24 * 60
        periods = Period.get_periods(start, duration)
        for p in periods:
            if p.state.abbreviation == 'P' and \
                p.session.session_type.type == 'open':
                p.delete()
                # don't save here, because the state has NOT been changed,
                # it's really been removed since it was in the Pending state
                #p.save()

        revision.comment = get_rev_comment(request, None, "delete_pending")

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()


######################################################################
# Declaring 'notifier' as a global allows it to keep state between
# 'GET' and 'POST' calls of scheduling_email.
######################################################################

try:
    notifier = SchedulingNotifier()
except:
    printException(formatExceptionInfo())

def scheduling_email(request, *args, **kwds):

    address_key = ["observer_address", "deleted_address", "staff_address"]
    subject_key = ["observer_subject", "deleted_subject", "staff_subject"]
    body_key    = ["observer_body", "deleted_body", "staff_body"]
    email_key   = ["observer", "deleted", "staff"]

    if request.method == 'GET':
        try:
            # Show the schedule from now until 8am eastern 'duration' days from now.
            start    = datetime.utcnow()
            duration = int(request.GET.get("duration"))
            end      = TimeAgent.est2utc(TimeAgent.utc2est(start + timedelta(days = duration - 1))
                                         .replace(hour = 8, minute = 0, second = 0,
                                                  microsecond = 0))

            periods  = list(Period.objects.filter(start__gt = start, start__lt = end))
            notifier.setPeriods(periods)

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
        except:
            return JSONExceptionInfo()

    elif request.method == 'POST':
        # here we are overriding what/who gets sent for the first round
        # of emails, but because we setup the object with Periods (above)
        # we aren't controlling who gets the 'change schedule' emails (TBF)

        try:
            for i in range(0, 3):
                addr = str(request.POST.get(address_key[i], "")).replace(" ", "").split(",")
                notifier.setAddresses(email_key[i], addr)
                notifier.setSubject(email_key[i], request.POST.get(subject_key[i], ""))
                notifier.setBody(email_key[i], request.POST.get(body_key[i], ""))

            notifier.notify()
        except:
            return JSONExceptionInfo()

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    else:
        return HttpResponse(json.dumps({'error':'request.method is neither GET or POST!'})
                          , mimetype = "text/plain")



def getInvestigators(pcodes):
    pi = []
    pc = []
    ci = []
    try:
        for i in pcodes:
            p = Project.objects.filter(pcode = i)[0]
            for k in p.investigator_set.all():
                if k.principal_investigator:
                    for j in k.user.email_set.all():
                        pi.append(j.email)
                if k.principal_contact:
                    for j in k.user.email_set.all():
                        pc.append(j.email)
                if not k.principal_investigator and not k.principal_contact:
                    for j in k.user.email_set.all():
                        ci.append(j.email)
    except IndexError, data:
        pass # in case of blanks at the end of the list.
    return pi, pc, ci


def getPcodesFromFilter(request):

    query_set = Project.objects.all()
    filterClp = request.GET.get("filterClp", None)

    if filterClp is not None:
        query_set = query_set.filter(
            complete = (filterClp.lower() == "true"))

    filterType = request.GET.get("filterType", None)

    if filterType is not None:
        query_set = query_set.filter(project_type__type = filterType.lower())

    filterSem = request.GET.get("filterSem", None)

    if filterSem is not None:
        query_set = query_set.filter(semester__semester__icontains = filterSem)

    filterText = request.GET.get("filterText", None)

    if filterText is not None:
        query_set = query_set.filter(
                Q(name__icontains                            = filterText) |
                Q(pcode__icontains                           = filterText) |
                Q(semester__semester__icontains              = filterText) |
                Q(project_type__type__icontains              = filterText))

    pcodes = [p.pcode for p in query_set]
    return pcodes


def projects_email(request, *args, **kwds):
    if request.method == 'GET':
        try:
            # Show the schedule from now until 8am eastern 'duration' days from now.
            pcodes = request.GET.get("pcodes") # pcodes is a Unicode string

            if pcodes:
                pcode_list = pcodes.split(" ")
            else:
                pcode_list = getPcodesFromFilter(request)

            pi_list, pc_list, ci_list = getInvestigators(pcode_list)

            return HttpResponse(
                json.dumps({
                    'PI-Addresses'   : pi_list,
                    'PC-Addresses'   : pc_list,
                    'CO-I-Addresses' : ci_list,
                    'PCODES'         : pcode_list
                 })
              , mimetype = "text/plain")
        except:
            return JSONExceptionInfo()

    elif request.method == 'POST':
        try:
            email_key = "projects_email"
            pe_notifier = Notifier()
            pe_notifier.registerTemplate(email_key, Email("helpdesk-dss@gb.nrao.edu", "", "", ""))
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
        except:
            return JSONExceptionInfo()

    else:
        return HttpResponse(json.dumps({'error':'request.method is neither GET or POST!'}),
                            mimetype = "text/plain")


@revision.create_on_success
def window_assign_period(request, *args, **kwds):
    try:
        if len(args) != 2:
            return HttpResponse(json.dumps({'success':'error'})
                              , mimetype = "text/plain")
        windowId = int(args[0])
        periodId = int(args[1])
        default = request.POST.get("default", True)

        # get the window & assign the period
        win = first(Window.objects.filter(id = windowId))
        if win is None:
            return HttpResponse(json.dumps({'success':'error'})
                              , mimetype = "text/plain")
        win.assignPeriod(periodId, default)

        revision.comment = get_rev_comment(request, None, "window_assign_period")

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()

def toggle_moc(request, *args, **kwds):
    try:
        if len(args) != 1:
            return HttpResponse(json.dumps({'success':'error'})
                              , mimetype = "text/plain")

        period = first(Period.objects.filter(id = args[0]))
        period.moc_ack = not period.moc_ack
        period.save()

        revision.comment = get_rev_comment(request, None, "toggle_moc")

        return HttpResponse(json.dumps({'success':'ok'})
                          , mimetype = "text/plain")
    except:
        return JSONExceptionInfo()
