from django.shortcuts               import render_to_response
from django.http  import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required

import simplejson as json

from utilities import *
from users.decorators import admin_only
from models import *
from pht.tools.database import PstImport
from httpadapters import *
from tools.database import PstInterface
import math

@login_required
@admin_only
def root(request):
    return render_to_response("pht/root.html", {})

@login_required
@admin_only
def tree(request, *args, **kws):
    "Service tailor made for populating an Ext JS 4 Tree Panel"

    # do we want all proposals, or just the sessions for a given proposal?
    node = request.GET.get('node', None)
    
    # each node in the tree needs:
    # text : what's displayed
    # leaf : whether it's the end of a branch (leaf) or not 
    # id : unique id for the node - when a proposal gets clicked on in the
    # tree, this is what the value of the node above will be
    js = []
    if node == 'root' or node is None:
        ps = Proposal.objects.all().order_by('pcode')
        js = [{'pcode' : p.pcode
             , 'id'    : p.pcode
             , 'text'  : p.pcode
             , 'leaf'  : False
             , 'store' : 'Proposals'
              } for p in ps]
    else:
        pcode = node
        p = Proposal.objects.get(pcode = pcode)
        js = [{ 'text' : "%s (%d)" % (s.name, s.id)
              , 'id'   : s.id
              , 'leaf' : True 
              , 'store' : 'Sessions'
              } for s in p.session_set.all()]

    return HttpResponse(json.dumps({"success" : "ok"
                                  , "proposals" : js
                                   })
                      , content_type = 'application/json')

@login_required
@admin_only
def import_proposals(request, *args, **kws):
    if request.method == 'POST':
        pst = PstImport()
        for pcode in request.POST.getlist('proposals'):
            pst.importProposal(pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/'))
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
def get_options(request, *args, **kws):
    "Depending on mode, returns various options"
    mode = request.GET.get("mode", None)
    if mode == "proposal_codes":
        ps = Proposal.objects.all().order_by('pcode')
        pcodes = [{'id' : p.id, 'pcode' : p.pcode} for p in ps]
        return HttpResponse(json.dumps({"success" : "ok" , 'proposal codes' : pcodes })
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
    return HttpResponse(json.dumps({"success" : "ok", "info" : pst.getUserInfo(person_id)})
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
