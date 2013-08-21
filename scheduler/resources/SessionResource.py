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

from django.http              import HttpResponse, HttpResponseRedirect
from django.db.models         import Q
from django.shortcuts         import get_object_or_404

from NellResource import NellResource
from scheduler.models       import Sesshun
from scheduler.utilities    import jsonMap
from scheduler.httpadapters import SessionHttpAdapter

import simplejson as json
from reversion import revision

class SessionResource(NellResource):
    def __init__(self, *args, **kws):
        super(SessionResource, self).__init__(Sesshun, SessionHttpAdapter, *args, **kws)
 
    def create(self, request, *args, **kws):
        return super(SessionResource, self).create(request, *args, **kws)

    def read(self, request, *args, **kws):
        if len(args) == 0:
            requestSort = request.GET.get("sortField", "pcode")
            sortField   = jsonMap.get(requestSort, "project__pcode")
            order       = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            query_set   = Sesshun.objects

            filterEnb = request.GET.get("filterEnb", None)
            if filterEnb is not None:
                query_set = query_set.filter(
                    status__enabled = (filterEnb.lower() == "true"))

            filterProjClp= request.GET.get("filterProjClp", None)
            if filterProjClp is not None:
                query_set = query_set.filter(
                    project__complete = (filterProjClp.lower() == "true"))
            
            filterAuth= request.GET.get("filterAuth", None)
            if filterAuth is not None:
                query_set = query_set.filter(
                    status__authorized = (filterAuth.lower() == "true"))

            filterSpr= request.GET.get("filterSpr", None)
            if filterSpr is not None:
                query_set = query_set.filter(project__sponsor__abbreviation = filterSpr)

            filterClp= request.GET.get("filterClp", None)
            if filterClp is not None:
                query_set = query_set.filter(
                    status__complete = (filterClp.lower() == "true"))

            filterType = request.GET.get("filterType", None)
            if filterType is not None:
                query_set = query_set.filter(session_type__type = filterType.lower())

            filterSci = request.GET.get("filterSci", None)
            if filterSci is not None:
                query_set = query_set.filter(observing_type__type = filterSci.lower())

            filterSem = request.GET.get("filterSem", None)
            if filterSem is not None:
                query_set = query_set.filter(project__semester__semester__icontains = filterSem)

            filterRcvr = request.GET.get("filterRcvr", None)
            if filterRcvr is not None:
                query_set = query_set.filter(receiver_group__receivers__abbreviation = filterRcvr)

            filterFreq = request.GET.get("filterFreq", None)
            if filterFreq is not None:
                if ">" in filterFreq:
                    filterFreq = filterFreq.replace(">", "")
                    query_set = query_set.filter(frequency__gt = float(filterFreq))
                elif "<=" in filterFreq:
                    filterFreq = filterFreq.replace("<=", "")
                    query_set = query_set.filter(frequency__lte = float(filterFreq))

            filterText = request.GET.get("filterText", None)
            if filterText is not None:
                query_set = query_set.filter(
                    Q(name__icontains=filterText) |
                    Q(project__pcode__icontains=filterText) |
                    Q(project__semester__semester__icontains=filterText) |
                    Q(session_type__type__icontains=filterText) |
                    Q(observing_type__type__icontains=filterText) |
                    Q(target__source__icontains=filterText)
                    )
            sessions = query_set.order_by(order + sortField)
            total    = len(sessions)
            offset   = int(request.GET.get("offset", 0))
            limit    = int(request.GET.get("limit", 50))
            json_sessions = [SessionHttpAdapter(s).jsondict() for s in sessions]
            if requestSort == "xi_factor":
                json_sessions = sorted(json_sessions
                                     , key = lambda session: session['xi_factor']
                                     , reverse = order == "-")
            json_sessions = json_sessions[offset:offset+limit]
            return HttpResponse(json.dumps(
                     dict(total = total
                        , sessions = json_sessions))
                   , content_type = "application/json")
        else:
            s_id  = args[0]
            s     = get_object_or_404(Sesshun, pk = s_id)
            return HttpResponse(json.dumps(dict(session = SessionHttpAdapter(s).jsondict())))
