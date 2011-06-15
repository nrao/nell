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

from django.db.models         import Q, Min
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from scheduler.models       import Elective
from utilities.TimeAgent        import str2dt
from scheduler.httpadapters import ElectiveHttpAdapter
from datetime              import datetime, timedelta, date

import simplejson as json

jsonMap = { "id" : "id"
          , "handle" : "session__name"
          , "complete" : "complete"
          }
    
class ElectiveResource(NellResource):
    def __init__(self, *args, **kws):
        super(ElectiveResource, self).__init__(Elective, ElectiveHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(ElectiveResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):

        # one or many?
        if len(args) == 0:
            # many, use filters
            query_set = Elective.objects

            filterComplete = request.GET.get("filterComplete", None)
            if filterComplete is not None:
                query_set = query_set.filter(complete = (filterComplete == "true"))

            filterSession = request.GET.get("filterSession", None)
            if filterSession is not None:
                query_set = query_set.filter(session__name = filterSession)

            filterSessionId = request.GET.get("filterSessionId", None)
            if filterSessionId is not None:
                query_set = query_set.filter(session__id = filterSessionId)

            # see if there is a sort field passed to us
            if request.GET.get("sortField", None) is not None:
                sortField = jsonMap.get(request.GET.get("sortField", "handle"), "id")
                order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""             
                es = query_set.order_by(order + sortField)
            else:
                # by default, sort by the earliest period's start
                es = query_set.annotate(elec_start=Min('periods__start')).\
                      order_by('elec_start').distinct()

            total = len(es)
            offset = int(request.GET.get("offset", 0))
            limit  = int(request.GET.get("limit", -1))
            if limit != -1:
                es = es[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                 , electives = [ElectiveHttpAdapter(e).jsondict() for e in es]))
            , content_type = "application/json")
        else:
            # one, identified by id in arg list
            e_id = args[0]
            elective = Elective.objects.get(id = e_id)
            return HttpResponse(json.dumps(dict(elective = ElectiveHttpAdapter(elective).jsondict()))
                              , content_type = "application/json")


