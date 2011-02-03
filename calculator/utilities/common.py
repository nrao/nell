from django.db.models import Q
from calculator.models        import *
from sesshuns.models          import first

def getHWList():
    return ['backend','mode','receiver','beams','polarization'
               ,'bandwidth','windows','switching']

def getOptions(filter, result):
    config = Configuration.objects.all()
    if result != 'backend':
        for k,v in filter.items():                                       
            #chain filters
            config = config.filter(eval("Q(%s__name__contains='%s')" % (k,v)))
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
        name, range = value.split(" (")
        rx          = first(Receiver.objects.filter(display_name = name))
        name        = rx.name
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

