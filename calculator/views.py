from decorators       import catch_json_parse_errors
from django.http      import HttpResponse
from utilities.Result import Result
from utilities.common import *

import simplejson as json

@catch_json_parse_errors
def get_result(request, *args, **kwds):
    result = request.session.get('SC_result', {}) or {}
    result['success'] = 'ok'
    return HttpResponse(json.dumps(result), mimetype = "text/plain")

#@catch_json_parse_errors
def set_terms(request, *args, **kwds):
    #SPECIAL_VALUES = ('trimester', 'conversionType', 'units')
    SPECIAL_VALUES = ()
    retval         = {}

    if request.method == 'POST': 

        # Start with what we already know.
        result    = Result('equations')
        sc_result = request.session.get('SC_result', {}) or {}
        for term, value in sc_result.items():
            if term not in SPECIAL_VALUES:
                result.set(term, value[0])

        # GXT returns lists for single values for some reason. Eew.
        info = {}
        for key, value in dict(request.POST).items():
            if '-hidden' not in key:
                info[key] = value[0] 
            elif '-' in key and key.split('-')[0] in getHWList():
                new_key, _ = key.split('-')
                info[new_key] = value[0]

        # Process special values.
        for value in SPECIAL_VALUES:
            if info.has_key(value):
                request.session['SC_' + value] = info.pop(value)

        # Process terms.
        for term, raw_value in info.items():

            try:
                value = float(raw_value)
            except ValueError:
                value = raw_value
            if value == "NOTHING":
                value = None
            result.set(term, value)

        # Squirrel away, send back, and clean up.
        request.session['SC_result'] = result.get()
        getMinIntegrationTime(request)
        #request.session['SC_result'].update(
        #    dict(trimester = (request.session.get('SC_trimester', ''), '', '')))
        try:
            result.__del__()
        except:
            pass

        retval = request.session['SC_result'].copy()
        retval.update(success = 'ok')

    return HttpResponse(json.dumps(retval), mimetype = "text/plain")

def initiateHardware(request):
    backends = getOptions({},'backend')
    selected = {'backend' : backends[0] if len(backends) > 0 else None}
    request.session['SC_backend'] = selected['backend']
    result = setHardwareConfig(request, selected, 'backend')
    result.update(backend = backends, success = 'ok')
    return HttpResponse(json.dumps(result), mimetype = "text/plain")

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

def reset(request):
    #request.session.update(initiate(request))
    #  TBF:  Temporary
    for k, v in request.session.items():
        if 'SC_' in k:
            request.session.update({k: None})
    return get_result(request)

