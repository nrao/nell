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
from scheduler.models       import Window
from scheduler.httpadapters import WindowHttpAdapter
from datetime              import datetime, timedelta, date

import simplejson as json

jsonMap = { "id" : "id"
          , "handle" : "session__name"
          , "start"  : "start_date"
          , "duration" : "duration"
          , "last" : "start_date"
          }
    
class WindowResource(NellResource):
    def __init__(self, *args, **kws):
        super(WindowResource, self).__init__(Window, WindowHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(WindowResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):

        # one or many?
        if len(args) == 0:
            # many, use filters
            query_set = Window.objects

            filterComplete = request.GET.get("filterComplete", None)
            if filterComplete is not None:
                query_set = query_set.filter(complete = (filterComplete == "true"))
            filterSession = request.GET.get("filterSession", None)
            if filterSession is not None:
                query_set = query_set.filter(session__name = filterSession)

            filterSessionId = request.GET.get("filterSessionId", None)
            if filterSessionId is not None:
                query_set = query_set.filter(session__id = filterSessionId)

            # time range filters come as a pair
            filterByDateRange = False
            filterStart = request.GET.get("filterStartDate", None)
            filterDur   = request.GET.get("filterDuration", None)
            if filterStart is not None and filterDur is not None:
                start = datetime.strptime(filterStart, "%Y-%m-%d").date() 
                days = int(filterDur)
                days = days if days >= 1 else 1
                last_day = (start + timedelta(days = days -1))
                # It would be ideal to finish the query here, but our query_set
                # is for Window, but our time info is kept in WindowRange
                # and the end point needs to be calculated
                # Note: what else can we do to filter more from DB?
                query_set = query_set.annotate(win_start=Min('windowrange__start_date')).filter(win_start__lte = last_day)
                filterByDateRange = True

            # see if a sort field was passed to us
            if request.GET.get("sortField", None) is not None:
                sortField = jsonMap.get(request.GET.get("sortField", "handle"), "start_date")
                order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""             
                windows = query_set.order_by(order + sortField)
            else:
                # by default, sort by the earliest period's start
                windows = query_set.annotate(win_start=Min('windowrange__start_date')).order_by('win_start').distinct()

            # if filtering by date range, we have to finish this programmatically
            if filterByDateRange:
                windows = [w for w in windows if w.last_date() >= start \
                    and w.start() <= last_day]

            total = len(windows)
            offset = int(request.GET.get("offset", 0))
            limit  = int(request.GET.get("limit", -1))
            if limit != -1:
                windows = windows[offset:offset+limit]
            return HttpResponse(json.dumps(dict(total = total
                 , windows = [WindowHttpAdapter(w).jsondict() for w in windows]))
            , content_type = "application/json")
        else:
            # one, identified by id in arg list
            w_id = args[0]
            window = Window.objects.get(id = w_id)
            return HttpResponse(json.dumps(dict(window = WindowHttpAdapter(window).jsondict()))
                              , content_type = "application/json")


