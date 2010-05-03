from datetime         import time
from django.db.models import Q
from nell.utilities   import UserInfo
from sesshuns.models  import *

def acknowledge_moc(requestor, period):
    """
    Sets acknowledge flag for periods which fail MOC.
    """
    if requestor.isOperator(): # Only operators can acknowledge MOC failures.
        period.moc_ack = True 
        period.save()

def get_rev_comment(request, obj, method):
    where = "%s %s" % (obj.__class__.__name__, method)
    who   = request.user.username
    return "WHO: %s, WHERE: %s" % (who, where)

def create_user(username):
    """
    If the DSS doesn't know about the user, but the User Portal does,
    then add them to our database so they can at least see their profile.
    """
    info = UserInfo().getStaticContactInfoByUserName(username
                                                   , use_cache = False)
    user = User(pst_id     = info['id']
              , username   = username
              , first_name = info['name']['first-name']
              , last_name  = info['name']['last-name']
              , role       = first(Role.objects.filter(role = "Observer")))
    user.save()

    return user

def get_requestor(request):
    """
    Gets login name; and if we don't have a user with that name,
    creates one before returning the user.

    Note: CAS (used by PST) has case-insensitive usernames.
    """
    loginUser = request.user.username
    requestor = first(User.objects.filter(username__iexact = loginUser))

    if requestor is None:
        requestor = create_user(loginUser)

    return requestor

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

def project_search(value):
    projects = Project.objects.filter(
        Q(pcode__icontains = value) | \
            Q(name__icontains = value) | \
            Q(semester__semester__icontains = value.upper()))
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

        if code == value.upper() and p not in projects:
            projects.append(p)

    return projects
