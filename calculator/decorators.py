import sys
import traceback
from django.http import HttpResponse
import inspect
import simplejson as json

def formatExceptionInfo(maxTBlevel=5):
    """
    Obtains information from the last exception thrown and extracts
    the exception name, data and traceback, returning them in a tuple
    (string, string, [string, string, ...]).  The traceback is a list
    which will be 'maxTBlevel' deep.
    """
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    excArgs = exc.__str__()
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

def printException(formattedException):
    """
    Takes the tuple provided by 'formatExceptionInfo' and prints it
    out exactly as an uncaught exception would be in an interactive
    python shell.
    """
    print "Traceback (most recent call last):"

    for i in formattedException[2]:
        print i,

    print "%s: %s" % (formattedException[0], formattedException[1])

def exceptionJSONdict(formattedException):
    jd = {"exception_type"      : formattedException[0],
          "exception_args"      : formattedException[1],
          "exception_traceback" : formattedException[2]}
    return jd

def JSONExceptionInfo(msg = None):
    print "in JSONExceptionInfo"
    jd = exceptionJSONdict(formatExceptionInfo()) # get this first, in case of trouble below

    try:
        frame = inspect.currentframe()            # the stack frame for this function
        oframes = inspect.getouterframes(frame)   # the list of frames leading to call of this function
        caller = oframes[1]                       # We're interested in the caller of this function
        fname = caller[3]                         # Calling function's name

        if msg == None:
            msg = 'Uncaught exception in'
    except:
        msg   = "Oops, error in JSONExceptionInfo, can't process error!"
        fname = ""
    finally:
        del frame
        del oframes

    return HttpResponse(json.dumps({'error': '%s %s' % (msg, fname),
                                      'exception_data': jd}), mimetype = "text/plain")

def catch_json_parse_errors(view_func):
    """
    Wrapper for functions that may generate a JSON parse error. Allows
    for graceful debugging. :-)
    """
    def decorate(request, *args, **kwds):
        try:
            return view_func(request, *args, **kwds)
        except:
            return JSONExceptionInfo()
    return decorate
