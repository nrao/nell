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

    def test_createFromSqlResult(self):

        sqlResult = {'SUPPORTED': u'\x00', 'FIRST_NAME': u'Carl', 'LAST_NAME': u'Gwinn', 'EMAIL': u'cgwinn@physics.ucsb.edu', 'OLD_PI': u'None', 'TITLE': u'Substructure in the Scattering Disk of Sgr A*', 'RELATED_PROPOSALS': u'', 'ASSIGNMENT': u'None', 'ABSTRACT': u'We propose observations to detect, or set limits on, substructure within the smooth scattering disk of the celebrated galactic center radio source SgrA*.  Such structure is predicted theoretically, and it may have been detected in observations of pulsars with RadioAstron, and in earlier observations of SgrA*. Results will place constraints on the spatial spectrum of the electron-density fluctuations that are responsible for the scattering.', 'CREATED_DATE': u'2013-01-26 18:18:54', 'contact_id': u'33166', 'JOINT_PROPOSAL_TYPE': u'Joint with GBT and VLA', 'OLD_CONTACT': u'None', 'DEADLINE_DATE': u'2013-02-01 22:30:00', 'PROCESSED': u'\x00', 'category2_id': u'None', 'STAFF_SUPPORT': u'Consultation', 'scienceCategory': u'Interstellar Medium', 'comments': u'', 'justificationFile_id': u'7403', 'MODIFIED_DATE': u'2013-02-04 21:57:56', 'user_id': u'2554', 'TELESCOPE': u'VLBA', 'OTHER_AWARDS': u'', 'reviewersConflict': u'\x00', 'allocated_hours': u'0.0', 'objectversion': u'0', 'principal_investigator_id': u'33166', 'RAPID_RESPONSE_TYPE': u'None', 'technicalCategory_id': u'78', 'category3_id': u'None', 'GRADUATION_YEAR': u'-1', 'person_id': u'2552', 'proposal_id': u'7917', 'disposition_letter': u'None', 'public': u'\x00', 'PRESENT': u'no', 'STATUS': u'SUBMITTED', 'trigger_criteria': u'None', 'dissertationPlan_id': u'None', 'PLAN_SUBMITTED': u'no', 'category1_id': u'None', 'SUPPORT_REQUESTER': u'\x00', 'DOMESTIC': u'\x01', 'PROFESSIONAL_STATUS': u'All Others', 'THESIS_OBSERVING': u'\x00', 'LOCK_MILLIS': u'0', 'STORAGE_ORDER': u'0', 'editor_id': u'33166', 'author_id': u'33166', 'SUBMITTED_DATE': u'2013-02-04 21:56:27', 'displayTechnicalReviews': u'\x00', 'DISPLAY_POSITION': u'0', 'LOCK_USER_ID': u'None', 'NEW_USER': u'\x00', 'PREV_PROP_IDS': u'None', 'PROPOSAL_TYPE': u'Regular', 'TELEPHONE': u'805-8932814', 'LOCK_USER_INFO': u'None', 'AFFILIATION': u'California at Santa Barbara, University of', 'BUDGET': u'0.0', 'OBSERVING_TYPE_OTHER': u'None', 'LEGACY_ID': u'BG221', 'ADDRESS': u'', 'PROP_ID': u'VLBA/13B-395', 'OLDAUTHOR_ID': u'2554', 'OLD_EDITOR': u'None'}

        p = Proposal.createFromSqlResult(sqlResult)
        pcode = 'VLBA13B-395'
        self.assertEqual(p.pcode, pcode)

        # now get fresh copy from db
        pdb = Proposal.objects.get(pcode = pcode)
        self.assertEqual(datetime(2013, 2, 4, 21, 56, 27), pdb.submit_date)
        self.assertEqual(datetime(2013, 2, 4, 21, 57, 56), pdb.modify_date)
        self.assertEqual(datetime(2013, 1, 26, 18, 18, 54), pdb.create_date)

        # now, recreate it, but w/ out the submit date
        pdb.delete()
        sqlResult['SUBMITTED_DATE'] = 'None'

        p = Proposal.createFromSqlResult(sqlResult)
        pcode = 'VLBA13B-395'
        self.assertEqual(p.pcode, pcode)

        # now get fresh copy from db
        pdb = Proposal.objects.get(pcode = pcode)
        self.assertEqual(datetime(2013, 2, 4, 21, 57, 56), pdb.modify_date)
        self.assertEqual(datetime(2013, 1, 26, 18, 18, 54), pdb.create_date)

        # the submit date should now be 'now'
        self.assertNotEqual(datetime(2013, 2, 4, 21, 56, 27), pdb.submit_date)
        frmt = '%Y-%m-%d %H:%M'
        now = datetime.now().strftime(frmt)
        self.assertEqual(now, pdb.submit_date.strftime(frmt))

        # demonstrate that as long as it's unicode, we're cool
        pdb.delete()
        a =  u'dog\xe0\xe1cat'
        sqlResult['ABSTRACT'] = a 
        p = Proposal.createFromSqlResult(sqlResult)
        pdb = Proposal.objects.get(pcode = pcode)
        self.assertEqual(a, pdb.abstract)


