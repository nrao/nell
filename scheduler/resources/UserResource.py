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

from django.db.models        import Q
from django.http             import HttpResponse, HttpResponseRedirect
from django_restapi.resource import Resource
from scheduler.models        import User
from scheduler.httpadapters  import UserHttpAdapter
from NellResource            import NellResource

import simplejson as json

class MethodException(Exception):

    def __init__(self, method):
        self.method = method

    def __str__(self):
        return "Method '%s' is invalid for UserResource." % self.method

class UserResource(NellResource):

    def __init__(self, *args, **kws):
        super(UserResource, self).__init__(User, UserHttpAdapter, *args, **kws)

    def create(self, request, *args, **kws):
        return super(UserResource, self).create(request, *args, **kws)
    
    def read(self, request, *args, **kws):
        if len(args) == 0:
            # many, filtered by:
            sortField = request.GET.get("sortField", "id")
            sortField = "id" if sortField == "null" else sortField
            order     = "-" if request.GET.get("sortDir", "ASC") == "DESC" else ""
            query_set = User.objects
            filterText = request.GET.get("filterText")
            if filterText is not None:
                query_set = query_set.filter(
                     Q(first_name__icontains=filterText) |
                     Q(last_name__icontains=filterText) |
                     Q(contact_instructions__icontains=filterText) 
                     )

            users     = query_set.order_by(order + sortField)
            total     = len(users)
            offset    = int(request.GET.get("offset", 0))
            limit     = int(request.GET.get("limit", 50))
            users     = users[offset:offset+limit]
            return HttpResponse(
                     json.dumps(dict(total = total
                                   , users = [UserHttpAdapter(u).jsondict() for u in users]))
                   , content_type = "application/json")
        else:
            # one, identified by id
            u_id, = args
            user  = User.objects.get(id = u_id)
            adapter = UserHttpAdapter(user)
            return HttpResponse(json.dumps(dict(user = adapter.jsondict()))
                              , content_type = "application/json")

    def update(self, request, *args, **kws):
        id      = int(args[0])
        u       = User.objects.get(id = id)
        adapter = UserHttpAdapter(u)
        adapter.update_from_post(request.POST)

        return HttpResponse(json.dumps({"success" : "ok"})
                          , mimetype = "text/plain")


