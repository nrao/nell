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
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from scheduler.models       import Project
from scheduler.httpadapters import ProjectHttpAdapter

import simplejson as json

class ProjectResource(NellResource):
    def __init__(self, *args, **kws):
        super(ProjectResource, self).__init__(Project, ProjectHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(ProjectResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        # one or many?
        if len(args) == 0:
            # many, filtered by:
            sortField = request.GET.get("sortField", "id")
            sortField = "pcode" if sortField == "null" or \
                                   sortField == "co_i" \
                                    else sortField
            sortField = "semester__semester" if sortField == "semester" else sortField
            sortField = "sponsor__abbreviation" if sortField == "sponsor" else sortField
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            query_set = Project.objects
            if sortField == "pi":
                sortField = "investigator__user__last_name"
                query_set = query_set.filter(Q(investigator__principal_investigator = True))
    
            filterClp = request.GET.get("filterClp", None)
            if filterClp is not None:
                query_set = query_set.filter(
                    complete = (filterClp.lower() == "true"))
    
            filterType = request.GET.get("filterType", None)
            if filterType is not None:
                query_set = query_set.filter(project_type__type = filterType.lower())
    
            filterSem = request.GET.get("filterSem", None)
            if filterSem is not None:
                query_set = query_set.filter(semester__semester__icontains = filterSem)
    
            filterSpn = request.GET.get("filterSpn", None)
            if filterSpn is not None:
                query_set = query_set.filter(sponsor__abbreviation__icontains = filterSpn)

            filterText = request.GET.get("filterText", None)
            if filterText is not None:
                query_set = query_set.filter(
                        Q(name__icontains=filterText) |
                        Q(pcode__icontains=filterText) |
                        Q(semester__semester__icontains=filterText) |
                        Q(project_type__type__icontains=filterText) |
                        Q(investigator__user__first_name__icontains = filterText) |
                        Q(investigator__user__last_name__icontains = filterText)
                        ).distinct()
            projects = query_set.order_by(order + sortField)
            total    = len(projects)
            offset   = int(request.GET.get("offset", 0))
            limit    = int(request.GET.get("limit", 50))
            projects = projects[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                                              , projects = [ProjectHttpAdapter(p).jsondict() for p in projects]))
                              , content_type = "application/json")
        else:
            # one, identified by id
            p_id = args[0]
            proj = Project.objects.get(id = p_id)
            return HttpResponse(json.dumps(dict(project = ProjectHttpAdapter(proj).jsondict()))
                              , content_type = "application/json")


