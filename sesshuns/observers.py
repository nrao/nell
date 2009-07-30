from datetime                 import datetime, time
from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import render_to_response
from models                   import *

def profile(request, *args, **kws):
    u_id, = args
    user = first(User.objects.filter(id = u_id))
    return render_to_response("sesshuns/profile.html"
                            , {'u': user})

def project(request, *args, **kws):
    # TBF: get the currently logged in user
    user = first(User.objects.filter(last_name = "Braatz"))
    pcode, = args
    project = first(Project.objects.filter(pcode = pcode))
    return render_to_response("sesshuns/project.html"
                            , {'p' : project
                             , 'u' : user
                               })

def search(request, *args, **kws):
    # TBF: get the currently logged in user
    user = first(User.objects.filter(last_name = "Braatz"))
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

def toggle_session(request, *args, **kws):
    pcode, sname = args
    s = first(Sesshun.objects.filter(project__pcode = pcode, name = sname))
    s.status.enabled = not s.status.enabled
    s.status.save()
    
    return HttpResponseRedirect("/project/%s" % pcode)

def toggle_observer(request, *args, **kws):
    pcode, i_id = args
    i = first(Investigators.objects.filter(project__pcode = pcode, id = i_id))
    i.observer = not i.observer
    i.save()
    
    return HttpResponseRedirect("/project/%s" % pcode)

def dynamic_contact_form(request, *args, **kws):
    u_id, = args
    user = first(User.objects.filter(id = u_id))
    return render_to_response("sesshuns/dynamic_contact_form.html"
                            , {'u': user})

def dynamic_contact_save(request, *args, **kws):
    u_id, = args
    user = first(User.objects.filter(id = u_id))
    user.contact_instructions = request.POST.get("contact_instructions", "")
    user.save()
    return HttpResponseRedirect("/profile/%s" % u_id)

def blackout_form(request, *args, **kws):
    method = request.GET.get('_method', '')
    u_id, = args
    user  = first(User.objects.filter(id = u_id))
    b     = first(Blackout.objects.filter(id = int(request.GET.get('id', 0))))
    times = [time(h, m).strftime("%H:%M")
             for h in range(1, 24) for m in range(0, 60, 15)]
    return render_to_response("sesshuns/blackout_form.html"
                            , {'method' : method
                             , 'b'      : b
                             , 'u'      : user
                             , 'tzs'    : TimeZone.objects.all()
                             , 'repeats': Repeat.objects.all()
                             , 'times'  : times
                               })

def blackout(request, *args, **kws):
    u_id, = args
    user = first(User.objects.filter(id = u_id))

    if request.GET.get('_method', '') == "DELETE":
        b = first(Blackout.objects.filter(
                id = int(request.GET.get('id', '0'))))
        b.delete()
        return HttpResponseRedirect("/profile/%s" % u_id)
        
    if request.POST.get('_method', '') == 'PUT':
        b = first(Blackout.objects.filter(id = request.POST.get('id', '0')))
    else:
        b = Blackout(user = user)
    b.start       = datetime.strptime(
        "%s %s" % (request.POST['start'], request.POST['starttime'])
      , "%m/%d/%Y %H:%M")
    b.end         = datetime.strptime(
        "%s %s" % (request.POST['end'], request.POST['endtime'])
      , "%m/%d/%Y %H:%M")
    b.tz          = first(TimeZone.objects.filter(timeZone = request.POST['tz']))
    b.repeat      = first(Repeat.objects.filter(repeat = request.POST['repeat']))
    b.until       = datetime.strptime(
        "%s %s" % (request.POST['until'], request.POST['untiltime'])
      , "%m/%d/%Y %H:%M")
    b.description = request.POST['description']
    b.save()
        
    return HttpResponseRedirect("/profile/%s" % u_id)
