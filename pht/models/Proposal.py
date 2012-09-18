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

from django.db          import models
from datetime           import datetime

from Author             import Author
from Backend            import Backend
from ObservingType      import ObservingType
from ScientificCategory import ScientificCategory
from Semester           import Semester
from Status             import Status
from ProposalType       import ProposalType
from ProposalComments   import ProposalComments
from Receiver           import Receiver

from scheduler.models   import Project as DSSProject 
from scheduler.models   import User as DSSUser 

from utilities          import TimeAccounting

class Proposal(models.Model):

    pst_proposal_id = models.IntegerField(null = True)
    dss_project     = models.ForeignKey(DSSProject, null = True, on_delete = models.SET_NULL)
    proposal_type   = models.ForeignKey(ProposalType)
    observing_types = models.ManyToManyField(ObservingType)
    status          = models.ForeignKey(Status)
    semester        = models.ForeignKey(Semester, null = True)
    friend          = models.ForeignKey(DSSUser, null = True)
    pi              = models.ForeignKey('Author', related_name = "pi_on", null = True)
    investigators   = models.ManyToManyField('Author', related_name = 'investigator_on')
    sci_categories  = models.ManyToManyField(ScientificCategory)
    pcode           = models.CharField(max_length = 32, unique = True)
    create_date     = models.DateTimeField()
    modify_date     = models.DateTimeField()
    submit_date     = models.DateTimeField()
    title           = models.CharField(max_length = 512)
    abstract        = models.CharField(max_length = 2000)
    spectral_line   = models.CharField(max_length = 2000, null = True)
    joint_proposal  = models.BooleanField()
    comments        = models.ForeignKey(ProposalComments, null = True)
    normalizedSRPScore       = models.FloatField(null = True)
    draft_normalizedSRPScore = models.FloatField(null = True)
    num_refs                 = models.IntegerField(null = True)
    next_semester_complete   = models.BooleanField(default = True)

    class Meta:
        db_table  = "pht_proposals"
        app_label = "pht"

    def __str__(self):
        return self.pcode

    def requestedTime(self):
        "Simply the sum of the sessions' time"
        return sum([s.getTotalRequestedTime() \
            for s in self.session_set.all() \
            if s.getTotalRequestedTime() is not None])

    def allocatedTime(self):
        "Simply the sum of the sessions' time"
        return sum([s.allotment.allocated_time \
            for s in self.session_set.all() \
                if s.allotment is not None \
                and s.allotment.allocated_time is not None])

    def allocatedTimeByGrade(self):
        "Sum the session times by grade."
        allotments = {}
        for s in self.session_set.all():
            if s.allotment is not None and s.allotment.allocated_time is not None:
                if allotments.has_key(s.grade.grade):
                    allotments[s.grade.grade] += s.allotment.allocated_time
                else:
                    allotments[s.grade.grade] = s.allotment.allocated_time
        return allotments.iteritems()

    def isThesis(self):
        students  = len(self.author_set.filter(thesis_observing = True))
        return students, students > 0

    def grades(self):
        "Return unique list of grades"
        return sorted(list(set([s.grade.grade \
            for s in self.session_set.order_by('grade') \
                if s.grade is not None])))

    # *** Section: accessing the corresponding DSS project
    def dssAllocatedTime(self):
        "How much was the corresponding DSS project allocated?"
        if self.dss_project is not None:
            ta = TimeAccounting()
            return ta.getProjectTotalTime(self.dss_project)
        else:
            return None

    def remainingTime(self):
        "From this proposal's project's time accounting."
        if self.dss_project is not None:
            ta = TimeAccounting()
            return ta.getTimeLeft(self.dss_project)
        else:
            return None

    def billedTime(self):
        "From this proposal's project's time accounting."
        return self.getTime('time_billed')

    def scheduledTime(self):
        "From this proposal's project's time accounting."
        return self.getTime('scheduled')

    def getTime(self, type):
        "Leverage time accounting for this proposal's project."
        if self.dss_project is not None:
            ta = TimeAccounting()
            return ta.getTime(type, self.dss_project)
        else:
            return None

    def backends(self):
        return ''.join([b.code for b in Backend.objects.raw(
            """
            select distinct b.id, b.* 
            from ((pht_sessions as s 
              join pht_proposals as p on p.id = s.proposal_id ) 
              join pht_sessions_backends as sb on s.id = sb.session_id) 
              join pht_backends as b on b.id = sb.backend_id 
            where p.pcode = '%s'""" % self.pcode)])

    def bands(self):
        "What are the bands associated with this proposal?"
        return ''.join([r.code for r in Receiver.objects.raw(
            """
            select distinct r.id, r.code
            from ((pht_sessions as s 
              join pht_proposals as p on p.id = s.proposal_id ) 
              join pht_sessions_receivers as sr on s.id = sr.session_id) 
              join pht_receivers as r on r.id = sr.receiver_id 
            where p.pcode = '%s'""" % self.pcode)])

    def isComplete(self):
        if self.dss_project is not None:
            return self.dss_project.complete
        else:
            return None

    # *** End Section: accessing the corresponding DSS project

    def setSemester(self, semester):
        "Uses semester name to set the correct object."
        try:
            self.semester = Semester.objects.get(semester = semester)
            self.save()
        except:
            pass

    def hasObsType(self, obsType, contains = False):
        "Does this proposal have the given observation type?"
        if contains:
            ts = self.observing_types.filter(type__icontains = obsType)
        else:
            ts = self.observing_types.filter(type = obsType)
        return len(ts) > 0
        
    @staticmethod
    def semestersUsed():
        "Returns only the distinct semesters used by all Proposals"
        sems = {}
        for p in Proposal.objects.all().order_by('pcode'):
            if p.semester.semester not in sems:
                sems[p.semester] = True
        return sems.keys()

    @staticmethod
    def createFromDssProject(project, pst):
        """
        Creates a new Proposal instance initialized using a DSS Project.
        """
        proposalType  = ProposalType.objects.get(type = "Director's Discretionary Time")
        status        = Status.objects.get(name = 'Submitted')
        abstract      = '' if project.abstract is None else project.abstract
        semester      = Semester.objects.get(semester = project.semester.semester)
        proposal = Proposal(pst_proposal_id = 0
                          , proposal_type   = proposalType
                          , status          = status
                          , semester        = semester
                          , pcode           = project.pcode
                          , create_date     = datetime.now()
                          , modify_date     = datetime.now()
                          , submit_date     = datetime.now()
                          , title           = project.name
                          , abstract        = abstract
                          , joint_proposal  = pst.isJointProposal(project.pcode)
                          )

        proposal.save()
        return proposal

    @staticmethod
    def createFromSqlResult(result):
        """
        Creates a new Proposal instance initialized using the result from
        an SQL query.
        """

        pcode         = result['PROP_ID'].replace('/', '')
        proposalType  = ProposalType.objects.get(type = result['PROPOSAL_TYPE'])
        status        = Status.objects.get(name = result['STATUS'].title())
        submit_date  = result['SUBMITTED_DATE'] \
            if result['SUBMITTED_DATE'] != 'None' \
            else datetime.now().strftime("%Y-%M-%d %H:%m:%S")

        proposal = Proposal(pst_proposal_id = result['proposal_id']
                          , proposal_type   = proposalType
                          , status          = status
                          , pcode           = pcode
                          , create_date     = result['CREATED_DATE']
                          , modify_date     = result['MODIFIED_DATE']
                          , submit_date     = submit_date 
                          , title           = result['TITLE']
                          , abstract        = result['ABSTRACT']
                          , joint_proposal  = result['JOINT_PROPOSAL_TYPE'].lower() != 'not a joint proposal'
                          )

        proposal.save()

        try:
            author      = Author.createFromSqlResult(result, proposal)
            proposal.pi = author
        except:
            pass

        proposal.save()
        return proposal

