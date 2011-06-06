from django.contrib.auth.decorators import login_required
from django.http      import HttpResponse
from django.shortcuts               import render_to_response
from decorators       import catch_json_parse_errors
from utilities.Result import Result
from utilities.common import *
import settings

import simplejson as json
import time

@login_required
def load_calc_ui(request):
    return render_to_response("war/Calculator_ui.html", {})

#@login_required
def display_results(request):
    explicit, leftovers, input = splitResults(request)
    leftovers = [r for r in leftovers if r['display'] is not None]
    leftovers = [sanitize(r) for r in sorted(leftovers, key = lambda r: r['display'][1]) 
                      if r['value'] is not None]
    input     = map(sanitize, input)
    explicit  = map(sanitize, explicit)
    explicit  = dict([splitKey(e) for e in explicit])
    # Also make a dict of the inputs for desiding on how to display stuff.
    ivalues   = dict([splitKey(i) for i in input])
    units     = {}
    units['sigma']       = 'mJy' if ivalues.get('units', {}).get('value') == 'flux' else 'mK'
    units['t_tot_units'] = 's' if ':' not in explicit.get('t_tot', {}).get('value', '') else 'HH:MM:SS.S'
    return render_to_response("results.html", {'e'         : explicit
                                             , 'leftovers' : leftovers
                                             , 'input'     : input
                                             , 'ivalues'   : ivalues
                                             , 'units'     : units
                                             , 'messages'  : getMessages(request)
                                             })

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

