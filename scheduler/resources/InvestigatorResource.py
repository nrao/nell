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

from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect, Http404

from NellResource          import NellResource
from scheduler.models       import Investigator
from scheduler.httpadapters import InvestigatorHttpAdapter

import simplejson as json

class InvestigatorResource(NellResource):
    def __init__(self, *args, **kws):
        super(InvestigatorResource, self).__init__(Investigator, InvestigatorHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(InvestigatorResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        try:
            # using brakets because we want a key error if its not there
            p_id = request.GET["project_id"]
        except:
            return HttpResponse(json.dumps(dict(total = 0
                                              , investigators = []))
                          , content_type = "application/json")

        sortField = request.GET.get("sortField", "id")
        sortField = "id" if sortField == "null" else sortField
        order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
        query_set = Investigator.objects.filter(project__id = p_id)
        if sortField == "pi":
            sortField = "investigator__user__last_name"
            query_set = query_set.filter(Q(investigator__principal_investigator = True))
    
        filterText = request.GET.get("filterText", None)
        if filterText is not None:
            query_set = query_set.filter(
                    Q(user__last_name__icontains=filterText) |
                    Q(user__first_name__icontains=filterText) 
                    )
        investigators = query_set.order_by(order + sortField)
        total         = len(investigators)
        offset        = int(request.GET.get("offset", 0))
        limit         = int(request.GET.get("limit", 50))
        investigators = investigators[offset:offset+limit]
        return HttpResponse(json.dumps(
              dict(total = total
                , investigators = [InvestigatorHttpAdapter(i).jsondict() for i in investigators]))
            , content_type = "application/json")
