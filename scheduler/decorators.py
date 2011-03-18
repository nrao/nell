from nell.utilities.FormatExceptionInfo import JSONExceptionInfo

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

