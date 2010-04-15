import sys
import traceback

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
