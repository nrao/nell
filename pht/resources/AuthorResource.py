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
from pht.httpadapters import AuthorHttpAdapter
from pht.models       import Author, Proposal

class AuthorResource(Resource):

    def __init__(self):
        self.adapter = AuthorHttpAdapter()

    def read(self, request, *args, **kws):
        if len(args) == 2:
            _, id   = args
            adapter = AuthorHttpAdapter(Author.objects.get(id = id))
            return HttpResponse(json.dumps(adapter.jsonDict())
                              , content_type = 'application/json')
        else:
            pcode,   = args
            proposal = Proposal.objects.get(pcode = pcode)
            authors  = [AuthorHttpAdapter(a).jsonDict() for a in proposal.author_set.all()]
            return HttpResponse(json.dumps({"success" : "ok" , 'authors' : authors })
                              , content_type = 'application/json')

    def update(self, request, *args, **kws):
        _, id   = args
        adapter  = AuthorHttpAdapter(Author.objects.get(id = id))
        adapter.updateFromPost(json.loads(request.raw_post_data))
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')

    def delete(self, request, *args, **kws):
        id,   = args
        author = Author.objects.get(id = id)
        author.delete()
        adapter = AuthorHttpAdapter(author)
        adapter.notify(author.proposal)
        return HttpResponse(json.dumps({"success" : "ok"})
                          , content_type = 'application/json')
