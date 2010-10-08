from datetime         import time
from django.db.models import Q
from pytz             import timezone
import pytz

from nell.utilities   import UserInfo
from sesshuns.models  import *

def getReceivers(names):
    rcvrs = []
    error = None
    for name in [n for n in names if len(n) != 0]:
        r = Receiver.get_rcvr(name)
        if r is not None:
            rcvrs.append(r)
        else:
            error = 'Unrecognized receiver: %s' % name
    return error, rcvrs

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

def acknowledge_moc(requestor, period):
    """
    Sets acknowledge flag for periods which fail MOC.
    """
    if requestor.isOperator(): # Only operators can acknowledge MOC failures.
        period.moc_ack = True 
        period.save()

def get_rev_comment(request, obj, method):
    className = obj.__class__.__name__ if obj is not None else ""
    where = "%s %s" % (className, method)
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
              , first_name = info['name']['first-name']
              , last_name  = info['name']['last-name']
              , role       = first(Role.objects.filter(role = "Observer")))
    user.save()

    p = Preference(user = user, timeZone = "UTC")
    p.save()

    return user

def get_requestor(request):
    """
    Gets login name; and if we don't have a user with that name,
    creates one before returning the user.

    Note: CAS (used by PST) has case-insensitive usernames.
    """
    loginUser = request.user.username
    pst_id = UserInfo().getIdFromUsername(loginUser)
    requestor = first(User.objects.filter(pst_id = pst_id))

    if requestor is None:
        requestor = create_user(loginUser)

    return requestor

def get_blackout_form_context(b_id, fdata, user, requestor, errors):
    "Returns dictionary for populating blackout form"
    return {
        'u'        : user
      , 'requestor': requestor
      , 'b_id'   : b_id
      , 'b'        : fdata # b's dates in DB are UTC
      , 'tzs'      : TimeZone.objects.all()
      , 'timezone' : 'UTC' # form always starts at UTC
      , 'repeats'  : Repeat.objects.all()
      , 'times'    : [time(h, m).strftime("%H:%M") \
                      for h in range(0, 24) for m in range(0, 60, 15)]
      , 'errors'   : errors
    }

def adjustDate(tz_pref, dt, to_utc = False):
    if dt is None:
        return
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    tz  = timezone(tz_pref)
    utc = pytz.utc
    if to_utc:
        return tz.localize(dt).astimezone(utc)
    else:
        return utc.localize(dt).astimezone(tz)

def parse_datetime(fdata, dateName, timeName, tz):
    "Extract the date & time from the form values to make a datetime obj"
    dt    = None
    error = None
    try:
        if fdata[dateName] != '':
            dt = adjustDate(tz, datetime.strptime(
                                 "%s %s" % (fdata[dateName], fdata[timeName])
                               , "%m/%d/%Y %H:%M")
                          , to_utc = True)

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
