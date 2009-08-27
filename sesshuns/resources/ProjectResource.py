from django.db.models         import Q
from django.http              import HttpResponse, HttpResponseRedirect

from NellResource import NellResource
from sesshuns.models       import Project, first

import simplejson as json

class ProjectResource(NellResource):
    def __init__(self, *args, **kws):
        super(ProjectResource, self).__init__(Project, *args, **kws)

    def create(self, request, *args, **kws):
        return super(ProjectResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        sortField = request.GET.get("sortField", "id")
        sortField = "pcode" if sortField == "null" or \
                               sortField == "pi" or \
                               sortField == "co_i" \
                            else sortField
        sortField = "semester__semester" if sortField == "semester" else sortField
        order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
        query_set = Project.objects

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

        filterText = request.GET.get("filterText", None)
        if filterText is not None:
            query_set = query_set.filter(
                    Q(name__icontains=filterText) |
                    Q(pcode__icontains=filterText) |
                    Q(semester__semester__icontains=filterText) |
                    Q(project_type__type__icontains=filterText) |
                    Q(investigators__user__first_name__icontains = filterText) |
                    Q(investigators__user__last_name__icontains = filterText)
                    )
        projects = query_set.order_by(order + sortField)
        total    = len(projects)
        offset   = int(request.GET.get("offset", 0))
        limit    = int(request.GET.get("limit", 50))
        projects = projects[offset:offset+limit]
        return HttpResponse(json.dumps(dict(total = total
                                          , projects = [p.jsondict() for p in projects]))
                          , content_type = "application/json")
