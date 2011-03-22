from django.http                        import HttpResponseRedirect
from sesshuns.models                    import *
from sesshuns.utilities                 import *

def admin_only(view_func):
    """
    If the logged in user isn't an administrator, redirect elsewhere.
    Otherwise, proceed as planned.
    """
    redirect_url = '/profile'
    def decorate(request, *args, **kwds):
        if not get_requestor(request).isAdmin():
            if len(args) != 0:
                redirect_url = redirect_url % args
            return HttpResponseRedirect(redirect_url)
        return view_func(request, *args, **kwds)
    return decorate

def is_operator(view_func):
    """
    If the logged in user isn't an operator and if he/she isn't
    an administrator, redirect elsewhere. Otherwise, proceed as planned.
    """
    redirect_url = '/schedule/public'
    def decorate(request, *args, **kwds):
        requestor = get_requestor(request)
        if not requestor.isOperator() and not requestor.isAdmin():
            return HttpResponseRedirect(redirect_url)
        return view_func(request, *args, **kwds)
    return decorate

def is_staff(view_func):
    """
    If the logged in user isn't a staff member, redirect elsewhere.
    Otherwise, proceed as planned.
    """
    redirect_url = '/schedule/public'
    def decorate(request, *args, **kwds):
        requestor = get_requestor(request)
        requestor.checkAuthUser()
        if not requestor.isStaff():
            return HttpResponseRedirect(redirect_url)
        return view_func(request, *args, **kwds)
    return decorate

def has_access(view_func):
    """
    If the logged in user isn't allowed to see this page and if he/she isn't
    an administrator, redirect elsewhere. Otherwise, proceed as planned.
    """
    redirect_url = '/profile'
    def decorate(request, *args, **kwds):
        user      = User.objects.get(id = args[0])
        requestor = get_requestor(request)

        if user != requestor and not requestor.isAdmin():
            return HttpResponseRedirect(redirect_url)
        return view_func(request, *args, **kwds)
    return decorate

def has_user_access(view_func):
    """
    Allows a user to see the page if they are looking at their own information,
    are part of another user's project, or an administrator. 
    Otherwise, they are redirected elsewhere.
    """
    redirect_url = '/profile'
    def decorate(request, *args, **kwds):
        if len(args) > 0:
            user = User.objects.get(id = args[0])
            if user is None or not get_requestor(request).canViewUser(user):
                return HttpResponseRedirect(redirect_url)
        return view_func(request, *args, **kwds)
    return decorate

def has_project_access(view_func):
    redirect_url = '/profile'
    def decorate(request, *args, **kwds):
        if not get_requestor(request).canViewProject(args[0]):
            return HttpResponseRedirect(redirect_url)
        return view_func(request, *args, **kwds)
    return decorate
