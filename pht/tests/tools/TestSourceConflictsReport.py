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

from django.test         import TestCase

from datetime import datetime, date, timedelta

from scheduler  import models as dss
from pht.tools.database import DssExport
from pht.models import *
from pht.utilities import *
from pht.httpadapters.SessionHttpAdapter import SessionHttpAdapter
from pht.tools.SourceConflicts import SourceConflicts
from pht.tools.reports.SourceConflictsReport import SourceConflictsReport
from pht.tests.utils import *

class TestSourceConflictsReport(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']


    def setUp(self):

        # get the one proposal and it's one session
        proposal = Proposal.objects.all()[0]
        self.proposal = proposal
        for s in self.proposal.session_set.all():
            s.grade = SessionGrade.objects.get(grade = 'A')
            s.save()

        s = proposal.session_set.all()[0]

        # give it some values so it will show up in plot
        s.grade = SessionGrade.objects.get(grade = 'A')
        s.target.min_lst = 0.0
        s.target.max_lst = hr2rad(12.5)
        s.target.save()
        time = 6.5 # hrs
        s.allotment.allocated_time = time # hrs
        s.allotment.save()
        s.save()
        self.session = s

    # TBF: stick this in a utility somewhere        
    def createSession(self, p):
        "Create a new session for the tests"
        return createSession(p)

    def createSrc(self, proposal, ra = 0.0, dec = 0.0):
        src = Source(proposal = proposal
                  , ra = ra
                  , dec = dec
                     )
        src.save()
        return src

    def test_findConflicts(self):

        s = self.proposal.session_set.all()[0]
        src0 = self.proposal.source_set.all()[0]
        tpcode = self.proposal.pcode
         
        # create a new proposal w/ sessions and sources
        newP = createProposal() 
        newP.pi = Author.objects.all()[0]
        newP.save()
        newS = self.createSession(newP)
        newS.grade = SessionGrade.objects.get(grade = 'A')
        newS.receivers.add(Receiver.objects.get(abbreviation = 'Q'))
        newS.receivers.add(Receiver.objects.get(abbreviation = '800'))
        newS.save()
        # second session isn't graded 
        newS2 = self.createSession(newP)
        newS2.grade = None 
        newS2.receivers.add(Receiver.objects.get(abbreviation = 'Q'))
        newS2.receivers.add(Receiver.objects.get(abbreviation = '800'))
        newS2.save()
        # make conflict
        src1 = self.createSrc(newP) 
        src1.target_name = src0.target_name
        src1.ra = src0.ra 
        src1.dec = src0.dec 
        src1.save()
        # make another conflict
        src2 = self.createSrc(newP) 
        src2.target_name = src0.target_name + "!"
        src2.ra = src0.ra + (src0.ra*0.0002)
        src2.dec = src0.dec - (src0.dec*0.0002)
        src2.save()

        # turn the crank
        sc = SourceConflicts()
        sc.findConflicts()
        cf = sc.conflicts

        # now create the report
        ps = Proposal.objects.all()
        filename = '12A'
        scr = SourceConflictsReport('sourceConflictsReport-%s-all.pdf' % filename)
        sc.filterConflicts(0)
        scr.report(sc.filteredConflicts, semester = '12A', level = 0)

        # no explicit tests - if this doesn't blow up we're good.
