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

from django.db                 import models

from Author             import Author
from ObservingType      import ObservingType
from ScientificCategory import ScientificCategory
from Semester           import Semester
from Status             import Status
from ProposalType       import ProposalType

from datetime           import datetime

class Proposal(models.Model):

    pst_proposal_id = models.IntegerField(null = True)
    proposal_type   = models.ForeignKey(ProposalType)
    observing_types = models.ManyToManyField(ObservingType)
    status          = models.ForeignKey(Status)
    semester        = models.ForeignKey(Semester, null = True)
    pi              = models.ForeignKey('Author', related_name = "pi_on", null = True)
    investigators   = models.ManyToManyField('Author', related_name = 'investigator_on')
    sci_categories  = models.ManyToManyField(ScientificCategory)
    pcode           = models.CharField(max_length = 32, unique = True)
    create_date     = models.DateTimeField()
    modify_date     = models.DateTimeField()
    submit_date     = models.DateTimeField()
    total_time      = models.FloatField()  # Minutes
    title           = models.CharField(max_length = 512)
    abstract        = models.CharField(max_length = 2000)
    spectral_line   = models.CharField(max_length = 2000, null = True)
    joint_proposal  = models.BooleanField()

    class Meta:
        db_table  = "pht_proposals"
        app_label = "pht"

    def __str__(self):
        return self.pcode

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
        sems = []
        for p in Proposal.objects.all().order_by('pcode'):
            if p.semester.semester not in sems:
                sems.append(p.semester)
        return sems

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
                          , total_time      = 0.0 #result['total_time']
                          , title           = result['TITLE']
                          , abstract        = result['ABSTRACT']
                          , joint_proposal  = False #result['joint_proposal']
                          )

        proposal.save()
        author      = Author.createFromSqlResult(result, proposal)
        proposal.pi = author
        proposal.save()
        return proposal

