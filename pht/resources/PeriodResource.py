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

from django.http import HttpResponse
import simplejson as json

from Resource         import Resource
from pht.httpadapters import PeriodHttpAdapter
from pht.models       import Period

class PeriodResource(Resource):

    def __init__(self):
        self.root    = 'periods'
        self.adapter = PeriodHttpAdapter()

    def read(self, request, *args, **kws):
        if len(args) == 1:
            id,      = args
            adapter  = PeriodHttpAdapter(Period.objects.get(id = id))
            return HttpResponse(json.dumps(adapter.jsonDict())
                              , content_type = 'application/json')
        else:
            periods = Period.objects.all().order_by('start')
            return HttpResponse(json.dumps({"success" : "ok"
                                          , "periods" : [PeriodHttpAdapter(p).jsonDict() for p in periods]
                                           })
                              , content_type = 'application/json')

    def update(self, request, *args, **kws):
        id,      = args
        adapter  = PeriodHttpAdapter(Period.objects.get(id = id))
        adapter.updateFromPost(json.loads(request.raw_post_data))
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')

    def delete(self, request, *args, **kws):
        id,    = args
        period = Period.objects.get(id = id)
        period.delete()
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')
