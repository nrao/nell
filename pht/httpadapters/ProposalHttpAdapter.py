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
import settings, pg, psycopg2

from pht.models import *
from AuthorHttpAdapter   import AuthorHttpAdapter
from PhtHttpAdapter      import PhtHttpAdapter
from SessionHttpAdapter  import SessionHttpAdapter
from SourceHttpAdapter   import SourceHttpAdapter

from scheduler.models import User as DSSUser

class ProposalHttpAdapter(PhtHttpAdapter):

    def __init__(self, proposal = None):
        self.setProposal(proposal)

    def setProposal(self, proposal):
        self.proposal = proposal

    @staticmethod
    def jsonDictHP(curr, keys, values):
        data = dict(zip(keys, values))
        id = data['proposal_id']
        # collect observing types
        query = """
          select ot.type, ot.code 
          from pht_proposals_observing_types as pot join pht_observing_types as ot on ot.id = pot.observingtype_id  
          where pot.proposal_id = %s
        """ % id
        curr.execute(query)
        results = curr.fetchall()
        data['observing_types'] = [t for t, c in results]
        data['obs_type_codes'] = [c for t, c in results]
        # science categories
        query = """
          select sc.category, sc.code 
          from pht_proposals_sci_categories as psc join pht_scientific_categories as sc on sc.id = psc.scientificcategory_id  
          where psc.proposal_id = %s
        """ % id
        curr.execute(query)
        results = curr.fetchall()
        data['sci_categories'] = [t for t, c in results]
        data['sci_cat_codes']  = [c for t, c in results]
        # authors 
        query = """
            select a.last_name, a.first_name
            from pht_authors as a 
            where a.proposal_id = %s
        """ % id
        curr.execute(query)
        results = curr.fetchall()
        data['authors'] = '; '.join(["%s, %s" % (last, first) for last, first in results])
        # stuff from the associated sessions: grades, times, etc.
        # grades
        query = """
          select distinct(g.grade)
          from pht_sessions as s join pht_session_grades as g on s.grade_id = g.id 
          where proposal_id = %s
          order by g.grade
        """ % id  
        curr.execute(query)
        results = curr.fetchall()
        data['grades']  = ','.join([g for g, in results])
        # requested time
        query = """
          select sum(a.requested_time * a.repeats) 
          from pht_sessions as s join pht_allotements as a on s.allotment_id = a.id 
          where proposal_id = %s
        """ % id
        curr.execute(query)
        data['requested_time'] = curr.fetchone()[0]
        # allocated time
        query = """
          select sum(a.allocated_time) 
          from pht_sessions as s join pht_allotements as a on s.allotment_id = a.id 
          where proposal_id = %s
        """ % id
        curr.execute(query)
        data['allocated_time'] = curr.fetchone()[0]
        # now the hard time - all the DSS project's time accounting!
        # TBF
        data['dss_total_time'] = None
        data['billed_time'] = None
        data['scheduled_time'] = None
        data['remaining_time'] = None

        # now a little clean up
        if data['allocated_time'] is None:
            data['allocated_time'] = 0
        if data['requested_time'] is None:
            data['requested_time'] = 0
        # date formatting    
        frmt = "%m/%d/%Y"
        fields = ['create_date', 'submit_date', 'modify_date']
        for f in fields:
            data[f] = data[f].strftime(frmt)
            
        return data

    @staticmethod
    def jsonDictAllHP():
        conn = psycopg2.connect(host   = settings.DATABASES['default']['HOST']
                              , user   = settings.DATABASES['default']['USER']
                              , password = settings.DATABASES['default']['PASSWORD']
                              , database = settings.DATABASES['default']['NAME']
                            )
        curr = conn.cursor()
        query = """
        SELECT
          p.pcode as id,
          p.id as proposal_id,
          p.pst_proposal_id,
          pt.type as proposal_type,
          ps.name as status,
          s.semester,
          a.id as pi_id,
          a.last_name || ', ' || a.first_name as pi_name,
          u.id as friend_id,
          u.last_name || ', ' || u.first_name as friend_name,
          p.pcode,
          p.create_date,
          p.modify_date,
          p.submit_date,
          p.title,
          p.abstract,
          p.spectral_line,
          p.joint_proposal,
          p.next_semester_complete as next_sem_complete,
          pj.pcode as dss_pcode,
          pj.complete,
          p."normalizedSRPScore",
          c.nrao_comment,
          c.srp_to_pi,
          c.srp_to_tac,
          c.tech_review_to_pi,
          c.tech_review_to_tac,
          c.tac_to_pi

        FROM (((((((
          pht_proposals as p
          left outer join pht_proposal_types as pt on pt.id = p.proposal_type_id)
          left outer join pht_status as ps on ps.id = p.status_id)
          left outer join pht_semesters as s on s.id = p.semester_id)
          left outer join pht_authors as a on a.id = p.pi_id)
          left outer join users as u on u.id = p.friend_id)
          left outer join projects as pj on pj.id = p.dss_project_id)
          left outer join pht_proposal_comments as c on c.id = p.comments_id)

        ORDER BY p.pcode  
        """
        curr.execute(query)
        keys = [d.name for d in curr.description]
        return [ProposalHttpAdapter.jsonDictHP(curr, keys, values) for values in curr.fetchall()]

    def jsonDict(self):
        authors        = '; '.join([a.getLastFirstName() for a in self.proposal.author_set.all()])
        sci_categories = [sc.category for sc in self.proposal.sci_categories.all()]
        sci_cat_codes  = [sc.code for sc in self.proposal.sci_categories.all()]
        obs_types      = [ot.type for ot in self.proposal.observing_types.all()]
        obs_type_codes = [ot.code for ot in self.proposal.observing_types.all()]
        semester = self.proposal.semester.semester if self.proposal.semester is not None else None
        friend_id   = self.proposal.friend.id if self.proposal.friend is not None else None
        friend_name = self.proposal.friend.__str__() if self.proposal.friend is not None else None
        pi_id   = self.proposal.pi.id if self.proposal.pi is not None else None
        pi_name = self.proposal.pi.getLastFirstName() if self.proposal.pi is not None else None
        dss_pcode = self.proposal.dss_project.pcode if self.proposal.dss_project is not None else None #'unknown'

        data = {'id'               : self.proposal.pcode
              , 'proposal_id'      : self.proposal.id
              , 'pst_proposal_id'  : self.proposal.pst_proposal_id
              , 'proposal_type'    : self.proposal.proposal_type.type
              , 'observing_types'  : obs_types
              , 'obs_type_codes'   : obs_type_codes
              , 'status'           : self.proposal.status.name
              , 'semester'         : semester
              , 'pi_id'            : pi_id 
              , 'pi_name'          : pi_name
              , 'friend_id'        : friend_id 
              , 'friend_name'      : friend_name
              , 'authors'          : authors
              , 'sci_categories'   : sci_categories
              , 'sci_cat_codes'    : sci_cat_codes
              , 'pcode'            : self.proposal.pcode
              , 'create_date'      : self.formatDate(self.proposal.create_date)
              , 'modify_date'      : self.formatDate(self.proposal.modify_date)
              , 'submit_date'      : self.formatDate(self.proposal.submit_date)
              , 'requested_time'   : self.proposal.requestedTime()
              , 'allocated_time'   : self.proposal.allocatedTime()
              , 'grades'           : ",".join(self.proposal.grades())
              , 'title'            : self.proposal.title
              , 'abstract'         : self.proposal.abstract
              , 'spectral_line'    : self.proposal.spectral_line
              , 'joint_proposal'   : self.proposal.joint_proposal
              , 'next_sem_complete': self.proposal.next_semester_complete
              , 'dss_pcode'        : dss_pcode
              , 'complete'         : self.proposal.isComplete()
              , 'dss_total_time'   : self.proposal.dssAllocatedTime()
              , 'billed_time'      : self.proposal.billedTime()
              , 'scheduled_time'   : self.proposal.scheduledTime()
              , 'remaining_time'   : self.proposal.remainingTime()
              , 'normalizedSRPScore' : self.proposal.normalizedSRPScore
              }

        # comments
        if self.proposal.comments:
            data.update({'nrao_comment'     : self.proposal.comments.nrao_comment
                       , 'srp_to_pi'        : self.proposal.comments.srp_to_pi
                       , 'srp_to_tac'       : self.proposal.comments.srp_to_tac
                       , 'tech_review_to_pi': self.proposal.comments.tech_review_to_pi
                       , 'tech_review_to_tac': self.proposal.comments.tech_review_to_tac
                       , 'tac_to_pi'         : self.proposal.comments.tac_to_pi
                        })
        else:
            data.update({'nrao_comment'      : None #''
                       , 'srp_to_pi'         : None #''
                       , 'srp_to_tac'        : None #''
                       , 'tech_review_to_pi' : None #''
                       , 'tech_review_to_tac': None #''
                       , 'tac_to_pi'         : None #''
                        })
        return data

    def initFromPost(self, data):
        self.proposal = Proposal()
        comments = ProposalComments()
        comments.save()
        self.proposal.comments = comments
        self.proposal.create_date = datetime.now()
        self.updateFromPost(self.cleanPostData(data))
        self.proposal.save()
        self.notify(self.proposal)

    def updateFromPost(self, data):

        dtfmt         = "%m/%d/%Y"
        dt            = data.get('submit_date')
        try:
            pi_id         = data.get('pi_id')
            pi            = Author.objects.get(id = pi_id) if pi_id is not None else None
        except:
            pi = None
        try:    
            friend_id     = data.get('friend_id')
            friend        = DSSUser.objects.get(id = friend_id) if friend_id is not None else None
        except:
            friend = None
        proposalType  = ProposalType.objects.get(type = data.get('proposal_type'))
        status        = Status.objects.get(name = data.get('status'))
        semester      = Semester.objects.get(semester = data.get('semester'))


        self.proposal.pst_proposal_id = data.get('pst_proposal_id')
        self.proposal.proposal_type   = proposalType
        self.proposal.pi              = pi
        self.proposal.friend          = friend
        self.proposal.status          = status
        self.proposal.semester        = semester
        self.proposal.pcode           = data.get('pcode')
        self.proposal.modify_date     = datetime.now()
        self.proposal.submit_date     = datetime.strptime(dt, dtfmt) 
        self.proposal.total_time      = data.get('total_time', 0.0)
        self.proposal.title           = data.get('title')
        self.proposal.abstract        = data.get('abstract')
        self.proposal.spectral_line   = data.get('spectral_line')
        self.proposal.joint_proposal  = \
            data.get('joint_proposal') == 'true'
        self.proposal.next_semester_complete  = \
            data.get('next_semester_complete') == 'true'

        self.proposal.save()

        # now that we definitely have a PK for the object, we can work w/ these:

        # multiple observing types possible - returned as an array
        for otype in self.proposal.observing_types.all():
            self.proposal.observing_types.remove(otype)
        obsTypes = data.get('obs_type_codes', [])    
        for otCode in obsTypes:
            otype = ObservingType.objects.get(code = otCode)
            self.proposal.observing_types.add(otype)

        # same is true for science categories
        for cats in self.proposal.sci_categories.all():
            self.proposal.sci_categories.remove(cats)
        cats = data.get('sci_cat_codes', [])    
        for cat in cats:
            cat = ScientificCategory.objects.get(code = cat)
            self.proposal.sci_categories.add(cat)

        # comments
        self.proposal.comments.nrao_comment = data.get('nrao_comment')
        self.proposal.comments.srp_to_pi = data.get('srp_to_pi')
        self.proposal.comments.srp_to_tac = data.get('srp_to_tac')
        self.proposal.comments.tech_review_to_pi = data.get('tech_review_to_pi')
        self.proposal.comments.tech_review_to_tac = data.get('tech_review_to_tac')
        self.proposal.comments.tac_to_pi = data.get('tac_to_pi')
        self.proposal.comments.save()

        self.proposal.save()    
        self.notify(self.proposal)

    def copy(self, new_pcode):
        data = self.jsonDict()
        data['pcode'] = new_pcode
        adapter = ProposalHttpAdapter()
        adapter.initFromPost(data)
        
        # Authors
        for a in self.proposal.author_set.all():
            aAdapter = AuthorHttpAdapter(a)
            aAdapter.copy(new_pcode)

        # Proposal Sources
        for s in self.proposal.source_set.all():
            sAdapter = SourceHttpAdapter(s)
            sAdapter.copy(new_pcode)

        # Sessions
        for s in self.proposal.session_set.all():
            sAdapter = SessionHttpAdapter(s)
            new_s = sAdapter.copy(new_pcode)
            
        return adapter.proposal
        
