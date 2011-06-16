from django.contrib.auth.decorators import login_required
from django.http      import HttpResponse
from django.shortcuts               import render_to_response, render
from decorators       import catch_json_parse_errors
from utilities.Result import Result
from utilities.common import *
import settings

import simplejson as json
import time

def text_results(request):
    response = render(request
                    , "results.txt"
                    , get_results_dict(request)
                    , content_type = 'text/plain')
    response['Content-Disposition'] = 'attachment; filename=results.txt'
    return response

@login_required
def load_calc_ui(request):
    return render_to_response("war/Calculator_ui.html", {})

#@login_required
def display_results(request):
    return render_to_response("results.html", get_results_dict(request))

#@login_required
def get_results(request, *args, **kwds):
    explicit, leftovers, input = splitResults(request, debug = True)
    results = explicit + leftovers
    retval = {'success'       : 'ok'
            , 'results'       : results
            , 'total_results' : len(results)
            , 'input'         : input
            , 'total_input'   : len(input)
             }

    return HttpResponse(json.dumps(retval), mimetype = "application/json")

#@login_required
def set_terms(request, *args, **kwds):
    retval         = {}

    if request.method == 'POST': 
        # Start with what we already know.
        result    = Result('equations')
        sc_result = request.session.get('SC_result', {}) or {}
        for term, value in sc_result.items():
            result.set(term, value[0])

        # GXT returns lists for single values for some reason. Eew.
        info = {}
        for key, value in dict(request.POST).items():
            if '-hidden' not in key:
                info[key] = validate(key, value[0])
            elif '-' in key and key.split('-')[0] in getHWList():
                new_key, _ = key.split('-')
                info[new_key] = validate(new_key, value[0])

        if request.session.get('SC_input') is not None:
            request.session['SC_input'].update(info)
        else:
            request.session['SC_input'] = info

        # Process terms.
        for term, raw_value in info.items():
            try:
                value = float(raw_value)
            except ValueError:
                value = raw_value == 'true' or raw_value
            if raw_value == "NOTHING" or raw_value == u'':
                value = None
            result.set(term, value)
        
        # Process unchecked checkbox
        if 'smoothing' in info.keys() and 'avg_pol' not in info.keys():
            result.set('avg_pol', False)
        if 'smoothing' in info.keys() and 'diff_signal' not in info.keys():
            result.set('diff_signal', False)

        # Squirrel away, send back, and clean up.
        request.session['SC_result'] = result.get()
        #getMinIntegrationTime(request)
        try:
            result.__del__()
        except:
            pass

        retval = request.session['SC_result'].copy()
        retval.update(success = 'ok')

    return HttpResponse(json.dumps(retval), mimetype = "text/plain")

#@login_required
def initiateHardware(request):
    request.session['SC_result'] = {}
    backends = getOptions({},'backend')
    selected = {'backend' : backends[0] if len(backends) > 0 else None}
    request.session['SC_backend'] = selected['backend']
    result = setHardwareConfig(request, selected, 'backend')
    result.update(backend = backends, success = 'ok')
    return HttpResponse(json.dumps(result), mimetype = "text/plain")

#@login_required
def setHardware(request):
    selected = {}
    newPick = None  
    if request.method == "POST":
        for k in getHWList(): 
            #add term to the filter selected
            v = None
            if request.POST.has_key(k) and request.session.has_key("SC_" + k):
                v = request.POST[k]
                selected[k] = getValue(k, v) if k == 'receiver' or k == 'backend' else v
            #new change,  stop add this to the filter then stop
            if not newPick and v != request.session.get("SC_" + k):
                newPick = k
                request.session["SC_" + k] = v
                break
    result = setHardwareConfig(request, selected, newPick)
    result.update(success = 'ok')
    return HttpResponse(json.dumps(result), mimetype = "text/plain")

