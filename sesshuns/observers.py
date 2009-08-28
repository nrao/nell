from datetime                       import datetime, date, time
from django.contrib.auth.decorators import login_required
from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import render_to_response
from models                   import *
from utilities                import UserInfo
from utilities                import NRAOBosDB

def calendar(request, *args, **kws):
    pcode, year, month, day = args
    
    return render_to_response("sesshuns/overview.html"
                            , {'today' : date(int(year), int(month), int(day))
                             , 'weeks' : range(6)
                             , 'days'  : range(7)
                             , 'p'     : first(Project.objects.filter(pcode = pcode))
                               }
                              )

@login_required
def profile(request, *args, **kws):
    loginUser = request.user.username
    if len(args) > 0:
        u_id,     = args
        user      = first(User.objects.filter(id = u_id))
        projects  = [i.project.pcode for i in user.investigators_set.all()]
        requestor = first(User.objects.filter(username = loginUser))
        union     = [i.project.pcode for i in requestor.investigators_set.all()
                        if i.project.pcode in projects]
        #  If the requestor is not the user profile requested and they are
        #  not on the same project redirect to the requestor's profile.
        if union == [] and user != requestor and not requestor.isAdmin():
            return HttpResponseRedirect("/profile")
    else:
        requestor = first(User.objects.filter(username = loginUser))
        user      = requestor
        
    # get the users' info from the PST
    ui = UserInfo()
    try:
        # TBF: use user's credentials to get past CAS, not Mr. Nubbles!
        info = ui.getProfileByID(user, 'dss', 'MrNubbles!')
    except:
        # we really should only see this during unit tests.
        print "encountered excpetion w/ UserInfo and user: ", user
        info = dict(emails = [e.email for e in user.email_set.all()]
                  , phones = ['Not Available']
                  , postals = ['Not Available']
                  , username = user.username)
        
    # get the reservations information from BOS
    bos = NRAOBosDB()
    reservations = bos.getReservationsByUsername(user.username)

    # Remember [] is False,  TBF is this needed?
    isFriend = ["yep" for p in user.investigators_set.all() if p.friend]
    return render_to_response("sesshuns/profile.html"
                            , {'u'          : user
                             , 'requestor'  : requestor
                             , 'authorized' : user == requestor # allowed to edit
                             , 'isFriend'   : isFriend
                             , 'emails'     : info['emails']
                             , 'phones'     : info['phones']
                             , 'postals'    : info['postals']
                             , 'username'   : info['username']
                             , 'reserves'   : reservations
                               })

@login_required
def project(request, *args, **kws):
    bos = NRAOBosDB()
    loginUser = request.user.username
    user   = first(User.objects.filter(username = loginUser))
    pcode, = args
    #  If the requestor is not on this project redirect to their profile.
    if pcode not in [i.project.pcode for i in user.investigators_set.all()] \
            and not user.isAdmin():
        return HttpResponseRedirect("/profile")
        
    project = first(Project.objects.filter(pcode = pcode))
    return render_to_response("sesshuns/project.html"
                            , {'p' : project
                             , 'u' : user
                             , 'r' : bos.reservations(project)
                               })

@login_required
def search(request, *args, **kws):
    loginUser = request.user.username
    user   = first(User.objects.filter(username = loginUser))
    search   = request.POST.get('search', '')
    projects = Project.objects.filter(
        Q(pcode__icontains = search) | \
            Q(name__icontains = search) | \
            Q(semester__semester__icontains = search))
    users    = User.objects.filter(
        Q(first_name__icontains = search) | Q(last_name__icontains = search))
    return render_to_response("sesshuns/search.html"
                            , {'ps' : projects
                             , 'us' : users
                             , 'u'  : user
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
    i = first(Investigators.objects.filter(project__pcode = pcode, id = i_id))
    i.observer = not i.observer
    i.save()
    
    return HttpResponseRedirect("/project/%s" % pcode)

@login_required
def dynamic_contact_form(request, *args, **kws):
    loginUser = request.user.username
    u_id,     = args
    user      = first(User.objects.filter(id = u_id))

    # TBF Use a decorator
    requestor = first(User.objects.filter(username = loginUser))
    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    return render_to_response("sesshuns/dynamic_contact_form.html"
                            , {'u': user})

@login_required
def dynamic_contact_save(request, *args, **kws):
    u_id, = args
    user = first(User.objects.filter(id = u_id))
    user.contact_instructions = request.POST.get("contact_instructions", "")
    user.save()
    return HttpResponseRedirect("/profile/%s" % u_id)

@login_required
def blackout_form(request, *args, **kws):
    loginUser = request.user.username
    method = request.GET.get('_method', '')
    u_id, = args
    user  = first(User.objects.filter(id = u_id))

    # TBF Use a decorator
    requestor = first(User.objects.filter(username = loginUser))
    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    b     = first(Blackout.objects.filter(id = int(request.GET.get('id', 0))))
    times = [time(h, m).strftime("%H:%M")
             for h in range(0, 24) for m in range(0, 60, 15)]
    return render_to_response("sesshuns/blackout_form.html"
                            , {'method' : method
                             , 'b'      : b
                             , 'u'      : user
                             , 'tzs'    : TimeZone.objects.all()
                             , 'repeats': Repeat.objects.all()
                             , 'times'  : times
                               })

@login_required
def blackout(request, *args, **kws):
    loginUser = request.user.username
    u_id, = args
    user = first(User.objects.filter(id = u_id))

    # TBF Use a decorator
    requestor = first(User.objects.filter(username = loginUser))
    if user != requestor and not requestor.isAdmin():
        return HttpResponseRedirect("/profile")

    if request.GET.get('_method', '') == "DELETE":
        b = first(Blackout.objects.filter(
                id = int(request.GET.get('id', '0'))))
        b.delete()
        return HttpResponseRedirect("/profile/%s" % u_id)
        
    if request.POST.get('_method', '') == 'PUT':
        b = first(Blackout.objects.filter(id = request.POST.get('id', '0')))
    else:
        b = Blackout(user = user)

    if request.POST['start'] != '':
        b.start       = datetime.strptime(
            "%s %s" % (request.POST['start'], request.POST['starttime'])
          , "%m/%d/%Y %H:%M")
    if request.POST['end'] != '':
        b.end         = datetime.strptime(
            "%s %s" % (request.POST['end'], request.POST['endtime'])
          , "%m/%d/%Y %H:%M")
    b.tz          = first(TimeZone.objects.filter(timeZone = request.POST['tz']))
    b.repeat      = first(Repeat.objects.filter(repeat = request.POST['repeat']))
    if request.POST['until'] != '':
        b.until       = datetime.strptime(
            "%s %s" % (request.POST['until'], request.POST['untiltime'])
          , "%m/%d/%Y %H:%M")
    b.description = request.POST['description']
    b.save()
        
    return HttpResponseRedirect("/profile/%s" % u_id)
