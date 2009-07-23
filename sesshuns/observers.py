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
        Q(pcode__contains = search) | Q(name__contains = search) | Q(semester__semester__contains = search))
    users    = User.objects.filter(
        Q(first_name__contains = search) | Q(last_name__contains = search))
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

from django.forms import ModelForm

class BlackoutForm(ModelForm):
    class Meta:
        model = Blackout
        fields = ('start', 'end', 'tz', 'repeat', 'description')

def blackout_form(request, *args, **kws):
    method = request.GET.get('_method', '')
    u_id, = args
    user  = first(User.objects.filter(id = u_id))
    b     = first(Blackout.objects.filter(id = int(request.GET.get('id', 0))))
    if method == "PUT" and b is not None:
        form = BlackoutForm(instance = b)
    else:
        form = BlackoutForm()

    return render_to_response("sesshuns/blackout_form.html"
                            , {'form'   : form
                             , 'method' : method
                             , 'b'      : b
                             , 'u'      : user})

def blackout(request, *args, **kws):
    u_id, = args
    user = first(User.objects.filter(id = u_id))

    if request.GET.get('_method', '') == "DELETE":
        b = first(Blackout.objects.filter(
                id = int(request.GET.get('id', '0'))))
        b.delete()
        return HttpResponseRedirect("/profile/%s" % u_id)
        
    form = BlackoutForm(request.POST)
    if form.is_valid():
        if request.POST.get('_method', '') == 'PUT':
            b = first(Blackout.objects.filter(id = request.POST.get('id', '0')))
        else:
            b = Blackout(user = user)
        b.start       = form.cleaned_data['start']
        b.end         = form.cleaned_data['end']
        b.tz          = form.cleaned_data['tz']
        b.repeat      = form.cleaned_data['repeat']
        b.description = form.cleaned_data['description']
        b.save()
        
        return HttpResponseRedirect("/profile/%s" % u_id)
    else:
        form = BlackoutForm()
    return render_to_response("sesshuns/blackout_form.html"
                            , {'form' : form
                             , 'u'    : user})
