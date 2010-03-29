from django_restapi.resource  import Resource
from django.http              import HttpResponse, HttpResponseRedirect

from sesshuns.models          import first

import simplejson as json
import reversion
from reversion import revision

class NellResource(Resource):
    def __init__(self, dbobject, *args, **kws):
        self.dbobject = dbobject
        super(NellResource, self).__init__(*args, **kws)

    def create(self, request, *args, **kws):
        method = request.POST.get("_method", None)
        if method == "put":
            return self.update(request, *args, **kws)
        elif method == "delete":
            return self.delete(request, *args, **kws)
        else:
            return self.create_worker(request, *args, **kws)

    def get_rev_comment(self, request, obj, method):
       
        where = "%s %s" % (obj.__class__.__name__, method)
        who = "nell" # TBF: see if a user is logged in
        return "WHO: %s, WHERE: %s" % (who, where)

    @revision.create_on_success 
    def create_worker(self, request, *args, **kws):
        o = self.dbobject()
        o.init_from_post(request.POST)
        # Query the database to insure data is in the correct data type
        o = first(self.dbobject.objects.filter(id = o.id))
    
        revision.comment = self.get_rev_comment(request, o, "create_worker")

        return HttpResponse(json.dumps(o.jsondict())
                          , mimetype = "text/plain")

    @revision.create_on_success 
    def update(self, request, *args, **kws):
        id    = int(args[0])
        o     = self.dbobject.objects.get(id = id)
        o.update_from_post(request.POST)

        revision.comment = self.get_rev_comment(request, o, "update")

        # NOTE: this originally returned "", but if we want JSON callbacks
        # to work from GWT, need A response.  This change seems benign
        #return HttpResponse("")
        return HttpResponse(json.dumps({"success" : "ok"})
                          , mimetype = "text/plain")

    @revision.create_on_success 
    def delete(self, request, *args):
        id = int(args[0])
        o  = self.dbobject.objects.get(id = id)
        revision.comment = self.get_rev_comment(request, o, "delete")
        o.delete()
        

        return HttpResponse(json.dumps({"success": "ok"}))

