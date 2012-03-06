from django.shortcuts               import render_to_response
from django.http  import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from datetime   import datetime, timedelta

import simplejson as json

from utilities import *
from nell.utilities import SLATimeAgent
from users.decorators import admin_only
from scheduler.models import *
from models import *
from pht.tools.database import PstImport
from httpadapters import *
from tools.database import PstInterface
from tools.database import BulkSourceImport
import math



@login_required
@admin_only
def root(request):
    return render_to_response("pht/root.html", {})

@login_required
@admin_only
def tree(request, *args, **kws):
    "Service tailor made for populating an Ext JS 4 Tree Panel"

    # Where in the tree is this request from? 
    node = request.GET.get('node', None)
    
    # Each node in the tree needs:
    # text : what's displayed
    # leaf : whether it's the end of a branch (leaf) or not 
    # id : unique id for the node - when a proposal gets clicked on in the
    # tree, this is what the value of the node above will be.  Here we've 
    # designed this id to be of form type=value, where type tells you what
    # level of the tree you are at.
    # store : this is used by the client to know where to retrieve
    # a requested object from.
    # XXX : we can also stick in whatever extra info we want in there.

    js = []
    if node == 'root' or node is None:
        # We're at the very top of our tree.
        # Get the Semesters used by proposals in this DB
        ps = Proposal.objects.all().order_by('pcode')
        sems = [s.semester for s in Proposal.semestersUsed()]
        js = [{'text' : semester
             , 'id'   : 'semester=%s' % semester
             , 'store': None 
             , 'semester' : semester
             , 'leaf' : False} for semester in sems]
    elif 'semester' in node:  
        # A semester node has been clicked on: 
        # send back the projects for this semester.
        sem =  node.split('=')[1] 
        ps = Proposal.objects.filter(semester__semester = sem).order_by('pcode')
        js = [{'pcode' : p.pcode
             , 'id'    : "pcode=%s" % p.pcode
             , 'text'  : p.pcode
             , 'leaf'  : False
             , 'store' : 'Proposals'
              } for p in ps]
    #else:
    elif 'pcode' in node:
        # A project node has been clicked on: 
        # send back the sessions for this project.
        pcode = node.split('=')[1] 
        p = Proposal.objects.get(pcode = pcode)
        js = [{ 'text' : "%s (%d)" % (s.name, s.id)
              , 'id'   : "sessionId=%d" % s.id
              , 'leaf' : True 
              , 'sessionId' : s.id
              , 'store' : 'Sessions'
              } for s in p.session_set.all().order_by('id')]

    return HttpResponse(json.dumps({"success" : "ok"
                                  , "proposals" : js
                                   })
                      , content_type = 'application/json')


@login_required
@admin_only
def import_proposals(request, *args, **kws):
    if request.method == 'POST':
        pst = PstImport()
        # pcode is in PHT format - need to convert
        for pcode in request.POST.getlist('proposals'):
            pst.importProposal(pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/'))
    return HttpResponse(json.dumps({"success" : "ok"})
                      , content_type = 'application/json')

@login_required
@admin_only
def import_pst_proposals(request, *args, **kws):
    if request.method == 'POST':
        pst = PstImport()
        # pcode is in PST format
        for pcode in request.POST.getlist('proposals'):
            pst.importProposal(pcode)
    return HttpResponse(json.dumps({"success" : "ok"})
                      , content_type = 'application/json')

@login_required
@admin_only
def import_semester(request, *args, **kws):
    if request.method == 'POST':
        pst      = PstImport()
        semester = request.POST.get('semester')
        if semester is not None:
            pst.importProposals(semester)
    return HttpResponse(json.dumps({"success" : "ok"})
                      , content_type = 'application/json')
                                  
@login_required
@admin_only
def sources_import(request):
    "Handles upload of a file containing sources"
    # TBF: not sure that these HttpResponses are correct thing to return
    if request.method == 'POST':
        pcode = request.POST.get('pcode')
        result, err = handle_uploaded_sources(request.FILES['file']
                                            , pcode)
        if result:                                    
            return HttpResponse(json.dumps({"success" : "ok"})
                              , content_type = 'application/json')
        else:
            #print err
            # error
            return HttpResponse(json.dumps({"success" : False
                                          , "errorMsg" : err})
                              , content_type = 'application/json')
            
    else:
        # error
        return HttpResponse(json.dumps({"success" : False})
                          , content_type = 'application/json')

def handle_uploaded_sources(f, pcode):

    try:
        # TBF: where to really put the file?
        filename = 'sourceImport.txt'
        destination = open(filename, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
    except Exception, e:
        return (False, str(e))
    # create sources if file is valid 
    i = BulkSourceImport(filename = filename
                       , pcode = pcode)
    return i.importSources()  

@login_required
@admin_only
def get_options(request, *args, **kws):
    "Depending on mode, returns various options"
    mode = request.GET.get("mode", None)
    if mode == "proposal_codes":
        ps = Proposal.objects.all().order_by('pcode')
        pcodes = [{'id' : p.id, 'pcode' : p.pcode} for p in ps]
        return HttpResponse(json.dumps({"success" : "ok" , 'proposal codes' : pcodes })
                          , content_type = 'application/json')
    elif mode == "session_names":                      
        ss = Session.objects.all().order_by('name')
        sess = [{'id' : s.id
               , 'session' : s.name
               , 'handle' : "%s (%s)" % (s.name, s.proposal.pcode)} for s in ss]
        return HttpResponse(json.dumps({"success" : "ok" , 'session names' : sess })
                          , content_type = 'application/json')
    else:
        return HttpResponse("")

# Sources - just like Sessions & Proposals, but with additional methods to support
# the Proposal Sources & Session Sources grids.

@login_required
@admin_only
def proposal_sources(request, *args):
    pcode,   = args
    proposal = Proposal.objects.get(pcode = pcode)
    sources  = [SourceHttpAdapter(ps).jsonDict()
                  for ps in proposal.source_set.all()]
    return HttpResponse(json.dumps({"success" : "ok" , 'sources' : sources })
                      , content_type = 'application/json')

@login_required
@admin_only
def session_sources(request, *args):
    if len(args) == 1:
        session_id, = args
        session     = Session.objects.get(id = session_id)
        sources     = [SourceHttpAdapter(s).jsonDict() for s in session.sources.all()]
        return HttpResponse(json.dumps({"success" : "ok" , 'sources' : sources })
                          , content_type = 'application/json')
    elif len(args) == 2:
        if request.method == 'POST':
            session_id, source_id, = args
            session = Session.objects.get(id = session_id)
            source  = Source.objects.get(id = source_id)
            session.sources.add(source)
            session.save()
        elif request.method == 'DELETE':
            session_id, source_id, = args
            session = Session.objects.get(id = session_id)
            source  = Source.objects.get(id = source_id)
            session.sources.remove(source)
            session.save()
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')

def meanAngle(thetas):
    if len(thetas) == 1:
        return thetas[0]

    thetas.sort()
    avg_theta = thetas[0]
    for theta in thetas[1:]:
        # Find the difference between the angles
        diff = abs(avg_theta - theta)
        if diff > math.pi:
            # Switch to the nearest angle
            diff_prime = 2 * math.pi - diff
            # Compute the middle of the angle
            avg      = diff_prime / 2.
            # Fold the average into the original angle
            theta = theta + avg
            # Account for wrap around and set the new overall average
            avg_theta = theta - (2 * math.pi) if theta >= 2 * math.pi else theta
        else:
            avg_theta = (avg_theta + theta) / 2.
    return avg_theta 

@login_required
@admin_only
def session_average_ra_dec(request, *args):
    if request.method == 'POST':
        # who's getting modified?
        session_id, = args
        session     = Session.objects.get(id = session_id)
        sources     = [Source.objects.get(id = id) for id in request.POST.getlist('sources')]
        average_ra  = meanAngle([s.ra for s in sources]) 
        average_dec = sum([s.dec for s in sources]) / float(len(sources))
        session.target.ra  = average_ra
        session.target.dec = average_dec
        session.target.save()

        # send back to the serve the result in both float
        # and string formats
        data = dict(ra = average_ra
                  , dec = average_dec
                  , ra_sexagesimel = rad2sexHrs(average_ra)
                  , dec_sexagesimel= rad2sexDeg(average_dec)
                   )
        return HttpResponse(json.dumps({"success" : "ok"
                                      , "data" : data})
                          , content_type = 'application/json')
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

@login_required
@admin_only
def session_generate_periods(request, *args):
    if request.method == 'POST':
        # who's getting modified?
        session_id, = args
        session     = Session.objects.get(id = session_id)
        
        periodSource = session.periodGenerationFrom()
        if periodSource is None:
            msg = """
            You have not specified enough information
            in this session to generate Periods.
            """
            return HttpResponse(json.dumps({"success" : False 
                                          , "message" : msg})
                              , content_type = 'application/json')
        
        # looks like we can safely proceed 
        numPs = session.genPeriods()
        msg = """
        Pre-existing periods have been removed, 
        and %d new Periods were generated using type: %s
        """ % (numPs, periodSource)
        session     = Session.objects.get(id = session_id)

        return HttpResponse(json.dumps({"success" : "ok"
                                      , "message" : msg})
                          , content_type = 'application/json')
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
        

@login_required
@admin_only
def session_calculate_LSTs(request, *args):
    if request.method == 'POST':
        # who's getting modified?
        session_id, = args
        session     = Session.objects.get(id = session_id)
 
        minLst, maxLst = session.target.calcLSTrange()
        if minLst is None or maxLst is None:
            return HttpResponse(json.dumps({"failure" : "failure"})
                              , content_type = 'application/json')
        
        # save calcs to the DB
        session.target.min_lst = minLst
        session.target.max_lst = maxLst
        session.target.save()

        # now use this LST range for the center & width
        center, width = session.target.calcCenterWidthLST()
        session.target.center_lst = center
        session.target.lst_width   = width
        session.target.save()

        # send back to the serve the result in both float
        # and string formats
        data = dict(minLst = minLst
                  , maxLst = maxLst
                  , centerLst = center
                  , lstWidth  = width
                  , minLstSexagesimel = rad2sexHrs(minLst)
                  , maxLstSexagesimel = rad2sexHrs(maxLst)
                  , centerLstSexagesimel = rad2sexHrs(center)
                  , lstWidthSexagesimel = rad2sexHrs(width)
                   )
        return HttpResponse(json.dumps({"success" : "ok"
                                      , "data" : data})
                          , content_type = 'application/json')
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')



@login_required
@admin_only
def users(request):
    pst   = PstInterface()
    users = [{'id' : r['person_id']
            , 'person_id' : r['person_id']
            , 'name' : '%s, %s' % (r['lastName'], r['firstName'])}
             for r in pst.getUsers()]
    return HttpResponse(json.dumps({"success" : "ok" , 'users' : users })
                      , content_type = 'application/json')

@login_required
@admin_only
def user_info(request):
    pst   = PstInterface()
    person_id = int(request.POST.get('person_id') if request.method == 'POST' \
                else request.GET.get('person_id'))
    info = pst.getUserInfo(person_id)
    info['address'] = "%s %s %s, %s %s %s" % (info.get('street1')
                                            , info.get('street2')
                                            , info.get('city')
                                            , info.get('state')
                                            , info.get('postalCode')
                                            , info.get('addressCountry')
                                             )
    return HttpResponse(json.dumps({"success" : "ok", "info" : info})
                      , content_type = 'application/json')

@login_required
@admin_only
def lst_range(request):
    def lstDt2lstHr(dt):
        time = dt.time()
        return time.hour + time.minute / 60. + (time.second + time.microsecond / 10e6) / 3600

    def check_lst_range(lst, startDate, endDate):
        slst  = lstDt2lstHr(startDate)
        elst  = lstDt2lstHr(endDate)
        if (elst > slst):
            i = 0
            newElst = slst
            while newElst < 3:
                i += 1
                newEndDate = startDate + timedelta(days = i)
                newEndDate = SLATimeAgent.RelativeLST2AbsoluteTime(lst, newEndDate)
                newElst    = lstDt2lstHr(newEndDate)
            newEndDate = startDate + timedelta(days = i - 1)
            newEndDate = SLATimeAgent.RelativeLST2AbsoluteTime(lst, newEndDate)
            newElst    = lstDt2lstHr(newEndDate)
            sndsd = newEndDate + timedelta(days = 1)
            sndsd = datetime(sndsd.year, sndsd.month, sndsd.day, 23, 59, 59)
            return [(startDate, newEndDate), (sndsd, endDate)]
        else:
            return [(startDate, endDate)]

    startDateStr = request.GET.get('start')
    numDays      = request.GET.get('numDays')
    startDate    = datetime.strptime(startDateStr, '%Y-%m-%d')
    endDate      = startDate + timedelta(days = int(numDays))
    lines = []
    for lst in [0, 6, 12, 18]:
        lines.extend([{'start': str(s), 'end' : str(e)} 
            for s, e in check_lst_range(lst
                                      , SLATimeAgent.RelativeLST2AbsoluteTime(lst, startDate)
                                      , SLATimeAgent.RelativeLST2AbsoluteTime(lst, endDate))])
    return HttpResponse(json.dumps({"success" : "ok", 'lines' : lines})
                      , content_type = 'application/json')


@login_required
@admin_only
def pis(request):
    authors = [{'id': a.id, 'name': a.getLastFirstName(), 'pcode': a.proposal.pcode}
               for a in Author.objects.all()]

    return HttpResponse(json.dumps({"success" : "ok" , 'pis' : authors })
                      , content_type = 'application/json')

@login_required
@admin_only
def proposal_types(request):
    return HttpResponse(json.dumps({"success" : "ok"
                                  , 'proposal types' : ProposalType.jsonDictOptions()})
                      , content_type = 'application/json')

@login_required
@admin_only
def session_separations(request):
    return HttpResponse(json.dumps({"success" : "ok" 
                                  , 'session separations' : SessionSeparation.jsonDictOptions()})
                      , content_type = 'application/json')

@login_required
@admin_only
def session_grades(request):
    return HttpResponse(json.dumps({"success" : "ok"
                                  , 'session grades' : SessionGrade.jsonDictOptions()})
                      , content_type = 'application/json')

def pst_proposal_codes(request):
    pst = PstInterface()
    return HttpResponse(json.dumps({"success" : "ok"
                                  , 'pst pcodes' : pst.getProposalCodes()})
                      , content_type = 'application/json')
    
def session_observing_types(request):
    return simpleGetAllResponse('observing types', Observing_Type.jsonDictOptions())

def session_types(request):
    return simpleGetAllResponse('session types', SessionType.jsonDictOptions())

def weather_types(request):
    return simpleGetAllResponse('weather types', WeatherType.jsonDictOptions())

def semesters(request):
    return simpleGetAllResponse('semesters', Semester.jsonDictOptions())

def receivers(request):
    return simpleGetAllResponse('receivers', Receiver.jsonDictOptions())

def backends(request):
    return simpleGetAllResponse('backends', Backend.jsonDictOptions())

def import_reports(request):
    return simpleGetAllResponse('import_reports', ImportReport.jsonDictOptions())

def observing_types(request):
    return simpleGetAllResponse('observing types', ObservingType.jsonDictOptions())

def science_categories(request):
    return simpleGetAllResponse('science categories', ScientificCategory.jsonDictOptions())

def statuses(request):
    return simpleGetAllResponse('statuses', Status.jsonDictOptions())

def source_epochs(request):
    return simpleGetAllResponse('source epochs', SourceCoordinateEpoch.jsonDictOptions())

def source_systems(request):
    return simpleGetAllResponse('source systems', SourceCoordinateSystem.jsonDictOptions())

def source_velocity_types(request):
    return simpleGetAllResponse('source velocity types', SourceVelocityType.jsonDictOptions())

def source_conventions(request):
    return simpleGetAllResponse('source conventions', SourceConvention.jsonDictOptions())

def source_reference_frames(request):
    return simpleGetAllResponse('source reference frames', SourceReferenceFrame.jsonDictOptions())

def simpleGetAllResponse(key, data):
    return HttpResponse(json.dumps({"success" : "ok" , key : data })
                      , content_type = 'application/json')
