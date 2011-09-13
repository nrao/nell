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

from django_restapi.resource  import Resource
from django.http              import HttpResponse, HttpResponseRedirect
from django.shortcuts         import get_object_or_404

from utilities.FormatExceptionInfo import formatExceptionInfo
from users.utilities            import get_requestor

import simplejson as json
import reversion
from reversion import revision

class NellResource(Resource):
    def __init__(self, dbobject, adapter, *args, **kws):
        self.dbobject = dbobject
        self.adapter  = adapter(None)
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
        who   = get_requestor(request)
        return "WHO: %s, WHERE: %s" % (who, where)

    @revision.create_on_success 
    def create_worker(self, request, *args, **kws):
        o = self.dbobject()
        self.adapter.load(o)
        self.adapter.init_from_post(request.POST)
        # Query the database to insure data is in the correct data type
        o = self.dbobject.objects.get(id = o.id)
        self.adapter.load(o)
    
        revision.comment = self.get_rev_comment(request, o, "create_worker")

        return HttpResponse(json.dumps(self.adapter.jsondict())
                          , mimetype = "text/plain")

    @revision.create_on_success 
    def update(self, request, *args, **kws):
        id    = int(args[0])
        o     = get_object_or_404(self.dbobject, pk = id)
        self.adapter.load(o)

        error = None
        try:
            self.adapter.update_from_post(request.POST)
        except:
            e, m, t = formatExceptionInfo()
            error = ": ".join((e, m))

        revision.comment = self.get_rev_comment(request, o, "update")

        # NOTE: this originally returned "", but if we want JSON callbacks
        # to work from GWT, need A response.  This change seems benign
        response = {"success" : "ok"}
        if error:
            response.update({"error" : error})
        return HttpResponse(json.dumps(response)
                          , mimetype = "text/plain")

    @revision.create_on_success 
    def delete(self, request, *args):
        id = int(args[0])
        o  = self.dbobject.objects.get(id = id)
        revision.comment = self.get_rev_comment(request, o, "delete")
        o.delete()
        

        return HttpResponse(json.dumps({"success": "ok"}))

