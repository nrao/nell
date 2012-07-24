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

#import unittest
from django.test import TestCase

from scheduler.models import Project as DSSProject
from scheduler.models import Period as DSSPeriod
from scheduler.models import Period_State as DSSPeriod_State
from scheduler.models import Period_Accounting as DSSPeriod_Accounting

from pht.models import Proposal
from pht.models import Semester
from pht.httpadapters import SessionHttpAdapter
from utilities import TimeAccounting
from scheduler.tests.utils     import create_sesshun
from pht.tests.utils import *

from datetime import datetime, timedelta

class TestProposal(TestCase):

    fixtures = ['scheduler.json', 'proposal_GBT12A-002']

    def setUp(self):
        super(TestProposal, self).setUp()

        # this project has no allotments!
        self.project = DSSProject.objects.order_by('pcode').all()[0]

        # setup some periods
        self.start = datetime(2000, 1, 1, 0)
        self.end   = self.start + timedelta(hours = 12)
        times = [(datetime(2000, 1, 1, 0), 5.0, "one")
               , (datetime(2000, 1, 1, 5), 3.0, "two")
               , (datetime(2000, 1, 1, 8), 4.0, "three")
               ]
        self.ps = []
        state = DSSPeriod_State.objects.get(abbreviation = 'P')
        for start, dur, name in times:
            # each session has grade 4, time = 3 
            s = create_sesshun()
            s.name = name
            s.save()
            pa = DSSPeriod_Accounting(scheduled = dur)
            pa.save()
            p = DSSPeriod( session    = s
                      , start      = start
                      , duration   = dur
                      , state      = state
                      , accounting = pa
                      )
            p.save()
            self.ps.append(p)


        # Okay, now set up the corresponding proposal
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sqlResult = { 'PROP_ID' : self.project.pcode
                    , 'PROPOSAL_TYPE' : 'Regular'
                    , 'STATUS' : 'Draft'
                    , 'SUBMITTED_DATE' : now 
                    , 'CREATED_DATE' : now 
                    , 'MODIFIED_DATE' : now 
                    , 'TITLE' : 'Lynrd Sknyrd'
                    , 'ABSTRACT' : 'What song do you wanna hear?'
                    , 'proposal_id' : 0
                    , 'JOINT_PROPOSAL_TYPE' : 'Not a joint Proposal'
                    }
        proposal = Proposal.createFromSqlResult(sqlResult)
        proposal.dss_project = self.project
        proposal.setSemester(self.project.semester.semester)
        proposal.save()
        self.proposal = proposal

        self.ta = TimeAccounting()

    def tearDown(self):
        super(TestProposal, self).tearDown()

        for p in self.ps:
            s = p.session
            p.delete()
            s.delete()

    # TBF: stick this in a utility somewhere        
    def createSession(self, p):
        "Create a new session for the tests"
        return createSession(p)

    def test_requestedTime(self):

        p = Proposal.objects.get(pcode = 'GBT09A-001')
        self.assertEqual(0.0, p.requestedTime())
        # now get some requested time
        self.createSession(p)
        self.assertEqual(7.0, p.requestedTime())
        
    def test_timeAccounting(self):

        self.assertEqual(12.0, self.ta.getTime('time_billed', self.project))
        self.assertEqual(12.0, self.proposal.billedTime())

        self.assertEqual(12.0, self.ta.getTime('scheduled', self.project))
        self.assertEqual(12.0, self.proposal.scheduledTime())

        self.assertEqual(-12.0, self.ta.getTimeRemaining(self.project))
        self.assertEqual(-12.0, self.proposal.remainingTime())
