from datetime                       import datetime, time, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts         import render_to_response
from models                   import *
from sets                     import Set
from utilities                import gen_gbt_schedule, UserInfo, NRAOBosDB

def public_schedule(request, *args, **kws):
    # serve up the GBT schedule
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

    start = TimeAgent.truncateDt(startDate)
    end   = start + timedelta(days = days)

    # View is in ET or UTC, database is in UTC.
    pstart  = TimeAgent.est2utc(start) if timezone == 'ET' else start
    pend    = TimeAgent.est2utc(end) if timezone == 'ET' else end
    periods = Period.in_time_range(pstart, pend)

    # ignore pending periods!
    periods = [p for p in periods if p.state.abbreviation != 'P']

    calendar = gen_gbt_schedule(start, end, days, timezone, periods)

    return render_to_response(
               'sesshuns/public_schedule.html'
             , {'calendar' : sorted(calendar.items())
              , 'day_list' : range(1, 15)
              , 'tz_list'  : timezones
              , 'timezone' : timezone
              , 'start'    : start
              , 'days'     : days
              , 'rschedule': Receiver_Schedule.extract_schedule(start, days)
              , 'timezone' : timezone
              , 'is_logged_in': request.user.is_authenticated()})

@login_required
def home(request, *args, **kwds):
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    if requestor.isOperator():
        return HttpResponseRedirect("/schedule/")
    else:
        return HttpResponseRedirect("/profile")

def create_user(username):
    # If the DSS doesn't know about the user, but the User Portal does,
    # then add them to our database so they can at least see their profile.
    info = UserInfo().getStaticContactInfoByUserName(username
                                                   , use_cache = False)
    user = User(pst_id     = info['id']
              , username   = username
              , first_name = info['name']['first-name']
              , last_name  = info['name']['last-name']
              , role       = first(Role.objects.filter(role = "Observer")))
    user.save()
    return user

@login_required
def dates_not_schedulable(request, *args, **kws):
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

@login_required
def events(request, *args, **kws):
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
        jsonobjlist.append(p.eventjson(id))
        id = id + 1

    # Semester start dates
    date = datetime.fromtimestamp(float(start))
    for s in Semester.getFutureSemesters(date):
        jsonobjlist.append(s.eventjson(id))
        id = id + 1

    return HttpResponse(json.dumps(jsonobjlist))

@login_required
def profile(request, *args, **kws):
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    if len(args) > 0:
        u_id,     = args
        user      = first(User.objects.filter(id = u_id))
        #  If the requestor is not the user profile requested and they are
        #  not on the same project redirect to the requestor's profile.
        if user is None or not requestor.canViewUser(user):
            return HttpResponseRedirect("/profile")
    else:
        user = requestor

    static_info  = user.getStaticContactInfo(use_cache = False)
    reservations = NRAOBosDB().getReservationsByUsername(user.username
                                                       , use_cache = False)

    return render_to_response("sesshuns/profile.html"
                            , {'u'            : user
                             , 'requestor'    : requestor
                             , 'authorized'   : user == requestor # allowed to edit
                             #, 'clients'      : Project.objects.filter(friend=user)
                             , 'emails'       : static_info['emails']
                             , 'phones'       : static_info['phones']
                             , 'postals'      : static_info['postals']
                             , 'affiliations' : static_info['affiliations']
                             , 'username'     : static_info['username']
                             , 'reserves'     : reservations
                             , 'isOps'        : requestor.isOperator()})

@login_required
def project(request, *args, **kws):
    loginUser = request.user.username
    user      = first(User.objects.filter(username = loginUser))

    if user is None:
        user = create_user(loginUser)

    pcode,    = args
    #  If the requestor doesn't have access to this, redirect to their profile.
    if not user.canViewProject(pcode):
        return HttpResponseRedirect("/profile")
        
    project = first(Project.objects.filter(pcode = pcode))
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
    sess = sorted(project.sesshun_set.all(),lambda x,y:cmp(x.name,y.name))

    return render_to_response(
        "sesshuns/project.html"
      , {'p'           : project
       , 'sess'        : sess
       , 'u'           : user
       , 'requestor'   : user
       , 'v'           : project.investigator_set.order_by('priority').all()
       , 'r'           : NRAOBosDB().reservations(project)
       , 'rcvr_blkouts': rcvr_blkouts
       }
    )

@login_required
def search(request, *args, **kws):
    loginUser = request.user.username
    user      = first(User.objects.filter(username = loginUser))

    if user is None:
        user = create_user(loginUser)

    search = request.POST.get('search', '')

    projects = Project.objects.filter(
        Q(pcode__icontains = search) | \
            Q(name__icontains = search) | \
            Q(semester__semester__icontains = search.upper()))
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

        if code == search.upper() and p not in projects:
            projects.append(p)

    users = User.objects.filter(
        Q(first_name__icontains = search) | Q(last_name__icontains = search))

    return render_to_response("sesshuns/search.html"
                            , {'ps'       : projects
                             , 'us'       : users
                             , 'u'        : user
                             , 'requestor': user
                               })

@login_required
def toggle_session(request, *args, **kws):
    pcode, sname = args
    s = first(Sesshun.objects.filter(project__pcode = pcode, name = sname))
    s.status.enabled = not s.status.enabled
    s.status.save()
    
    return HttpResponseRedirect("/project/%s" % pcode)

@login_required
def toggle_observer(request, *args, **kws):
    pcode, i_id = args
    i = first(Investigator.objects.filter(project__pcode = pcode, id = i_id))
    i.observer = not i.observer
    i.save()

    project = Project.objects.filter(pcode=pcode)[0]
    project.normalize_investigators()
    
    return HttpResponseRedirect("/project/%s" % pcode)

@login_required
def modify_priority(request, *args, **kws):
    pcode, i_id, dir = args
    project = Project.objects.filter(pcode=pcode)[0]
    project.normalize_investigators()
    I = first(project.investigator_set.filter(id = i_id))
    key = 'priority' if dir == "down" else '-priority'
    t = None
    for i in project.investigator_set.order_by(key):
        if i.observer:
            if t:
                t.priority, i.priority = i.priority, t.priority
                t.save()
                i.save()
                break
            if i == I:
                t = i
    
    return HttpResponseRedirect("/project/%s" % pcode)

@login_required
def project_notes_form(request, *args, **kwds):
    pcode, = args

    # TBF Use a decorator
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    #  If the requestor doesn't have access to this, redirect to their profile.
    if not requestor.canViewProject(pcode):
        return HttpResponseRedirect("/profile")

    project = first(Project.objects.filter(pcode = pcode))
    if project is None:
        raise Http404 # Bum pcode

    return render_to_response("sesshuns/project_notes_form.html"
                            , {'p'        : project
                             , 'requestor': requestor})

@login_required
def project_notes_save(request, *args, **kws):
    pcode, = args

    # TBF Use a decorator
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    #  If the requestor doesn't have access to this, redirect to their profile.
    if not requestor.canViewProject(pcode):
        return HttpResponseRedirect("/profile")

    project = first(Project.objects.filter(pcode = pcode))
    if project is None:
        raise Http404 # Bum pcode

    project.notes = request.POST.get("notes", "")
    project.save()

    return HttpResponseRedirect("/project/%s" % pcode)

@login_required
def project_snotes_form(request, *args, **kwds):
    pcode, = args

    # TBF Use a decorator
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    #  If the requestor doesn't have access to this, redirect to the project.
    if not requestor.isAdmin():
        return HttpResponseRedirect("/project/%s" % pcode)

    project = first(Project.objects.filter(pcode = pcode))
    if project is None:
        raise Http404 # Bum pcode

    return render_to_response("sesshuns/project_snotes_form.html"
                            , {'p'        : project
                             , 'requestor': requestor})

@login_required
def project_snotes_save(request, *args, **kws):
    pcode, = args

    # TBF Use a decorator
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    #  If the requestor doesn't have access to this, redirect to the project.
    if not requestor.isAdmin():
        return HttpResponseRedirect("/project/%s" % pcode)

    project = first(Project.objects.filter(pcode = pcode))
    if project is None:
        raise Http404 # Bum pcode

    project.schedulers_notes = request.POST.get("notes", "")
    project.save()

    return HttpResponseRedirect("/project/%s" % pcode)

@login_required
def dynamic_contact_form(request, *args, **kws):
    u_id,     = args
    user      = first(User.objects.filter(id = u_id))

    # TBF Use a decorator
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    return render_to_response("sesshuns/dynamic_contact_form.html"
                            , {'u'        : user
                             , 'requestor': requestor})

@login_required
def dynamic_contact_save(request, *args, **kws):
    u_id, = args
    user  = first(User.objects.filter(id = u_id))

    # TBF Use a decorator
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    user = first(User.objects.filter(id = u_id))
    user.contact_instructions = request.POST.get("contact_instructions", "")
    user.save()

    return HttpResponseRedirect("/profile/%s" % u_id)

@login_required
def blackout_form(request, *args, **kws):
    u_id,     = args
    loginUser = request.user.username
    user      = first(User.objects.filter(id = u_id))
    requestor = first(User.objects.filter(username = loginUser))

    # TBF Use a decorator to see if user is allowed here
    if requestor is None:
        requestor = create_user(loginUser)

    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    method = request.GET.get('_method', '')
    b = first(Blackout.objects.filter(id = int(request.GET.get('id', 0))))

    return render_to_response(
        "sesshuns/blackout_form.html"
      , get_blackout_form_context(method, b, user, requestor, [])
    )

def get_blackout_form_context(method, blackout, user, requestor, errors):
    "Returns dictionary for populating blackout form"
    return {
        'u'        : user
      , 'requestor': requestor
      , 'method'   : method
      , 'b'        : blackout # b's dates in DB are UTC
      , 'tzs'      : TimeZone.objects.all()
      , 'timezone' : 'UTC' # form always starts at UTC
      , 'repeats'  : Repeat.objects.all()
      , 'times'    : [time(h, m).strftime("%H:%M") \
                      for h in range(0, 24) for m in range(0, 60, 15)]
      , 'errors'   : errors
    }

def parse_datetime(request, dateName, timeName, utcOffset):
    "Extract the date & time from the form values to make a datetime obj"
    dt    = None
    error = None
    try:
        if request.POST[dateName] != '':
            dt = datetime.strptime(
                "%s %s" % (request.POST[dateName], request.POST[timeName])
              , "%m/%d/%Y %H:%M") + utcOffset
    except:
        error = "ERROR: malformed %s date" % dateName
    return (dt, error)    
 
@login_required
def blackout(request, *args, **kws):
    u_id, = args

    if request.method == 'GET': # This method is only good for POSTs.
        return HttpResponseRedirect("/profile/%s" % u_id)

    # TBF Use a decorator to see if user can view this page
    user      = first(User.objects.filter(id = u_id))
    loginUser = request.user.username
    requestor = first(User.objects.filter(username = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    # if we're deleting this black out, get it over with
    if request.GET.get('_method', '') == "DELETE":
        b = first(Blackout.objects.filter(
                id = int(request.GET.get('id', '0'))))
        b.delete()
        return HttpResponseRedirect("/profile/%s" % u_id)
        
    # TBF: is this error checking so ugly because we aren't using
    # a Django form object?
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
        
    return HttpResponseRedirect("/profile/%s" % u_id)
