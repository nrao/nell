from django.db.models import Q
from calculator.models        import *

# View utility functions go here.

def get_results_dict(request):
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
    return {'e'         : explicit
          , 'leftovers' : leftovers
          , 'input'     : input
          , 'ivalues'   : ivalues
          , 'units'     : units
          , 'messages'  : getMessages(request)
          }

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
            result['value'] = "%02d:%02d:%04.1f" % (hr, mi, sec)
        elif time >= 60:
            mi = time / 60.
            sec = (mi - int(mi)) * 60
            mi  = int(mi)
            result['value'] = "00:%02d:%04.1f" % (mi, sec)

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

def getHWList():
    return ['backend','mode','receiver','beams','polarization'
               ,'bandwidth','windows','switching']

def getDBName(hw, v):
    if hw != "receiver":
        return 'name', v
    else:
        value = v.split(" (")
        return ('display_name', value[0] if len(value) > 0 else v)

def getOptions(filter, result):
    config = Configuration.objects.all()
    if result != 'backend':
        for k,v in filter.items():                                       
            #chain filters
            if v != 'NOTHING':
                column = 'name'
                value  = v
                config = config.filter(eval("Q(%s__%s__contains='%s')" % (k, column, value)))
    config  = config.values(result).distinct()
    if result == 'receiver':
        answers = [getName(result, c[result]) for c in config.order_by('receiver__dss_receiver')]
    else:
        answers = [getName(result, c[result]) for c in config]
        answers.sort()
    if result == "mode" and 'Spectral Line' in answers:
        answers.reverse()
    return answers

def setHardwareConfig(request, selected, newPick=None):
    #returns dictionary of option lists for all hardware 
    config = {}
    filterDict = {}
    if not newPick: #hardware hasn't changed dont return anything
        return config
    selected_keys = selected.keys()
    hardwareList  = [h for h in getHWList() if h not in selected_keys]
    for i in hardwareList:
        #Get valid list for hardware i given selected
        config[i] = getOptions(selected,i)

        #ERROR nothing matches in the database with given filter
        if len(config[i]) == 0:
            config[i].append("NOTHING")
        if not selected.has_key(i) or selected[i] not in config[i]:
            if request.session.has_key('SC_' + i) and \
               request.session['SC_' + i] in config[i]:
                #if user already has valid choice keep it
                selected[i] = request.session['SC_' + i]
            else:
                selected[i] = config[i][0]
                request.session['SC_' + i] = config[i][0]
    return config

def getRxValue(value):
    try:
        name, raw_range = value.split(" (")
        low, hi         = map(float, raw_range.replace(" GHz)", "").split(" - "))
        rx              = Receiver.objects.get(display_name = name, band_low = low, band_hi = hi)
        name            = rx.name
    except:
        name = value
    return name

def getBackendValue(value):
    results = Calc_Backend.objects.filter(dss_backend__name = value)
    if len(results) > 0:
        return results[0].name
    return value

def getValue(key, value):
    if key == 'receiver':
        return getRxValue(value)
    elif key == 'backend':
        return getBackendValue(value)
    return value

def getMinIntegrationTime(request):
    hardware = [(k, v[0]) for k, v in request.session['SC_result'].iteritems() if k in getHWList()]
    filter = {}
    for k, v in hardware:
        filter[k] = getValue(k, v) if k == 'receiver' or k == 'backend' else v
    min_int = ', '.join(getOptions(filter, 'integration'))
    request.session['SC_result']['min_integration'] = (min_int, None, '', '', None)

def validate(key, value):
    if value is None or value == '':
        return value
    if key in ('declination', 'right_ascension'):
        values = value.split(":")
        hour   = values[0]
        if len(values) == 3:
            minute = (float(values[1]) + float(values[2]) / 3600.) / 60.
        elif len(values) == 2:
            minute = float(values[1]) / 60.
        else:
            return value
        return -1 * (float(hour[1:]) + minute) if '-' in hour else float(hour) + minute
    else:
        return value
