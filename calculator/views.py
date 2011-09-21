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
    """
    Instead of producing a viewable HTML file, this takes the same
    results and presents them in a simple text file format that
    is downloaded from the client browser.
    """
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
    """
    Produces stand-alone HTML page viewable from the browser that
    uses the same HTML template as what is used to produce the 
    HTML in the calculator's results tab.
    """
    return render_to_response("results.html", get_results_dict(request))

#@login_required
def get_results(request, *args, **kwds):
    """
    Produces the same results that the other *_results methods do, 
    except here we just return the raw JSON.
    """
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

