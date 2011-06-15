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

from datetime   import datetime
from django.db.models                   import Q

from nell.utilities.database.external  import UserInfo, NRAOBosDB
from scheduler.models       import *
from scheduler.httpadapters import *

def get_rev_comment(request, obj, method):
    className = obj.__class__.__name__ if obj is not None else ""
    where = "%s %s" % (className, method)
    who   = request.user.username
    return "WHO: %s, WHERE: %s" % (who, where)

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

def getReservationsFromBOS(start, end):
    """
    Returns a dictionary of reservation info that falls within
    the given dates by querying the BOS.
    Make sure this creates the same output as getReservationsFromDB.
    """

    res = NRAOBosDB().reservationsRange(start, end)
    reservations = []
    for r in res:
       # BOS is still using the wrong ID - we need 'global id'
       # See Story: https://www.pivotaltracker.com/story/show/14549863
       userAuth_id = int(r['id'])
       pst_id = UserInfo().getIdFromUserAuthenticationId(userAuth_id)
       try: 
           user = User.objects.get(pst_id = pst_id)
           pcodes = ",".join(user.getIncompleteProjects())
           hasInc = user.hasIncompleteProject()
       except User.DoesNotExist:
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
            # Note: using update_from_post instead of init for accounting?
            PeriodHttpAdapter(newP).update_from_post(pj, 'UTC')
            newP.elective = newE
            newP.save()

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
            # Note: using update_from_post instead of init for accounting?
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
        #print "    new Window: "
        #print "    ", newW.id, newW

jsonMap = {"authorized"     : "status__authorized"
         , "between"        : "time_between"
         , "backup"         : "status__backup"
         , "pcode"          : "project__pcode"
         , "complete"       : "status__complete"
         , "coord_mode"     : "target__system__name"
         , "enabled"        : "status__enabled"
         , "freq"           : "frequency"
         , "grade"          : "allotment__grade"
         , "id"             : "id"
         , "name"           : "name"
         , "orig_ID"        : "original_id"
         , "receiver"       : "receiver_group__receivers__abbreviation"
         , "PSC_time"       : "allotment__psc_time"
         , "req_max"        : "max_duration"
         , "req_min"        : "min_duration"
         , "science"        : "observing_type__type"
         , "sem_time"       : "allotment__max_semester_time"
         , "source"         : "target__source"
         , "source_h"       : "target__horizontal"
         , "source_v"       : "target__vertical"
         , "total_time"     : "allotment__total_time"
         , "type"           : "session_type__type"
               }
