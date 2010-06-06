from datetime                       import datetime, time, timedelta
from decorators                     import *
from django.contrib.auth.decorators import login_required
from django.db.models               import Q
from django.core.exceptions         import ObjectDoesNotExist
from django.http                    import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response
from models                         import *
from sets                           import Set
from nell.tools                     import IcalMap
from nell.utilities.TimeAgent       import EST, UTC, adjustDateTimeTz
from nell.utilities                 import gen_gbt_schedule, NRAOBosDB
from nell.utilities                 import Shelf
from reversion                      import revision
from utilities                      import *
from forms                          import BlackoutForm, PreferencesForm
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

def adjustBlackoutTZ(tz, blackout):
    return {'user'        : blackout.user
          , 'id'          : blackout.id
          , 'start_date'  : adjustDateTimeTz(tz, blackout.start_date)
          , 'end_date'    : adjustDateTimeTz(tz, blackout.end_date)
          , 'repeat'      : blackout.repeat
          , 'until'       : adjustDateTimeTz(tz, blackout.until)
          , 'description' : blackout.description
           }

@revision.create_on_success
@login_required
@has_user_access
def profile(request, *args, **kws):
    """
    Shows a user-centric page chock-full of interesting tidbits.
    """
    requestor = get_requestor(request)
    user = first(User.objects.filter(id = args[0])) if args else requestor
    static_info  = user.getStaticContactInfo()
    reservations = NRAOBosDB().getReservationsByUsername(user.username)

    try:
        tz = requestor.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

    blackouts    = [{'user'        : user
                   , 'id'          : b.id
                   , 'start_date'  : adjustDateTimeTz(tz, b.start_date)
                   , 'end_date'    : adjustDateTimeTz(tz, b.end_date)
                   , 'repeat'      : b.repeat
                   , 'until'       : adjustDateTimeTz(tz, b.until)
                   , 'description' : b.description
                    } for b in user.blackout_set.order_by("start_date") \
                      if b.isActive()]

    upcomingPeriods = [(proj
                       , [{'session'  : pd.session
                         , 'start'    : adjustDateTimeTz(tz, pd.start)
                         , 'duration' : pd.duration
                          } for pd in pds]
                         ) for proj, pds in user.getUpcomingPeriodsByProject().items()]
    return render_to_response("sesshuns/profile.html"
                            , {'u'            : user
                             , 'blackouts'    : blackouts
                             , 'requestor'    : requestor
                             , 'authorized'   : user == requestor
                             , 'tz'           : tz
                             , 'emails'       : static_info['emailDescs']
                             , 'phones'       : static_info['phoneDescs']
                             , 'postals'      : static_info['postals']
                             , 'affiliations' : static_info['affiliations']
                             , 'username'     : static_info['username']
                             , 'reservations' : reservations
                             , 'upcomingPeriods' : upcomingPeriods
                             , 'tzs'             : pytz.common_timezones
                             , 'isOps'           : requestor.isOperator()})

@revision.create_on_success
@login_required
@has_project_access
def project(request, *args, **kws):
    """
    Shows a project-centric page chock-full of interesting tidbits.
    """
    requestor = get_requestor(request)
    try:
       tz = requestor.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

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

    investigators = project.investigator_set.order_by('priority').all()
    blackouts     = [adjustBlackoutTZ(tz, b) for i in investigators for b in i.projectBlackouts()]
    periods = [{'session'    : p.session
              , 'start'      : adjustDateTimeTz(tz, p.start)
              , 'duration'   : p.duration
              , 'accounting' : p.accounting
               } for p in project.get_observed_periods()]
    windows = [{'session'   : w.session
              , 'start_date' : w.start_date
              , 'duration'   : w.duration
              , 'is_scheduled_or_completed' : {'start' : adjustDateTimeTz(tz, w.is_scheduled_or_completed().start)
                                             , 'duration' : w.is_scheduled_or_completed().duration
                                               } if w.is_scheduled_or_completed() is not None else None
               } for w in project.get_active_windows()]
    upcomingPeriods = [{'session'  : pd.session
                      , 'start'    : adjustDateTimeTz(tz, pd.start)
                      , 'duration' : pd.duration
                       } for pd in project.getUpcomingPeriods()]
    return render_to_response(
        "sesshuns/project.html"
      , {'p'           : project
       , 'sess'        : sess
       , 'u'           : requestor
       , 'requestor'   : requestor
       , 'v'           : investigators
       , 'r'           : NRAOBosDB().reservations(project)
       , 'rcvr_blkouts': rcvr_blkouts
       , 'tz'          : tz
       , 'projectBlackouts' : blackouts
       , 'periods'          : periods
       , 'windows'          : windows
       , 'upcomingPeriods'  : upcomingPeriods
       , 'tzs'              : pytz.common_timezones
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
    pcode, sid = args
    s = first(Sesshun.objects.filter(project__pcode = pcode, id = sid))
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

def observer_ical(request, *args, **kws):
    """
    Serves up an investigator-centric iCalendar.
    """
    user     = first(User.objects.filter(id = args[0]))
    response = HttpResponse(IcalMap(user).getSchedule(), mimetype='text/calendar')
    response['Content-Type'] = 'text/calendar'
    response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
    return response

@login_required
@has_access
def clear_user_cache(request, *args, **kwds):
    user = first(User.objects.filter(id = args[0]))
    user.clearCachedInfo()
    return HttpResponseRedirect("/profile/%s" % args[0])
 
@revision.create_on_success
@login_required
@has_access
def blackout(request, *args, **kws):
    """
    Allows investigators to manage blackouts.
    """
    if len(args) == 1:
        u_id, = args
        b_id  = None
    else:
        u_id, b_id, = args

    user      = first(User.objects.filter(id = u_id))
    requestor = get_requestor(request)

    try:
        tz = user.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

    tz_form = PreferencesForm(initial = {'timeZone' : tz})

    if request.method == 'POST':
        tz_form = PreferencesForm(request.POST)
        if tz_form.is_valid():
            tzp = tz_form.cleaned_data['timeZone']
        else:
            tz_form = PreferencesForm()
            tzp = tz
        f = BlackoutForm(request.POST)
        f.format_dates(tzp, request.POST)
        if f.is_valid():
            if request.POST.get('_method', '') == 'PUT':
                b = first(Blackout.objects.filter(id = b_id))
            else:
                b = Blackout(user = user)

            b.start_date  = f.cleaned_start
            b.end_date    = f.cleaned_end
            b.until       = f.cleaned_until
            b.repeat      = f.cleaned_data['repeat']
            b.description = f.cleaned_data['description']
            b.save()
        
            revision.comment = get_rev_comment(request, b, "blackout")
            return HttpResponseRedirect("/profile/%s" % u_id)
    else:
        b = first(Blackout.objects.filter(id = b_id)) if b_id is not None else None
        if request.GET.get('_method', '') == "DELETE" and b is not None:
            b.delete()
            return HttpResponseRedirect("/profile/%s" % u_id)

        f = BlackoutForm.initialize(b, tz) if b is not None else BlackoutForm()

    return render_to_response("sesshuns/blackout_form.html"
                            , {'form'      : f
                             , 'requestor' : requestor
                             , 'u'         : user
                             , 'b_id'      : b_id
                             , 'tz'        : tz
                             , 'tz_form'   : tz_form
                             })

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
    requestor = get_requestor(request)

    try:
        tz = requestor.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

    # Each event needs a unique id.  Let's start with 1.
    id          = 1
    jsonobjlist = []

    # Investigator blackout events
    blackouts = Set([b for i in project.investigator_set.all() \
                       for b in i.user.blackout_set.all()])
    for b in blackouts:
        jsonobjlist.extend(b.eventjson(start, end, id, tz))
        id = id + 1

    # Investigator reservations
    reservations, id = NRAOBosDB().eventjson(project, id)
    jsonobjlist.extend(reservations)

    # Scheduled telescope periods
    for p in project.getPeriods():
        jsonobjlist.append(p.eventjson(id, tz))
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
