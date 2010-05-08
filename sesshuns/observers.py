from datetime                       import datetime, time, timedelta
from decorators                     import *
from django.contrib.auth.decorators import login_required
from django.db.models         import Q
from django.core.exceptions   import ObjectDoesNotExist
from django                   import forms
from django.http              import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts         import render_to_response
from models                   import *
from sets                     import Set
from nell.tools               import IcalMap
from nell.utilities.TimeAgent import EST, UTC
from nell.utilities           import gen_gbt_schedule, NRAOBosDB
from nell.utilities           import Shelf
from reversion                import revision
from utilities                import *
import pytz

def public_schedule(request, *args, **kws):
    """
    Serves up a version of the GBT schedule fit for general purpose viewing.
    No logon required.

    Note: This view is in either ET or UTC, database is in UTC.
    """
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
        days      = 5
        startDate = datetime.now()

    start    = TimeAgent.truncateDt(startDate)
    end      = start + timedelta(days = days)
    pstart   = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend     = TimeAgent.est2utc(end) if timezone == 'ET' else end

    periods  = [p for p in Period.in_time_range(pstart, pend) \
                if not p.isPending()]
    calendar = gen_gbt_schedule(start, end, days, timezone, periods)

    try:
        tzutc = Shelf()["publish_time"].replace(tzinfo = UTC)
        tz = EST if timezone == 'ET' else UTC
        pubdate = tzutc.astimezone(tz)
    except:
        pubdate = None

    return render_to_response(
               'sesshuns/public_schedule.html'
             , {'calendar' :    sorted(calendar.items())
              , 'day_list' :    range(1, 15)
              , 'tz_list'  :    timezones
              , 'timezone' :    timezone
              , 'start'    :    start
              , 'days'     :    days
              , 'rschedule':    Receiver_Schedule.extract_schedule(start, days)
              , 'timezone' :    timezone
              , 'is_logged_in': request.user.is_authenticated()
              , 'pubdate'  :    pubdate
               })

@revision.create_on_success
@login_required
def home(request, *args, **kwds):
    """
    Serves up the index page for users.
    """
    if get_requestor(request).isOperator():
        return HttpResponseRedirect("/schedule/")
    else:
        return HttpResponseRedirect("/profile")

@login_required
def preferences(request, *args, **kws):
    user = get_requestor(request)
    class PreferencesForm(forms.Form):
        timeZone = forms.ChoiceField(choices = [(tz, tz) for tz in pytz.all_timezones])

    try:
        preferences = user.preference
    except ObjectDoesNotExist:
        preferences = Preference(user = user)
        preferences.save()

    form = PreferencesForm(initial = {'timeZone' : preferences.timeZone})
    if request.method == "POST":
        form = PreferencesForm(request.POST)
        if form.is_valid():
            preferences.timeZone = form.cleaned_data['timeZone']
            preferences.save()
            return HttpResponseRedirect("/profile/%s" % user.id)


    return render_to_response('sesshuns/preferences.html'
                            , {'form' : form
                             , 'u'    : user
                            })

@revision.create_on_success
@login_required
@has_user_access
def profile(request, *args, **kws):
    """
    Shows a user-centric page chock-full of interesting tidbits.
    """
    requestor = get_requestor(request)
    if len(args) > 0:
        user = first(User.objects.filter(id = args[0]))
    else:
        user = requestor

    static_info  = user.getStaticContactInfo(use_cache = False)
    reservations = NRAOBosDB().getReservationsByUsername(user.username
                                                       , use_cache = False)

    try:
        tz = user.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

    blackouts    = user.blackout_set.order_by("start_date")
    return render_to_response("sesshuns/profile.html"
                            , {'u'            : user
                             , 'tz'           : tz
                             , 'blackouts'    : blackouts
                             , 'requestor'    : requestor
                             , 'authorized'   : user == requestor
                             #, 'clients'      : Project.objects.filter(friend=user)
                             , 'emails'       : static_info['emailDescs']
                             , 'phones'       : static_info['phoneDescs']
                             , 'postals'      : static_info['postals']
                             , 'affiliations' : static_info['affiliations']
                             , 'username'     : static_info['username']
                             , 'reserves'     : reservations
                             , 'isOps'        : requestor.isOperator()})

@revision.create_on_success
@login_required
@has_project_access
def project(request, *args, **kws):
    """
    Shows a project-centric page chock-full of interesting tidbits.
    """
    requestor = get_requestor(request)
    project   = first(Project.objects.filter(pcode = args[0]))
    if project is None:
        raise Http404 # Bum pcode

    now          = datetime.utcnow().replace(hour = 0, minute = 0, second = 0)
    later        = now + timedelta(days = 90)
    rcvr_blkouts = []
    for s, e in project.get_receiver_blackout_ranges(now, later):
        if e is None:
            rcvr_blkouts.append((s.date(), None))
        else:
            rcvr_blkouts.append((s.date(), e.date()))

    # sort all the sessions by name
    sess = sorted(project.sesshun_set.all(), lambda x,y: cmp(x.name, y.name))

    return render_to_response(
        "sesshuns/project.html"
      , {'p'           : project
       , 'sess'        : sess
       , 'u'           : requestor
       , 'requestor'   : requestor
       , 'v'           : project.investigator_set.order_by('priority').all()
       , 'r'           : NRAOBosDB().reservations(project)
       , 'rcvr_blkouts': rcvr_blkouts
       }
    )

@revision.create_on_success
@login_required
def search(request, *args, **kws):
    """
    Serves up a page that contains search results.
    """
    search   = request.POST.get('search', '')
    users    = User.objects.filter(
        Q(first_name__icontains = search) | Q(last_name__icontains = search))
    user     = get_requestor(request)
    return render_to_response("sesshuns/search.html"
                            , {'ps'       : project_search(search)
                             , 'us'       : users
                             , 'u'        : user
                             , 'requestor': user
                               })

@revision.create_on_success
@login_required
def toggle_session(request, *args, **kws):
    """
    Allows investigators to enables or disable a session for a project.
    """
    pcode, sname = args
    s = first(Sesshun.objects.filter(project__pcode = pcode, name = sname))
    s.status.enabled = not s.status.enabled
    s.status.save()

    revision.comment = get_rev_comment(request, s, "toggle_session")

    return HttpResponseRedirect("/project/%s" % pcode)

@revision.create_on_success
@login_required
def toggle_observer(request, *args, **kws):
    """
    Allows investigators to designate observers for a project.
    """
    pcode, i_id = args
    i = first(Investigator.objects.filter(project__pcode = pcode, id = i_id))
    i.observer = not i.observer
    i.save()

    project = Project.objects.filter(pcode=pcode)[0]
    project.normalize_investigators()

    revision.comment = get_rev_comment(request, i, "toggle_observer")

    return HttpResponseRedirect("/project/%s" % pcode)

@revision.create_on_success
@login_required
def modify_priority(request, *args, **kws):
    """
    Allows investigators to prioritize observers for a project.
    """
    pcode, i_id, dir = args

    project = Project.objects.filter(pcode = pcode)[0]
    project.normalize_investigators()

    I   = first(project.investigator_set.filter(id = i_id))
    key = 'priority' if dir == "down" else '-priority'
    t   = None
    for i in project.investigator_set.order_by(key):
        if i.observer:
            if t:
                t.priority, i.priority = i.priority, t.priority
                t.save()
                i.save()
                break
            if i == I:
                t = i
    
    revision.comment = get_rev_comment(request, project, "modify_priority")

    return HttpResponseRedirect("/project/%s" % pcode)

@revision.create_on_success
@login_required
@has_project_access
def project_notes(request, *args, **kwds):
    """
    Allows investigators to attach notes to one of their projects.
    """
    pcode,  = args
    project = first(Project.objects.filter(pcode = pcode))
    if project is None:
        raise Http404 # Bum pcode

    if request.method == 'GET':
        return render_to_response("sesshuns/project_notes_form.html"
                                , {'p'        : project
                                 , 'requestor': get_requestor(request)})
    else: # POST
        project.notes = request.POST.get("notes", "")
        project.save()
        revision.comment = get_rev_comment(request, project, "project_notes_save")
        return HttpResponseRedirect("/project/%s" % pcode)

@revision.create_on_success
@login_required
@admin_only
def project_snotes(request, *args, **kwds):
    """
    Allows schedulers to attach a note to a project.
    """
    project = first(Project.objects.filter(pcode = args[0]))
    if project is None:
        raise Http404 # Bum pcode

    if request.method == 'GET':
        return render_to_response("sesshuns/project_snotes_form.html"
                                , {'p'        : project
                                 , 'requestor': get_requestor(request)})
    else: # POST
        project.schedulers_notes = request.POST.get("notes", "")
        project.save()
        revision.comment = get_rev_comment(request, project, "project_snotes_save")
        return HttpResponseRedirect("/project/%s" % args[0])

@revision.create_on_success
@login_required
@has_access
def dynamic_contact(request, *args, **kws):
    """
    Allows investigators to update their dynamic contact information.
    """
    user = first(User.objects.filter(id = args[0]))
    if request.method == 'GET':
        return render_to_response("sesshuns/dynamic_contact_form.html"
                                , {'u':         user
                                 , 'requestor': get_requestor(request)})
    else: # POST
        user.contact_instructions = request.POST.get("contact_instructions", "")
        user.save()
        revision.comment = get_rev_comment(request, user, "dynamic_contact_save")
        return HttpResponseRedirect("/profile/%s" % args[0])

@revision.create_on_success
@login_required
@has_access
def observer_ical(request, *args, **kws):
    """
    Serves up an investigator-centric iCalendar.
    """
    user     = first(User.objects.filter(id = args[0]))
    response = HttpResponse(IcalMap(user).getSchedule())
    response['Content-Type'] = 'text/calendar'
    response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
    return response

@revision.create_on_success
@login_required
@has_access
def blackout(request, *args, **kws):
    """
    Allows investigators to manage blackouts.
    """
    u_id,     = args
    user      = first(User.objects.filter(id = u_id))
    requestor = get_requestor(request)

    if request.method == 'GET':
        b = first(Blackout.objects.filter(id = int(request.GET.get('id', '0'))))
        if request.GET.get('_method', '') == "DELETE":
            b.delete()
            return HttpResponseRedirect("/profile/%s" % u_id)
        else:
            return render_to_response(
                "sesshuns/blackout_form.html"
              , get_blackout_form_context(request.GET.get('_method', '')
                                        , b
                                        , user
                                        , requestor
                                        , []))

    # TBF: Use a django form!
    # Now see if the data to be saved is valid    
    # Convert blackout to UTC.
    utcOffset = first(TimeZone.objects.filter(timeZone = request.POST['tz'])).utcOffset()
    # watch for malformed dates
    start, stError = parse_datetime(request, 'start', 'starttime', utcOffset)
    end,   edError = parse_datetime(request,   'end',   'endtime', utcOffset)
    until, utError = parse_datetime(request, 'until', 'untiltime', utcOffset)
    repeat      = first(Repeat.objects.filter(repeat = request.POST['repeat']))
    description = request.POST['description']
    errors = [e for e in [stError, edError, utError] if e is not None]

    # more error checking!
    # start, end can't be null
    if start is None or end is None:
        errors.append("ERROR: must specify Start and End")
    # start has to be a start, end has to be an end 
    if end is not None and start is not None and end < start:
        errors.append("ERROR: End must be after Start")
    if end is not None and until is not None and until < end:
        errors.append("ERROR: Until must be after End")
    # if it's repeating, we must have an until date
    if repeat.repeat != "Once" and until is None:
        errors.append("ERROR: if repeating, must specify Until")

    # do we need to redirect back to the form because of errors?
    if len(errors) != 0:
         if request.POST.get('_method', '') == 'PUT':
            # go back to editing this pre-existing blackout date
            b = first(Blackout.objects.filter(id = int(request.POST.get('id', 0))))
            return render_to_response("sesshuns/blackout_form.html"
                 , get_blackout_form_context('PUT', b, user, requestor, errors))
         else:
            # go back to creating a new one
            return render_to_response("sesshuns/blackout_form.html"
                 , get_blackout_form_context('', None, user, requestor, errors))
         
    # no errors - retrieve obj, or create new one
    if request.POST.get('_method', '') == 'PUT':
        b = first(Blackout.objects.filter(id = request.POST.get('id', '0')))
    else:
        b = Blackout(user = user)
    b.start_date  = start
    b.end_date    = end
    b.until       = until
    b.repeat      = repeat
    b.description = description
    b.save()
        
    revision.comment = get_rev_comment(request, b, "blackout")

    return HttpResponseRedirect("/profile/%s" % u_id)

@login_required
def events(request, *args, **kws):
    """
    Used by monthly project calendar JavaScript to figure out the happenings
    surrounding a particular project, which include observations, blackouts,
    reservations, trimester boundaries, and windows.
    """
    pcode     = args[0]
    start     = request.GET.get('start', '')
    end       = request.GET.get('end', '')
    project   = first(Project.objects.filter(pcode = pcode).all())

    # Each event needs a unique id.  Let's start with 1.
    id          = 1
    jsonobjlist = []

    # Investigator blackout events
    blackouts = Set([b for i in project.investigator_set.all() \
                       for b in i.user.blackout_set.all()])
    for b in blackouts:
        jsonobjlist.extend(b.eventjson(start, end, id))
        id = id + 1

    # Investigator reservations
    reservations, id = NRAOBosDB().eventjson(project, id)
    jsonobjlist.extend(reservations)

    # Scheduled telescope periods
    for p in project.getPeriods():
        #print w.eventjson(id)
        jsonobjlist.append(p.eventjson(id))
        id = id + 1

    # Semester start dates
    date = datetime.fromtimestamp(float(start))
    for s in Semester.getFutureSemesters(date):
        jsonobjlist.append(s.eventjson(id))
        id = id + 1

    # Scheduled telescope windows
    # TBF trial run, may make calendar too busy
    for w in project.get_windows():
        jsonobjlist.append(w.eventjson(id))
        id = id + 1

    return HttpResponse(json.dumps(jsonobjlist))

@login_required
def dates_not_schedulable(request, *args, **kws):
    """
    Used by monthly project calendar JavaScript to figure out when a
    project cannot observe.
    """
    pcode     = args[0]
    start     = datetime.fromtimestamp(float(request.GET.get('start', '')))
    end       = datetime.fromtimestamp(float(request.GET.get('end', '')))
    project   = first(Project.objects.filter(pcode = pcode).all())
    period    = (end - start).days

    dates = Set([])
    if not project.has_schedulable_sessions():
        dates = dates.union([start + timedelta(days = i) for i in range(period)])
    else:
        dates = dates.union(project.get_blackout_dates(start, end))
        dates = dates.union(project.get_receiver_blackout_dates(start, end))
        dates = dates.union(project.get_prescheduled_days(start, end))

    return HttpResponse(json.dumps([{"start": d.isoformat()} for d in dates]))
