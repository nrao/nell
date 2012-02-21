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

def formatDate(dt):
    return str(dt.strftime('%m/%d/%Y'))

def cleanPostData(data):
    bad_keys = [k for k, v in data.iteritems() if v == '']
    for bk in bad_keys:
        data.pop(bk)
    return data

class ProposalHttpAdapter(object):

    def __init__(self, proposal = None):
        self.setProposal(proposal)

    def setProposal(self, proposal):
        self.proposal = proposal

    def jsonDict(self):
        authors        = '; '.join([a.getLastFirstName() for a in self.proposal.author_set.all()])
        sci_categories = [sc.category for sc in self.proposal.sci_categories.all()]
        obs_types      = [ot.type for ot in self.proposal.observing_types.all()]
        semester = self.proposal.semester.semester if self.proposal.semester is not None else None
        pi_id   = self.proposal.pi.id if self.proposal.pi is not None else None
        pi_name = self.proposal.pi.getLastFirstName() if self.proposal.pi is not None else None

        return {'id'               : self.proposal.pcode
              , 'pst_proposal_id'  : self.proposal.pst_proposal_id
              , 'proposal_type'    : self.proposal.proposal_type.type
              , 'observing_types'  : obs_types
              , 'status'           : self.proposal.status.name
              , 'semester'         : semester
              , 'pi_id'            : pi_id 
              , 'pi_name'          : pi_name
              , 'authors'          : authors
              , 'sci_categories'   : sci_categories
              , 'pcode'            : self.proposal.pcode
              , 'create_date'      : formatDate(self.proposal.create_date)
              , 'modify_date'      : formatDate(self.proposal.modify_date)
              , 'submit_date'      : formatDate(self.proposal.submit_date)
              , 'total_time'       : self.proposal.total_time
              , 'title'            : self.proposal.title
              , 'abstract'         : self.proposal.abstract
              , 'spectral_line'    : self.proposal.spectral_line
              , 'joint_proposal'   : self.proposal.joint_proposal
               }

    def initFromPost(self, data):
        self.proposal = Proposal()
        self.proposal.create_date = datetime.now()
        self.updateFromPost(cleanPostData(data))
        self.proposal.save()

    def updateFromPost(self, data):

        dtfmt         = "%m/%d/%Y"
        dt            = data.get('submit_date')
        pi_id         = data.get('pi_id')
        pi            = Author.objects.get(id = pi_id) if pi_id is not None else None
        proposalType  = ProposalType.objects.get(type = data.get('proposal_type'))
        status        = Status.objects.get(name = data.get('status'))
        semester      = Semester.objects.get(semester = data.get('semester'))


        self.proposal.pst_proposal_id = data.get('pst_proposal_id')
        self.proposal.proposal_type   = proposalType
        # TBF: authors is very complicated, need to fix this
        #self.proposal.pi              = pi
        self.proposal.status          = status
        self.proposal.semester        = semester
        self.proposal.pcode           = data.get('pcode')
        self.proposal.modify_date     = datetime.now()
        self.proposal.submit_date     = datetime.strptime(dt, dtfmt) 
        self.proposal.total_time      = data.get('total_time', 0.0)
        self.proposal.title           = data.get('title')
        self.proposal.abstract        = data.get('abstract')
        self.proposal.spectral_line   = data.get('spectral_line')
        self.proposal.joint_proposal  = data.get('joint_proposal') == 'true'

        self.proposal.save()

        # now that we definitely have a PK for the object, we can work w/ these:

        # multiple observing types possible - returned as an array
        for otype in self.proposal.observing_types.all():
            self.proposal.observing_types.remove(otype)
        obsTypes = data.get('observing_types', [])    
        for otName in obsTypes:
            otype = ObservingType.objects.get(type = otName)
            self.proposal.observing_types.add(otype)

        # same is true for science categories
        for cats in self.proposal.sci_categories.all():
            self.proposal.sci_categories.remove(cats)
        cats = data.get('sci_categories', [])    
        for cat in cats:
            cat = ScientificCategory.objects.get(category = cat)
            self.proposal.sci_categories.add(cat)

        self.proposal.save()    
