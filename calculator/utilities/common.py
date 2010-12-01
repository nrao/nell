from django.db.models import Q
from calculator.models        import *

def getHWList():
    return ['backend','mode','receiver','beams','polarization'
               ,'bandwidth','windows','integration','switching']

def getOptions(filter, result):
    config = Configuration.objects.all()
    if result != 'backend':
        for k,v in filter.items():                                       
            #chain filters
            config = config.filter(eval("Q(%s__name__contains='%s')" % (k,v)))
    config  = config.values(result).distinct()
    answers = [getName(result, c[result]) for c in config]
    answers.sort()
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

def getRxName(rx):
    try:
        name, range = rx.split(" (")
    except:
        name = rx
    return name

