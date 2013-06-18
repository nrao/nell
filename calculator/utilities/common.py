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

from django.db.models         import Q
from calculator.models        import *
from functions                import isNotVisible
from utilities.TimeAgent      import *

# View utility functions go here.

def get_results_dict(request):
    """
    Takes the results that are squirrled away in the cookie, and formats
    it properly for use in the HTML to be rendered.
    """

    explicit, leftovers, input = splitResults(request)
    #for l in leftovers:
    #    print l

    # filter out leftovers that don't have a display
    leftovers = [r for r in leftovers if r['display'] is not None]
    # so that you can then sort the leftovers by the second half of
    # their display, and convert the values to strings
    leftovers = [sanitize(r) for r in sorted(leftovers, key = lambda r: r['display'][1]) 
                      if r['value'] is not None]
    # convert everything else to strings too
    input     = map(sanitize, input)
    explicit  = map(sanitize, explicit)

    # The next two dicts are created for easy display in the rendered HTML
    # Take the list of dictionaries, and make a new one, keyed off of term
    explicit  = dict([splitKey(e) for e in explicit])
    # Also make a dict of the inputs for desiding on how to display stuff.
    ivalues   = dict([splitKey(i) for i in input])

    #print ivalues.get('effective_bw'), ivalues.get('duty_cycle')

    # create a small custom dictionary to handle a few units issues
    units     = {}
    sensitivity_units        = ivalues.get('units', {}).get('value')
    if sensitivity_units is not None:
        units['sigma']           = 'mJy' if sensitivity_units == 'flux' else 'mK'
        explicit['confusion_limit']['units']= "%s (%s)" % ('S' if sensitivity_units == 'flux' else sensitivity_units.title(), units['sigma'])
    units['t_tot_units'] = 's' if ':' not in explicit.get('t_tot', {}).get('value', '') else 'HH:MM:SS.S'

    # error checking and such
    msgs = getMessages(request)

    return {'e'         : explicit
          , 'leftovers' : leftovers
          , 'input'     : input
          , 'ivalues'   : ivalues
          , 'units'     : units
          , 'messages'  : msgs
          }

def splitResults(request, debug = False):
    """
    Takes the current SC_result found in the cookie (request.session)
    and splits thme into different lists, all of which are lists
    of a dictionary encapsulating a Term object.
    The different lists include those things that were originally just
    user input, and then different types of derived results: explict
    and leftovers.  Explicits are the main things that we worry about
    in this calculatory, and have dedicated displays.  Leftovers is 
    all the other stuff, which get displayed in a more generic manner.
    """

    exceptions = ('topocentric_freq', 'smoothing_resolution')

    explicit, leftovers, input, debug_results = [], [], [], []
    # split up the calculator results into differet lists of dictionary
    # representations of a Term object
    for k, (v, u, e, l, d) in request.session.get('SC_result', {}).items(): 
        data = {'term' : k
              , 'value' : v
              , 'units' : u
              , 'equation' : e
              , 'label'    : l
              , 'display'  : d
                }
        # The second part of the display decides what type of result it is
        # A priority of 1 makes it EXPLICIT
        if (e != '' or k in exceptions) and d is not None and d[1] == 1:
            explicit.append(data)
        # everything else is a leftover, to be treated accordingly    
        elif (e != '' or k in exceptions) and d is not None and d[1] > 1:
            leftovers.append(data)
        # if the original equation was blank, it must be user input    
        elif e == '' and k not in exceptions:
            input.append(data)
        else:
            debug_results.append(data)

    if debug:
        leftovers += debug_results

    return explicit, leftovers, input

def sanitize(result):
    """
    Attempts to convert the value of the given result from it's current
    form (most likely a float), into a string representation, using the
    first part of the display of the given result.
    """
    v = result.get('value')
    u = result.get('units')
    d = result.get('display')
    t = result.get('term')
    result['units'] = '' if u is None else u
    # try and convert the float value to a string rep. using
    # the first part of the display from equations.cfg
    if v is not None and v != '' and d is not None and d[0] != '':
        try:
            result['value'] = ("%" + d[0]) % float(v)
        except:
            pass
    if v is None:
        result['value'] = ''
    # special handling of time formatting    
    if v is not None and v != '' and t is not None and (t == 'time' or t == 't_tot' or u == 's'):
        try:
            time = float(v)
        except ValueError:
            time = sex2float(v)
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
        elif time >= 1:
            result['value'] = "%.1f" % time
        elif time <= 0.01:
            result['value'] = "%4.3g" % time

    return result

def splitKey(e):
    k = e.pop('term')
    return k, sanitize(e)

def getMessages(request):
    """
    Examines the current results, looks for possible problems,
    and returns snotty messages for each problem found.
    Each message also includes a type (ie, Error, Warning)
    """

    # TBF: isn't this redundant? why not pass these in?
    explicit, leftovers, input = splitResults(request)

    # Convert the list of dictionaries, to a dictionary keyed by term
    results = dict([splitKey(r) for r in explicit + leftovers])
    ivalues = dict([splitKey(i) for i in input])

    messages = []

    # All right, slog through each problem child, and check on them

    # source not visible?
    min_elevation =  ivalues.get("min_elevation", {}).get("value", 1)
    dec = ivalues.get("declination", {}).get("value", 0)
    if dec != '' and min_elevation != '' and \
        isNotVisible(float(dec), float(min_elevation)):
        messages.append({'type' : 'Error'
                       , 'msg'  : 'Source will never rise above min elevation.'
                        })

    # source diameter
    diameter = results.get("source_diameter", {}).get("value", 1)
    if diameter != '' and float(diameter) > 0:
        messages.append({'type' : 'Warning', 'msg' : 'Since source is extended, the calculated results are approximations.'})

    # declination too low?   
    if dec != '' and float(dec) < -46:
        messages.append({'type' : 'Error', 'msg' : 'Source Declination is below -46, the lower limit for the GBT.'})

    # frequency out of bound?    
    rx        = ivalues.get('receiver', {}).get('value')
    topo_freq = results.get('topocentric_freq', {}).get('value', 0)
    if rx is not None and rx != '' and rx != 'NA' and topo_freq != '':
        _, v = rx.split('(')
        rx_low, rx_hi = map(float, v.replace(" GHz)", '').split(' - ') )
        rx_low, rx_hi = float(rx_low), float(rx_hi)
        topo_freq = round(float(topo_freq) * 1e-3, 3)
        if not (topo_freq >= rx_low and topo_freq <= rx_hi):
            messages.append({'type' : 'Warning', 'msg' : 'Topocentric frequnecy is beyond the nominal range for the selected receiver.'})

    mode       = ivalues.get('mode', {}).get('value')
    if mode != 'Pulsar':
        # sensitivity vs. confusion limit?
        sensitivity = results.get("sigma", {}).get("value")
        confusion_limit = results.get("confusion_limit", {}).get("value")
        if sensitivity != '' and confusion_limit != '' and sensitivity < confusion_limit:
            messages.append({'type' : 'Warning', 'msg' : 'Sensitivity is less than the confusion limit.'})

    if mode == 'Continuum':
        # 1/F gain variations?
        backend    = ivalues.get('backend', {}).get('value')
        bandwidth  = ivalues.get('bw', {}).get('value')
        time       = ivalues.get('time', {}).get('value')
        conversion = ivalues.get('conversion', {}).get('value')
        t_tot      = results.get('t_tot', {}).get('value')
        msg = {'type' : 'Warning', 'msg' : 'Time*(Bandwidth resolution) exceeds the suggested limit for 1/F gain variations.  Advanced observing techniques may be required to reach your scientific goals.  Please address this issue in your technical justification.'}
        if rx != '' and bandwidth != '' and time != '' and t_tot != '' and conversion != '' and None not in (rx, bandwidth, time, t_tot, conversion):
            # check for exceeding limit
            limit = sex2float(time) * float(bandwidth) if conversion == 'Time to Sensitivity' else \
                    sex2float(t_tot) * float(bandwidth)
            checks = [(backend == 'Mustang 1.5' and limit >= 1e5)
                    , (backend == 'Caltech Continuum Backend' and 'Ka' in rx and limit >= 3.5e4)
                    , (("3" in rx or "4" in rx or "6" in rx or "8" in rx) and limit >= 20)
                    , ("A" in rx and limit >= 400)
                    , ("L" in rx and limit >= 730)
                    , ("S" in rx and limit >= 160)
                    , ("C" in rx and limit >= 40)
                    , ("X" in rx and limit >= 210)
                    , (("U" in rx or "D" in rx) and limit >= 400)
                    , ("KFPA" in rx and limit >= 370)
                    , (("B1" in rx or "B2" in rx or "B3" in rx) and limit >= 400)
                    , ("Q" in rx and limit >= 590)
                    , (("W1" in rx or "W2" in rx or "W3" in rx or "W4" in rx) and limit >= 770)
                    ]
            for check in checks:
                if check:
                    messages.append(msg)
                    break

    # Frequency resolution
    k2 = results.get("k2", {}).get("value", 1)
    bandwidth  = ivalues.get('bw', {}).get('value')
    minTopoFreq = results.get("min_topo_freq", {}).get("value", 1)
    if k2 != '' and bandwidth != '' and minTopoFreq != '' and float(bandwidth)/float(minTopoFreq) < float(k2):
        messages.append({'type' : 'Error', 'msg' : 'Desired frequency or velocity resolution is smaller than what the backend can provide.'})

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
                #print "Q(%s__%s__contains='%s')" % (k, column, value)
    config  = config.values(result).distinct()
    if result == 'receiver':
        answers = [getName(result, c[result]) for c in config.order_by('receiver__band_low')]
    else:
        answers = [getName(result, c[result]) for c in config]
        try:
            answers = map(int, answers)
        except:
            pass
        answers.sort()
    if result == "mode" and 'Spectral Line' in answers:
        answers.reverse()
    return answers

def setHardwareConfig(request, selected):
    #returns dictionary of option lists for all hardware 
    config = {}
    filterDict = {}
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
                selected[i] = getRxValue(request.session['SC_' + i]) if i == 'receiver' \
                      else request.session['SC_' + i]
            else:
                selected[i] = getRxValue(config[i][0]) if i == 'receiver' else config[i][0]
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

def sex2float(value):
    try:
        if value == '' or value is None:
            return value
        elif ':' not in value:
            return float(value)
    except TypeError:
        return value
    values = value.split(":")
    hour   = values[0]
    if len(values) == 3:
        minute = (float(values[1]) + float(values[2]) / 3600.) / 60.
    elif len(values) == 2:
        minute = float(values[1]) / 60.
    else:
        return value
    return -1 * (float(hour[1:]) + minute) if '-' in hour else float(hour) + minute

def validate(key, value):
    if value is None or value == '':
        return value
    if key in ('right_ascension'):
        return sex2float(value)
    else:
        return value
