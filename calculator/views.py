from decorators       import catch_json_parse_errors
from django.http      import HttpResponse
from django.shortcuts               import render_to_response
from utilities.Result import Result
from utilities.common import *

import simplejson as json
import time

def splitResults(request, debug = False):
    exceptions = ('topocentric_freq', 'smoothing_resolution')

    explicit, leftovers, input, debug_results = [], [], [], []
    for k, (v, u, e, l, d) in request.session.get('SC_result', {}).items(): 
        data = {'term' : k
              , 'value' : v
              , 'units' : u
              , 'equation' : e
              , 'label'    : l
              , 'display'  : d
                }
        if (e != '' or k in exceptions) and d is not None and d[1] == 1:
            explicit.append(data)
        elif (e != '' or k in exceptions) and d is not None and d[1] > 1:
            leftovers.append(data)
        elif e == '' and k not in exceptions:
            input.append(data)
        else:
            debug_results.append(data)

    if debug:
        leftovers += debug_results
    return explicit, leftovers, input

def sanitize(result):
    v = result.get('value')
    u = result.get('units')
    d = result.get('display')
    t = result.get('term')
    result['units'] = '' if u is None else u
    if v is not None and v != '' and d is not None and d[0] != '':
        try:
            result['value'] = ("%" + d[0]) % float(v)
        except:
            pass
    if v is None:
        result['value'] = ''
    if v is not None and (t == 'time' or t == 't_tot'):
        time = float(v)
        if time > 3600:
            hr = time / 3600.
            mi = (hr - int(hr)) * 60
            hr = int(hr)
            sec = (mi - int(mi)) * 60
            mi  = int(mi)
            result['value'] = "%s:%s:%.3f" % (hr, mi, sec)
        elif time >= 60:
            mi = time / 60.
            sec = (mi - int(mi)) * 60
            mi  = int(mi)
            result['value'] = "%s:%.3f" % (mi, sec)

    return result

def splitKey(e):
    k = e.pop('term')
    return k, sanitize(e)

def getMessages(request):
    explicit, leftovers, input = splitResults(request)
    results = dict([splitKey(r) for r in explicit + leftovers])
    ivalues = dict([splitKey(i) for i in input])

    messages = []
    diameter = results.get("source_diameter", {}).get("value", 1)
    if diameter != '' and float(diameter) > 0:
        messages.append({'type' : 'Warning', 'msg' : 'Since source is extended, the calculated results are approximations.'})
    dec = ivalues.get("declination", {}).get("value", 0)
    if dec != '' and float(dec) < -46:
        messages.append({'type' : 'Error', 'msg' : 'Source Declination is below -46, the lower limit for the GBT.'})
    rx        = ivalues.get('receiver', {}).get('value')
    topo_freq = results.get('topocentric_freq', {}).get('value', 0)
    if rx is not None and rx != '' and topo_freq != '':
        _, v = rx.split('(')
        rx_low, rx_hi = map(float, v.replace(" GHz)", '').split(' - ') )
        rx_low, rx_hi = float(rx_low), float(rx_hi)
        topo_freq = round(float(topo_freq) * 1e-3, 3)
        if not (topo_freq >= rx_low and topo_freq <= rx_hi):
            messages.append({'type' : 'Warning', 'msg' : 'Topocentric frequnecy is beyond the nominal range for the selected receiver.'})

    sensitivity = results.get("sigma", {}).get("value")
    confusion_limit = results.get("confusion_limit", {}).get("value")
    if sensitivity != '' and confusion_limit != '' and sensitivity < confusion_limit:
        messages.append({'type' : 'Warning', 'msg' : 'Sensitivity is less than the confusion limit.'})
    backend    = ivalues.get('backend', {}).get('value')
    bandwidth  = ivalues.get('bandwidth', {}).get('value')
    time       = ivalues.get('time', {}).get('value')
    conversion = ivalues.get('conversion', {}).get('value')
    t_tot      = results.get('t_tot', {}).get('value')
    msg = {'type' : 'Warning', 'msg' : 'Time*Bandwidth exceeds the suggested limit from 1/F gain variations of . Please justify how you plan on observing beyond that limit.'}
    if rx != '' and bandwidth != '' and time != '' and t_tot != '' and conversion != '' and None not in (rx, bandwidth, time, t_tot, conversion):
        limit = float(time) * float(bandwidth) if conversion == 'Time to Sensitivity' else \
                float(t_tot) * float(bandwidth)
        if backend == 'Mustang' and limit >= 1e11:
            messages.append(msg)
        elif backend == 'Caltech Continuum Backend' and 'Ka' in rx and limit >= 1e11:
            messages.append(msg)
        elif limit >= 1e9:
            messages.append(msg)

    return messages

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
    units     = 'mJy' if ivalues.get('units', {}).get('value') == 'flux' else 'mK'
    return render_to_response("results.html", {'e'         : explicit
                                             , 'leftovers' : leftovers
                                             , 'input'     : input
                                             , 'ivalues'   : ivalues
                                             , 'units'     : units
                                             , 'messages'  : getMessages(request)
                                             })

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

def initiateHardware(request):
    request.session['SC_result'] = {}
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

