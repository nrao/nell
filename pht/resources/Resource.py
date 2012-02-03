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

import simplejson as json
from django.http import HttpResponse

class Resource(object):

    def requestHandler(self, request, *args, **kws):
        if request.method == 'GET':
            return self.read(request, *args, **kws)
        elif request.method == 'POST':
            return self.create(request, *args, **kws)
        elif request.method == "PUT":
            return self.update(request, *args, **kws)
        elif request.method == "DELETE":
            return self.delete(request, *args, **kws)
        else:
            return self.read(request, *args, **kws)

    def create(self, request, *args, **kws):
        self.adapter.initFromPost(json.loads(request.raw_post_data))
        return HttpResponse(json.dumps(self.adapter.jsonDict())
                          , content_type = 'application/json')

