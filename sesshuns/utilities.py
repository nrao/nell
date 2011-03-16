from datetime                           import datetime, time, timedelta
from django.db.models                   import Q
from pytz                               import timezone
from copy                               import deepcopy
import pytz

from scheduler.models                   import *
from sesshuns.models                   import *
from scheduler.httpadapters             import *
from nell.utilities                     import UserInfo, NRAOBosDB, TimeAgent
from scheduler.GBTCalendarEvent         import CalEventPeriod, CalEventElective, CalEventMaintenanceActivity
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException

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

def getInvestigatorEmails(pcodes):
    """
    Given a list of project codes, what are the list of emails for them
    organized by:
       * Principal Investigator
       * Principal Contact
       * Co-Investigatrs
       * Observers
       * Friends
    """   
    pi = []
    pc = []
    ci = []
    ob = []
    fs = []
    try:
        # TBF: use list comprehension?
        for pcode in pcodes:
            p = Project.objects.filter(pcode = pcode)[0]
            for inv in p.investigator_set.all():
                if inv.principal_investigator:
                    for email in inv.user.getEmails():
                        pi.append(email)
                if inv.principal_contact:
                    for email in inv.user.getEmails():
                        pc.append(email)
                if not inv.principal_investigator and not inv.principal_contact:
                    for email in inv.user.getEmails():
                        ci.append(email)
                if inv.observer:
                    for email in inv.user.getEmails():
                        ob.append(email)
            for f in p.friend_set.all():                        
                for email in f.user.getEmails():
                    fs.append(email)
    except IndexError, data:
        pass # in case of blanks at the end of the list.
    return sorted(pi), sorted(pc), sorted(ci), sorted(ob), sorted(fs)

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
    user = User(pst_id     = info['person_id']
              , first_name = info['first_name']
              , last_name  = info['last_name']
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

def getReservationsFromBOS(start, end):
    """
    Returns a dictionary of reservation info that falls within
    the given dates by querying the BOS.
    Make sure this creates the same output as getReservationsFromDB.
    """

    res = NRAOBosDB().reservationsRange(start, end)
    reservations = []
    for r in res:
       # TBF: BOS is still using the wrong ID - we need 'global id'
       userAuth_id = int(r['id'])
       pst_id = UserInfo().getIdFromUserAuthenticationId(userAuth_id)
       user = first(User.objects.filter(pst_id = pst_id))
       if user is not None:
           pcodes = ",".join(user.getIncompleteProjects())
           hasInc = user.hasIncompleteProject()
       else:
           pcodes = ""
           hasInc = False
       if hasInc:
           r.update({"pcodes" : pcodes})
           r.update({"id" : user.pst_id})
           reservations.append(r)
    return reservations

def getReservationsFromDB(start, end):
    """
    Returns a dictionary of reservation info that falls within the
    given dates by querying the Reservations table, which is populated
    daily using the BOS query service.
    Make sure this creates the same output as getReservationsFromBOS.
    """

    startDT = datetime.strptime(start, "%m/%d/%Y")
    endDT   = datetime.strptime(end  , "%m/%d/%Y")
    resDB = [r for r in Reservation.objects.all() if r.end_date >= startDT and r.start_date <= endDT]
    reservations = [{'id'    : r.user.pst_id
                   , 'name'  : r.user.display_name()
                   , 'pcodes': ",".join(r.user.getIncompleteProjects())
                   , 'start' : r.start_date.strftime("%m/%d/%Y")
                   , 'end'   : r.end_date.strftime("%m/%d/%Y")
                   } for r in resDB if r.user is not None and r.user.hasIncompleteProject()]
    return reservations

######################################################################
# Creates a list of events for the date range provided. First, gets
# all the scheduled periods.  Next, gets the pending maintenance
# periods.  Finally, collects the non-maintenance-period maintenance
# events for each day. These are then sorted and added to the day's
# activities.  For every day there will be a tuple consisting of the
# datetime for that day, and a list of that day's events.
######################################################################

def get_gbt_schedule_events(start, end, timezone, get_moc = False, ignore_non_maint_period_maint_events = False):
    """
    Generate a list of schedule events.  The list returned consists of
    tuples: first element is a datetime, the second element is the
    list of events for that date.
    """

    days = (end - start).days
    calendar = []

    for i in range(0, days):
        daily_events = []
        today = start + timedelta(days = i)
        delta = timedelta(days = 1)
        yesterday = today - delta
        tomorrow = today + delta

        # must use UTC equivalents for database lookups if times given
        # in Eastern Time
        utc_today  = TimeAgent.est2utc(today) if timezone == 'ET' else today
        utc_yesterday = utc_today - delta
        utc_tomorrow = utc_today + delta
        
        # include previous day's periods because last one may end
        # today.  Perhaps there is a way to do this exclusively via
        # query, but there aren't that many periods in a day.
        ps = Period.objects.filter(start__gte = utc_yesterday)\
            .filter(start__lt = utc_tomorrow).filter(state__name = "Scheduled")

        for p in ps:
            if p.end() > utc_today:
                if p.elective:
                    ev = CalEventElective(p.elective, p.start < utc_today, p.end() > utc_tomorrow,
                                          p.moc_met() if get_moc else True, timezone)
                else:
                    ev = CalEventPeriod(p, p.start < utc_today, p.end() > utc_tomorrow,
                                        p.moc_met() if get_moc else True, timezone)
                daily_events.append(ev)

        # if today is monday, get floating maintenance events for the week
        if today.weekday() == 0:
            daily_events += _get_floating_maint_events(today, timezone)

        # finally gather up the non-maintenance-period maintenance events
        if not ignore_non_maint_period_maint_events:
            daily_events += _get_non_maint_period_maint_events(today, timezone)

        # now sort the events and add to the calendar list
        daily_events.sort()
        calendar.append((today, daily_events))

    return calendar

######################################################################
# This helper gathers up all the floating maintenance activities
# Floating activities may come as pending periods, or incomplete
# electives and have a session type of 'maintenance'.  This helper
# fetches the pending periods (if any) and the incomplete events (if
# any) in the date range, packages them in a list of CalEvents, sorts
# the list and labels each event appropriately ('A', 'B', etc.) and
# returns the list.
######################################################################

def _get_floating_maint_events(day, timezone):
    """
    _get_floating_maint_events(day, timezone)
    
    Takes the day (assumes it is Monday) and finds the maintenance
    periods for that week.  Returns a list of CalEvent objects
    consisting of all the floating activities for that Monday's week.
    """

    pend = []
    utc_day = TimeAgent.est2utc(day) if timezone == 'ET' else day

    try:
        delta = timedelta(days = 7)
        # get maintenance periods for the date span
        mp = Period.objects\
            .filter(session__observing_type__type = "maintenance")\
            .filter(start__gte = utc_day)\
            .filter(start__lt = utc_day + delta)\
            .filter(elective = None)\
            .exclude(state__abbreviation = 'D')

        # get maintenance electives for the date span
        me = Elective.objects\
            .filter(session__observing_type__type = 'maintenance')\
            .filter(periods__start__gte = utc_day)\
            .filter(periods__start__lt = utc_day + delta)\
            .distinct()

        # combine both kinds of maintenance events (elective provides
        # first period as representative), then sort the events by
        # underlying period's start datetime.
        maint_events = []
        next_day = utc_day + timedelta(days = 1)

        for p in mp:
            ev = CalEventPeriod(p, p.start < utc_day, p.end() >= next_day, True, timezone)
            maint_events.append(ev)

        for i in me:
            ev = CalEventElective(i, TZ = timezone)
            maint_events.append(ev)

        maint_events.sort()

        # ensure that first one gets 'A', second 'B', etc.
        for i in range(0, len(maint_events)):
            maint_events[i].set_fm_name(chr(i + 65))

        # now remove those that are scheduled.  Including scheduled
        # non-elective periods and completed electives in the above
        # queries ensures that if 'A' has been scheduled, 'B' still
        # appears as 'B' and not the new 'A', which would happen if we
        # only consider pending periods or non-complete electives.
        maint_events = [e for e in maint_events if e.is_floating_maintenance()] 
    except:
        if settings.DEBUG == True:
            printException(formatExceptionInfo())

        maint_events = []

    return maint_events

######################################################################
# Finds any non-maintenance-period maintenance activities and places
# them in a CalEvent object.  This object is returned as a list of one
# CalEvent object, to make it easier to add to other lists of CalEvent
# objects.
######################################################################

def _get_non_maint_period_maint_events(today, timezone):
    """
    Gathers up all the non-maintenance-period maintenance activities,
    and returns them in a list of CalEvent objects.
    """

    utc_today = TimeAgent.est2utc(today) if timezone == 'ET' else today

    mas = Maintenance_Activity.objects.filter(_start__gte = utc_today) \
        .filter(_start__lt = utc_today + timedelta(days = 1)) \
        .filter(period = None) \
        .filter(deleted = False) \
        .order_by('_start')

    if mas.exists():
        ev = CalEventMaintenanceActivity(mas, TZ = timezone)
        return [ev]

    return []

def copy_elective(id, num):
    """
    Makes copies of the elective identified by the passed id.
    See copy_window for more.
    """
    e = Elective.objects.get(id = id)
    ej = ElectiveHttpAdapter(e).jsondict()
    for count in range(num):
        newE = Elective()
        WindowHttpAdapter(newE).init_from_post(ej) #Window()
        for pj in ej['periods']:
            newP = Period()
            # TBF: using update_from_post instead of init for accounting?
            PeriodHttpAdapter(newP).update_from_post(pj, 'UTC')
            newP.elective = newE
            newP.save()
        # it looks like setting the periods & accounting causes
        # the complete flag to get set somehow, so do it again(TBF)
        newE.complete = ej['complete']
        newE.save()


def copy_window(id, num):
    """
    Makes copies of the window identified by the passed id.
    Most of the 'copying' of objects that is done in the DSS, is done
    via the 'duplicate' button in all the explorers, but since
    we don't have an explorer for windows, we must do this ourselves.
    However, we use the same strategy: the explorers take the json
    representation of the current object, and post that to create
    a new one.
    Note: not using deepcopy, it can cause issues.
    """
    w = Window.objects.get(id = id)
    wj = WindowHttpAdapter(w).jsondict()
    for count in range(num):
        # first the window
        newW = Window()
        #newW.save()
        #print wj["handle"], wj["total_time"], wj['complete']
        WindowHttpAdapter(newW).init_from_post(wj) #Window()
        
        #newW.session = w.session
        #newW.total_time = w.total_time
        #newW.complete = w.complete
        #newW.save()
        #print "new win id: ", newW.id
        # now it's associated objects
        #ranges = w.ranges()
        #for rg in w.ranges():
        for wrj in wj['ranges']:
            newWr = WindowRange()
            #newWr.save()
            WindowRangeHttpAdapter(newWr).init_from_post(wrj)
            newWr.window = newW
            newWr.save()
            
            
            #wr = WindowRange(window = newW
            #               , start_date = rg.start_date
            #               , duration = rg.duration
            #                )
            #wr.save()                
        for pj in wj['periods']:
            newP = Period()
            # TBF: using update_from_post instead of init for accounting?
            PeriodHttpAdapter(newP).update_from_post(pj, 'UTC')
            newP.window = newW
            newP.save()

        #periods = w.periods.all()
        #for p in periods:
            #pa = deepcopy(p.accounting)
            #pa.id = None
            #pa.save()
            #newP = Period(session = p.session
            #            , start = p.start
            #            , duration = p.duration
            #            , state = p.state
            #            , window = newW
            #            , accounting = pa
            #            , score = p.score
            #            , forecast = p.forecast
            #            , backup = p.backup
            #            , moc_ack = p.moc_ack  
            #             )
            #newP.save()
            # now the rx
            #for r in p.receivers.all():
            #    pr = Period_Receiver(receiver = r, period = newP)
            #    pr.save()
            #print "newP has window: ", newP.id, newP.window, newP.window.id
            # is this period the default?
            if w.default_period.id == pj['id']:
                newW.default_period = newP
                newW.save()
            # it looks like setting the periods & accounting causes
            # the complete flag to get set somehow, so do it again(TBF)
        newW.complete = wj['complete']
        newW.save()
        #print "    new Window: "
        #print "    ", newW.id, newW


