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

from datetime                       import datetime, time, timedelta
from decorators                     import *
from django.contrib.auth.decorators import login_required
from django.db.models               import Q
from django.core.exceptions         import ObjectDoesNotExist
from django.http                    import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts               import render_to_response, get_object_or_404
from scheduler.utilities            import get_rev_comment
from models                         import *
from scheduler.httpadapters         import EventJson
from nell.tools                     import IcalMap
from nell.utilities.TimeAgent       import EST, UTC, adjustDateTimeTz
from reversion                      import revision
from utilities                      import *
from forms                          import BlackoutForm, PreferencesForm

import pytz
import simplejson as json

def public_schedule(request, *args, **kws):
    """
    Serves up a version of the GBT schedule fit for general purpose viewing.
    No logon required.

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
    # impossible for the user to send us malformed params.

    data      = request.POST if request.method == 'POST' else request.GET
    timezone  = data.get('tz', 'ET')
    days      = int(data.get('days', 5))    
    startDate = cleanSD(data.get('start', None) )

    start    = TimeAgent.truncateDt(startDate)
    end      = start + timedelta(days = days)
    pstart   = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend     = TimeAgent.est2utc(end) if timezone == 'ET' else end

    schedule = get_gbt_schedule_events(start, end, timezone)

    try:
        s_n = Schedule_Notification.objects.all()
        tzutc = s_n[len(s_n)-1].date.replace(tzinfo=UTC)
        tz = EST if timezone == 'ET' else UTC
        pubdate = tzutc.astimezone(tz)
    except:
        pubdate = None

    if len(args) == 1:
        printerFriendly, = args
    else:
        printerFriendly = None
    template = 'users/schedules/public_schedule_friendly.html' if printerFriendly == 'printerFriendly' \
                   else 'users/public_schedule.html'
    # day range of the public schedule               
    day_list = range(1,15)
    day_list.append(30)
    return render_to_response(
                template
              , {'calendar'     :    schedule
              , 'day_list'     :    day_list
              , 'tz_list'      :    timezones
              , 'timezone'     :    timezone
              , 'start'        :    start
              , 'startFmt'     :    start.strftime('%m/%d/%Y')
              , 'days'         :    days
              , 'rschedule'    :    Receiver_Schedule.extract_schedule(start, days)
              , 'timezone'     :    timezone
              , 'is_logged_in' : request.user.is_authenticated()
              , 'pubdate'      :    pubdate
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

    return render_to_response('users/preferences.html'
                            , {'form' : form
                             , 'u'    : user
                            })

def adjustBlackoutTZ(tz, blackout):
    """
    Takes a Blackout object and converts the datetimes from UTC to
    'tz'.
    """
    return {'user'        : blackout.user # None for project blackouts
          , 'id'          : blackout.id
          , 'start_date'  : blackout.getStartDateTZ(tz)
          , 'end_date'    : blackout.getEndDateTZ(tz)
          , 'repeat'      : blackout.getRepeat()
          , 'until'       : blackout.getUntilTZ(tz)
          , 'description' : blackout.getDescription()
           }

@revision.create_on_success
@login_required
@has_user_access
def profile(request, *args, **kws):
    """
    Shows a user-centric page chock-full of interesting tidbits.
    """
    requestor = get_requestor(request)
    requestor.checkAuthUser()
    user = User.objects.get(id = args[0]) if args else requestor
    static_info  = user.getStaticContactInfo()
    reservations = user.getReservations()

    try:
        tz = requestor.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

    blackouts = \
        sorted([{'user'        : user
                 , 'id'          : b.id
                 , 'start_date'  : adjustDateTimeTz(tz, b.getStartDate())
                 , 'end_date'    : adjustDateTimeTz(tz, b.getEndDate())
                 , 'repeat'      : b.getRepeat()
                 , 'until'       : adjustDateTimeTz(tz, b.getUntil())
                 , 'description' : b.getDescription()
                 } for b in user.blackout_set.all() if b.isActive()],
               key = lambda  bl: bl['start_date'])



    upcomingPeriods = [(proj
                       , [{'session'  : pd.session
                         , 'start'    : adjustDateTimeTz(tz, pd.start)
                         , 'duration' : pd.duration
                          } for pd in pds]
                         ) for proj, pds in user.getUpcomingPeriodsByProject().items()]
    return render_to_response("users/profile.html"
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

def project_public(request, *args, **kws):
    project       = get_object_or_404(Project, pcode = args[0])
    investigators = project.investigator_set.order_by('priority').all()
    for i in investigators:
        i.user.loadStaticContactInfo()

    return render_to_response(
        "users/project_public.html"
      , {'project'       : project
       , 'abstract'      : None if project.abstract == '' else project.abstract
       , 'investigators' : investigators
         })

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

    project   = get_object_or_404(Project, pcode = args[0])

    now          = datetime.utcnow().replace(hour = 0, minute = 0, second = 0)
    later        = now + timedelta(days = 180)
    rcvr_blkouts = []
    for s, e in project.get_receiver_blackout_ranges(now, later):
        if e is None:
            rcvr_blkouts.append((s.date(), None))
        else:
            rcvr_blkouts.append((s.date(), e.date()))

    # sort all the sessions by name
    sess = sorted(project.sesshun_set.all(), lambda x,y: cmp(x.name, y.name))

    # what are the user blackouts we need to display?
    investigators = project.investigator_set.order_by('priority').all()
    obsBlackouts      = [adjustBlackoutTZ(tz, b) for i in investigators for b in i.projectBlackouts()]
    reqFriendBlackouts = [adjustBlackoutTZ(tz, b) for f in project.friend_set.all() for b in f.projectBlackouts() if f.required ]

    # prevent duplicates when adding required friend's blackouts:
    for ob in reqFriendBlackouts:
        if ob not in obsBlackouts:
            obsBlackouts.append(ob)

    # and the project blackouts?
    projBlackouts     = [adjustBlackoutTZ(tz, b) for b in project.blackout_set.all() if b.isActive()]

    periods = [{'session'    : p.session
              , 'start'      : adjustDateTimeTz(tz, p.start)
              , 'duration'   : p.duration
              , 'accounting' : p.accounting
               } for p in project.get_observed_periods()]
    windows = [{'session'   : w.session
              , 'start_date' : w.start_date()
              , 'duration'   : w.duration()
              , 'last_date'  : w.last_date()
              , 'total_time'  : w.total_time
              , 'time_billed' : w.timeBilled()
              , 'complete'    : w.complete
              , 'contigious'  : w.isContigious()
              , 'ranges'      : [{'start' : wr.start_date
                                , 'duration' : wr.duration
                                , 'end' : wr.last_date()} \
                                for wr in w.ranges()]
              , 'periods'     : [{'start' : adjustDateTimeTz(tz, p.start)
                                , 'duration' : p.duration
                                , 'time_billed' : p.accounting.time_billed()} \
                                    for p in w.scheduledPeriods()]
               } for w in project.get_active_windows()]
    upcomingPeriods = [{'session'  : pd.session
                      , 'start'    : adjustDateTimeTz(tz, pd.start)
                      , 'duration' : pd.duration
                       } for pd in project.getUpcomingPeriods()]
    electivePeriods = [ {'elective' : e
                       , 'periods' : [{'start' : adjustDateTimeTz(tz, p.start)
                                     , 'duration' : p.duration
                                     , 'scheduled' : "Yes" if p.isScheduled() else ""
                                     , 'time_billed' : p.accounting.time_billed()} \
                                    for p in e.periodsOrderByDate()]
                        } for e in project.getActiveElectives()]
    res = project.getUpcomingReservations()
    return render_to_response(
        "users/project.html"
      , {'p'                 : project
       , 'sess'              : sess
       , 'u'                 : requestor
       , 'requestor'         : requestor
       , 'v'                 : investigators
       , 'r'                 : res
       , 'rcvr_blkouts'      : rcvr_blkouts
       , 'tz'                : tz
       , 'observerBlackouts' : obsBlackouts
       , 'projectBlackouts'  : projBlackouts
       , 'periods'           : periods
       , 'windows'           : windows
       , 'upcomingPeriods'   : upcomingPeriods
       , 'electivePeriods'   : electivePeriods
       , 'tzs'               : pytz.common_timezones
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
    return render_to_response("users/search.html"
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
    s = Sesshun.objects.get(project__pcode = pcode, id = sid)
    s.status.enabled = not s.status.enabled
    s.status.save()

    revision.comment = get_rev_comment(request, s, "toggle_session")

    return HttpResponse(
            json.dumps({"success" :   "ok"})
          , mimetype = "text/plain")

@revision.create_on_success
@login_required
def toggle_required_friend(request, *args, **kws):
    """
    Allows investigators to designate required friends for a project.
    """
    pcode, f_id = args
    f = Friend.objects.get(project__pcode = pcode, id = f_id)
    f.required = not f.required
    f.save()

    revision.comment = get_rev_comment(request, f, "toggle_required_friend")

    return HttpResponse(
            json.dumps({"success" :   "ok"})
          , mimetype = "text/plain")

@revision.create_on_success
@login_required
def toggle_observer(request, *args, **kws):
    """
    Allows investigators to designate observers for a project.
    """
    pcode, i_id = args
    i = Investigator.objects.get(project__pcode = pcode, id = i_id)
    i.observer = not i.observer
    i.save()

    project = Project.objects.filter(pcode=pcode)[0]
    project.normalize_investigators()

    revision.comment = get_rev_comment(request, i, "toggle_observer")

    return HttpResponse(
            json.dumps({"success" :   "ok"})
          , mimetype = "text/plain")

@revision.create_on_success
@login_required
def modify_priority(request, *args, **kws):
    """
    Allows investigators to prioritize observers for a project.
    """
    pcode, i_id, dir = args

    project = Project.objects.filter(pcode = pcode)[0]
    project.normalize_investigators()

    I   = project.investigator_set.get(id = i_id)
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
    project = get_object_or_404(Project, pcode = pcode)

    if request.method == 'GET':
        return render_to_response("users/project_notes_form.html"
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
    project = get_object_or_404(Project, pcode = args[0])

    if request.method == 'GET':
        return render_to_response("users/project_snotes_form.html"
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
    user = User.objects.get(id = args[0])
    if request.method == 'GET':
        return render_to_response("users/dynamic_contact_form.html"
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
    user     = User.objects.get(id = args[0])
    response = HttpResponse(IcalMap(user).getSchedule(), mimetype='text/calendar')
    response['Content-Type'] = 'text/calendar'
    response['Content-Disposition'] = 'attachment; filename=GBTschedule.ics'
    return response

@revision.create_on_success
@login_required
@has_project_access
def project_blackout(request, *args, **kws):
    """
    Allows investigators to manage project blackouts.
    """
    if len(args) == 1:
        p_id, = args
        b_id  = None
    else:
        p_id, b_id, = args

    project   = Project.objects.get(pcode = p_id)
    requestor = get_requestor(request)

    return blackout_worker(request
                         , "project_blackout"
                         , project
                         , b_id
                         , requestor
                         , "/project/%s" % p_id) # urlRedirect

@revision.create_on_success
@login_required
@has_access
def user_blackout(request, *args, **kws):
    """
    Allows investigators to manage user blackouts.
    """
    if len(args) == 1:
        u_id, = args
        b_id  = None
    else:
        u_id, b_id, = args
        blackout = Blackout.objects.get(id = b_id)

    user      = User.objects.get(id = u_id)
    requestor = get_requestor(request)

    return blackout_worker(request
                         , "user_blackout"
                         , user
                         , b_id
                         , requestor
                         , "/profile/%s" % u_id) # urlRedirect

def blackout_worker(request, kind, forObj, b_id, requestor, urlRedirect):
    "Does most of the work for processing blackout forms"

    try:
        # use the requestor's time zone preference - not the users,
        # since this could be for a project blackout.
        tz = requestor.preference.timeZone
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
                b = Blackout.objects.get(id = b_id)
            else:
                if kind == "project_blackout":
                    b = Blackout(project = forObj)
                else:
                    b = Blackout(user = forObj)

            b.initialize(tzp, f.cleaned_start, f.cleaned_end, f.cleaned_data['repeat'],
                         f.cleaned_until, f.cleaned_data['description'])
            revision.comment = get_rev_comment(request, b, "blackout")
            return HttpResponseRedirect(urlRedirect)
    else:
        b = Blackout.objects.get(id = b_id) if b_id is not None else None

        if request.GET.get('_method', '') == "DELETE" and b is not None:
            b.delete()
            return HttpResponseRedirect(urlRedirect)

        f = BlackoutForm.initialize(b, tz) if b is not None else BlackoutForm()

    blackoutUrl = "%d/" % int(b_id) if b_id is not None else ""
    # the forms we render have different actions according to whether
    # these blackouts are for users or projects
    if kind == "project_blackout":
        for_name = forObj.pcode
        form_action = "/project/%s/blackout/%s" % (forObj.pcode, blackoutUrl)
        cancel_action =  "/project/%s" % forObj.pcode
    else:
        for_name = forObj.display_name()
        form_action = "/profile/%d/blackout/%s" % (forObj.id, blackoutUrl)
        cancel_action =  "/profile/%d" % forObj.id

    return render_to_response("users/blackout_form.html"
                            , {'form'      : f
                             , 'b_id'      : b_id
                             , 'action'    : form_action
                             , 'cancel'    : cancel_action
                             , 'for_name'  : for_name
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
    project   = Project.objects.get(pcode = pcode)
    requestor = get_requestor(request)

    try:
        tz = requestor.preference.timeZone
    except ObjectDoesNotExist:
        tz = "UTC"

    ej = EventJson()

    jsonobjlist = ej.getEvents(project, start, end, tz)

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
    past      = 'True' == request.GET.get('past', 'False')
    project   = Project.objects.get(pcode = pcode)
    period    = (end - start).days

    dates = set([])
    if not project.has_schedulable_sessions():
        # it doesn't matter, all dates are all unavailable
        dates = dates.union([start + timedelta(days = i) for i in range(period)])
    else:
        # it does depend on the time.  Do we need to bother with the past?
        if not past:
            now = datetime.today()
            today = datetime(now.year, now.month, now.day)
            s = max(start, today)
            e = max(end,   today)
        else:
            s = start
            e = end
        dates = dates.union(project.get_blackout_dates(s, e))
        dates = dates.union(project.get_receiver_blackout_dates(s, e))
        # NOTE: use static method optimization
        #dates = dates.union(project.get_prescheduled_days(s, e))
        dates = dates.union(Period.get_prescheduled_days(s, e
             , project = project))


    return HttpResponse(json.dumps([{"start": d.isoformat()} for d in dates]))

@login_required
def not_schedulable_details(request, *args, **kws):
    """
    Used by monthly project calendar JavaScript to figure out why a
    project cannot observe on a particular date.
    """
    pcode     = args[0]
    date     = datetime.fromtimestamp(float(request.GET.get('date', '')))
    project   = Project.objects.get(pcode = pcode)
    # construct dict of reasons why it's unavailable
    dct = {"pcode": pcode
         , "date": date.strftime("%Y-%m-%d")
         , "no_enabled_sessions" : not project.has_enabled_sessions()
         , "no_authorized_sessions" : not project.has_authorized_sessions()
         , "no_incomplete_sessions" : not project.has_incomplete_sessions()
         , "project_complete" : project.complete
         , "no_receivers" : project.day_has_rcvrs_unavailable(date) 
         , "blackedout" : project.day_is_blackedout(date) 
         # NOTE: use static method optimization
         #, "prescheduled" : project.day_is_prescheduled(date) 
         , "prescheduled" : Period.day_is_prescheduled(date
                                                     , project = project) 
          }
    return HttpResponse(json.dumps(dct))
    
