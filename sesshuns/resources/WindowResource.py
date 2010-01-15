from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from sesshuns.models       import Window, first

import simplejson as json

class WindowResource(NellResource):
    def __init__(self, *args, **kws):
        super(WindowResource, self).__init__(Window, *args, **kws)

    def create(self, request, *args, **kws):
        return super(WindowResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        # one or many?
        #if len(args) == 0:
            # one, identified by id
        w_id = args[0]
        window = first(Window.objects.filter(id = w_id))
        return HttpResponse(json.dumps(dict(window = window.jsondict()))
                          , content_type = "application/json")


