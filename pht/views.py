from django.shortcuts               import render_to_response, render
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
from pht.tools.LstPressures import LstPressures
from pht.tools.PlotLstPressures import PlotLstPressures
from httpadapters import *
from tools.database import PstInterface, BulkSourceImport
from tools.reports import *
import settings

from matplotlib.backends.backend_agg import FigureCanvasAgg 
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy, math

def notify(request):
    return HttpResponse(json.dumps({"success" : "ok" })
                      , content_type = 'application/json')

@login_required
@admin_only
def root(request):
    return render_to_response("pht/root.html", {'extjs' : settings.EXTJS_URL})

@login_required
@admin_only
def tree(request, *args, **kws):
    "Service tailor made for populating an Ext JS 4 Tree Panel"

    if request.method == 'POST':
        return HttpResponse(json.dumps({"success" : "ok" })
                          , content_type = 'application/json')
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
def lst_pressure(request, *args, **kws):

    # Are we calculating pressures for all sessions, or just
    # specific ones?
    filters = request.GET.get('filter', None)

    # TBF: even though it's possible to have two filters at once
    # we will just use one of them
    if filters is not None:
        filters = eval(filters)
        for filter in filters:
            prop = filter.get('property')
            value = filter.get('value')
            if prop == 'pcode':
                ss = Session.objects.filter(proposal__pcode = value)
            else:
                ss = Session.objects.filter(id = value)
    else:
        ss = None
        
    # calcualte the LST pressures    
    lst = LstPressures()
    pressure = lst.getPressures(sessions = ss)

    return HttpResponse(json.dumps({"success" : "ok"
                                  , "lst_pressure" : pressure
                                   })
                      , content_type = 'application/json')

@login_required
@admin_only
def print_lst_pressure(request, *args, **kws):
 
    type = args[0]
    
    plot = PlotLstPressures()
    plot.plot(type)

    response=HttpResponse(content_type='image/png')
    plot.canvas.print_png(response)
    return response

@login_required
@admin_only
def import_proposals(request, *args, **kws):
    if request.method == 'POST':
        pst = PstImport()
        # pcode is in PHT format - need to convert
        pcodes = request.POST.getlist('proposals')
        pst.importProposalsByPhtPcode(pcodes)
    return HttpResponse(json.dumps({"success" : "ok"})
                      , content_type = 'application/json')

@login_required
@admin_only
def import_pst_proposals(request, *args, **kws):
    if request.method == 'POST':
        pst = PstImport()
        # pcode is in PST format 
        pcodes = request.POST.getlist('proposals')
        pst.importProposalsByPcode(pcodes)
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
def sources_transfer(request):
    "Make sure that one session get's all the sources of another."
    if request.method == 'POST':
        fromId = request.POST.get('from')         
        toId   = request.POST.get('to')
        if fromId is not None and toId is not None:
            fromSess = Session.objects.get(id = int(fromId))
            toSess   = Session.objects.get(id = int(toId))
            for src in fromSess.sources.all():
                toSess.sources.add(src)
                toSess.save()
        SessionHttpAdapter(toSess).notify(toSess.proposal)
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')
    else:
        # error
        return HttpResponse(json.dumps({"success" : False})
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
        SourceHttpAdapter(source).notify(source.proposal)
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')

@login_required
@admin_only
def session_average_ra_dec(request, *args):
    if request.method == 'POST':
        # who's getting modified?
        session_id, = args
        session     = Session.objects.get(id = session_id)
        sources     = [Source.objects.get(id = id) for id in request.POST.getlist('sources')]
        average_ra, average_dec = session.averageRaDec(sources)

        # send back to the serve the result in both float
        # and string formats
        data = dict(ra = average_ra
                  , dec = average_dec
                  , ra_sexagesimel = rad2sexHrs(average_ra)
                  , dec_sexagesimel= rad2sexDeg(average_dec)
                   )
        SessionHttpAdapter(session).notify(session.proposal)
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

        SessionHttpAdapter(session).notify(session.proposal)
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
        SessionHttpAdapter(session).notify(session.proposal)
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
def proposal_summary(request):
    semester = request.GET.get('semester')
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=proposalSummary.pdf'

    ps = ProposalSummary(response)
    ps.report(semester = semester)

    return response

@login_required
@admin_only
def lst_pressure_report(request, *args, **kws):
    #print "lst: ", request.GET, args, kws
    debug = request.GET.get('debug', 'false')
    debug = debug == 'true'
    sessionId = request.GET.get('session', None)
    sessions = None
    if sessionId is not None:
        s = Session.objects.get(id = int(sessionId))
        sessions = [s]

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=LstPressureReport.pdf'

    lst = LstPressureReport(response)
    lst.report(sessions = sessions, debug = debug)

    return response

def mkProposalView(proposal, keys):
    retval = []
    for k in keys:
        field = proposal.get(k)
        if type(field) == list:
            field = ', '.join(field)
        if field is None:
            field = ''
        try:
            field = field.replace('\n', '<br/>').replace('\r', '<br/>')
        except:
            pass
        retval.append(field)
    return '\t'.join(map(str, retval))

@login_required
@admin_only
def proposals_export(request):
    semester  = request.GET.get('semester')
    proposals = [ProposalHttpAdapter(p).jsonDict() 
                   for p in Proposal.objects.filter(semester__semester = semester)]
    ignoredKeys = ('nrao_comment', 'srp_to_pi', 'srp_to_tac', 
                   'tech_review_to_pi', 'tech_review_to_tac', 'tac_to_pi')
    keys      = [k for k in proposals[0].keys() if k not in ignoredKeys]
    keys.remove('id')
    keys.insert(0, 'id')
    proposals = [mkProposalView(p, keys) for p in proposals]
    proposals.insert(0, '\t'.join(keys))
    response  = render(request
                    , "pht/proposals.txt"
                    , {'proposals' : proposals }
                    , content_type = 'text/plain')
    response['Content-Disposition'] = 'attachment; filename=proposals_' + semester + '.txt'
    return response

@login_required
@admin_only
def proposal_ranking(request):
    semester = request.GET.get('semester')
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=proposalRanking.pdf'

    ps = ProposalRanking(response)
    ps.report(semester = semester)

    return response

@login_required
@admin_only
def proposal_ranking_export(request):
    semester  = request.GET.get('semester')
    ps        = ProposalRanking(None)
    proposals = [ps.genRowDataOrdered(p) for p in ps.getProposals(semester)]
    header    = ps.genHeaderStr()
    response  = render(request
                    , "pht/proposalRanking.txt"
                    , {'proposals' : proposals
                     , 'header' : header} 
                    , content_type = 'text/plain')
    response['Content-Disposition'] = 'attachment; filename=proposalRanking.txt'
    return response

@login_required
@admin_only
def semester_summary(request):
    semester = request.GET.get('semester')
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=semesterSummary.pdf'

    ss = SemesterSummary(response, semester = semester)
    ss.report()

    return response

@login_required
@admin_only
def friends(request):
        users = [u for u in User.objects.all().order_by('last_name')
                   if u.isFriend() and u.username != 'dss']
        friends = [{'name' : u.__str__()
                  , 'id' : u.id} for u in users]
        return HttpResponse(json.dumps({"success" : "ok"
                                      , "friends" : friends})
          , mimetype = "text/plain")

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
