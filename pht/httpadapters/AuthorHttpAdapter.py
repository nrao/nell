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

from datetime import datetime

from pht.models import *
from PhtHttpAdapter      import PhtHttpAdapter

class AuthorHttpAdapter(PhtHttpAdapter):

    def __init__(self, author = None):
        self.setAuthor(author)

    def setAuthor(self, author):
        self.author = author

    def jsonDict(self):
        return {'id'                  : self.author.id
              , 'pst_person_id'       : self.author.pst_person_id
              , 'pst_author_id'       : self.author.pst_author_id
              , 'pcode'               : self.author.proposal.pcode
              , 'affiliation'         : self.author.affiliation
              , 'domestic'            : self.author.domestic
              , 'new_user'            : self.author.new_user
              , 'email'               : self.author.email
              , 'address'             : self.author.address
              , 'telephone'           : self.author.telephone
              , 'last_name'           : self.author.last_name
              , 'first_name'          : self.author.first_name
              , 'name'                : self.author.getLastFirstName()
              , 'professional_status' : self.author.professional_status
              , 'thesis_observing'    : self.author.thesis_observing
              , 'graduation_year'     : self.author.graduation_year
              , 'oldauthor_id'        : self.author.oldauthor_id
              , 'storage_order'       : self.author.storage_order
              , 'other_awards'        : self.author.other_awards
              , 'support_requester'   : self.author.support_requester
              , 'supported'           : self.author.supported
              , 'budget'              : self.author.budget
              , 'assignment'          : self.author.assignment
               }

    def initFromPost(self, data):
        self.author = Author()
        self.updateFromPost(data)
        self.notify(self.author.proposal)

    def updateFromPost(self, data):
        proposal  = Proposal.objects.get(pcode = data.get('pcode'))
        author_id = data.get('pst_author_id')

        self.author.pst_person_id        = data.get('pst_person_id')
        self.author.pst_author_id        = author_id if author_id != '' else None
        self.author.proposal             = proposal
        self.author.affiliation          = data.get('affiliation')
        self.author.domestic             = data.get('domestic')
        self.author.new_user             = data.get('new_user')
        self.author.email                = data.get('email')
        self.author.address              = data.get('address')
        self.author.telephone            = data.get('telephone')
        self.author.last_name            = data.get('last_name')
        self.author.first_name           = data.get('first_name')
        self.author.professional_status  = data.get('professional_status')
        self.author.thesis_observing     = data.get('thesis_observing')
        self.author.graduation_year      = data.get('graduation_year')
        self.author.oldauthor_id         = data.get('oldauthor_id')
        self.author.storage_order        = data.get('storage_order')
        self.author.other_awards         = data.get('other_awards')
        self.author.support_requester    = data.get('support_requester')
        self.author.supported            = data.get('supported')
        self.author.budget               = data.get('budget')
        self.author.assignment           = data.get('assignment')
        self.author.save()

        self.notify(self.author.proposal)

    def copy(self, new_pcode):
        data = self.jsonDict()
        data['pcode'] = new_pcode
        adapter = AuthorHttpAdapter()
        adapter.initFromPost(data)

        return adapter.author
