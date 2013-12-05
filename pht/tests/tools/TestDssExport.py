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
from django.test.client  import Client
from django.test         import TestCase
from django.conf         import settings
from django.contrib.auth import models as m
from datetime            import datetime

from scheduler  import models as dss
from pht.models import *
from pht.tools.database import DssExport, PstInterface

class TestDssExport(TestCase):

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):
        self.proposal  = Proposal.objects.get(pcode = 'GBT12A-002')
        self.session   = self.proposal.session_set.all()[0]
        self.session.allotment.allocated_time = self.session.allotment.requested_time
        self.session.allotment.save()
        self.session.grade = SessionGrade.objects.get(grade = 'A')
        for source in self.proposal.source_set.all():
            self.session.sources.add(source)
        self.session.save()

    def addAuthor(self, proposal):

        # add me as another author;
        # here's how to do it from the DB:
        #pst = PstInterface()
        #marganian_id = 821
        #q = """
        #    select person.person_id, a.* 
        #    from (author as a 
        #      join userAuthentication as ua on ua.userAuthentication_id = a.user_id)
        #      join person on person.personAuthentication_id = ua.userAuthentication_id
        #    where person_id = %d
        #""" % marganian_id
        #pst.cursor.execute(q)
        #keys = pst.getKeys()
        #rows = pst.cursor.fetchall()
        #row = rows[0]
        
        # but we want to remove the link with the DB, so here's
        # all we need:
        pst = PstInterface()
        keys = ['person_id', 'author_id', 'objectversion', 'AFFILIATION', 'DOMESTIC', 'NEW_USER', 'EMAIL', 'ADDRESS', 'FIRST_NAME', 'LAST_NAME', 'PROFESSIONAL_STATUS', 'THESIS_OBSERVING', 'GRADUATION_YEAR', 'TELEPHONE', 'OLDAUTHOR_ID', 'DISPLAY_POSITION', 'STORAGE_ORDER', 'OTHER_AWARDS', 'SUPPORT_REQUESTER', 'SUPPORTED', 'BUDGET', 'ASSIGNMENT', 'proposal_id', 'user_id', 'dissertationPlan_id']
        row = (821L, 3352L, 0L, 'National Radio Astronomy Observatory ', '\x01', '\x00', 'pmargani@nrao.edu', None, 'Paul', 'Marganian', 'NRAO Staff', '\x00', None, '304-456-2202', '44370', 0L, 0L, None, '\x00', '\x00', 0.0, None, 961L, 823L, None)
        author = Author.createFromSqlResult(dict(zip(keys, map(pst.safeUnicode, row))), proposal)
        return author

    def test_exportProposal(self):

        # add an author to test more code - make it the contact
        author = self.addAuthor(self.proposal)
        self.proposal.contact = author
        self.proposal.save()

        export   = DssExport()
        project  = export.exportProposal(self.proposal.pcode)

        self.assertEqual(self.proposal.pcode, project.pcode)
        a = project.allotments.all()[0]
        self.assertEqual(a.psc_time, self.session.allotment.allocated_time)

        self.assertTrue(project.investigator_set.filter(
              user__pst_id = self.proposal.pi.pst_person_id)[0].principal_investigator)
       
        # should be 2 investigators, and I'm not the principal
        self.assertEqual(2, len(project.investigator_set.all()))      
        for i in project.investigator_set.all():
            self.assertEqual(i.principal_investigator
                           , i.user.last_name != 'Marganian' 
                            )
            self.assertEqual(i.principal_contact
                           , i.user.last_name == 'Marganian' 
                            )

    def test_exportFlags(self):

        export   = DssExport()

        s = self.proposal.session_set.all()[0]

        # set all the flags, and see how the transfer
        s.flags.thermal_night = True
        s.flags.optical_night = True
        s.flags.rfi_night = True
        s.flags.transit_flat = True
        s.flags.guaranteed = True
        s.flags.save()

        project  = export.exportProposal(self.proposal.pcode)

        s = project.sesshun_set.all()[0]

        #self.assertTrue(s.guaranteed()) # TBF
        self.assertTrue(s.transit())
        # these two are mutually exclusive:
        self.assertEqual(False, s.RfiNight())
        self.assertTrue(s.PtcsNight())
        # TBF: what about optical ?

    def test_exportProposal2(self):


        # now make sure no allocated time keeps it from getting transferred
        s = self.proposal.session_set.all()[0]
        original_time =  s.allotment.allocated_time
        s.allotment.allocated_time = 0.0
        s.allotment.save()

        export   = DssExport()
        project  = export.exportProposal(self.proposal.pcode)

        # make sure it wasn't transferred
        self.assertEqual(self.proposal.pcode, project.pcode)
        self.assertEqual(len(self.proposal.session_set.all()) - 1
                       , len(project.sesshun_set.all()))

        # restore the allocated time, but make sure it has a failing grade
        s = self.proposal.session_set.all()[0]
        s.allotment.allocated_time = original_time 
        s.allotment.save()
        original_grade = s.grade
        s.grade = SessionGrade.objects.get(grade = 'N*')
        s.save()

        export   = DssExport()
        # we can't call exportProposal again, becasuse if the corresponding 
        # DSS Project exists already, it will go ahead and use it; and deleting
        # Projects is a pain in the ass.  Instead, just try to import the session.
        #project  = export.exportProposal(self.proposal.pcode)
        export.exportSession(s, project) 

        # make sure it still wasn't transferred - get them fresh from DB to be sure
        proposal = Proposal.objects.get(pcode = self.proposal.pcode)
        project = dss.Project.objects.get(pcode = project.pcode)
        self.assertEqual(len(proposal.session_set.all()) - 1
                       , len(project.sesshun_set.all()))

       
        # now restore the original grade, and we should see the session get exported
        s.grade = original_grade
        s.save()

        export.exportSession(s, project) 

        # make sure it WAS transferred - get them fresh from DB to be sure
        proposal = Proposal.objects.get(pcode = self.proposal.pcode)
        project = dss.Project.objects.get(pcode = project.pcode)
        self.assertEqual(len(proposal.session_set.all())
                       , len(project.sesshun_set.all()))


    def genPeriods(self):
        # now set it up for a custom sequence
        start = datetime(2011, 1, 1)
        dur = 2.5
        self.session.monitoring.start_time = start
        self.session.allotment.period_time = dur
        self.session.monitoring.custom_sequence = "1,3,5"
        self.session.monitoring.window_size = 4
        self.session.monitoring.save()

        # generate periods
        numPs = self.session.genPeriods()

    def test_exportFixedSession(self):
        self.genPeriods()
        self.session.session_type = SessionType.objects.get(type = 'Fixed')
        self.session.save()
        ps = self.session.period_set.all().order_by('start')

        export   = DssExport()
        project  = export.exportProposal(self.proposal.pcode)
        dss_session = project.sesshun_set.all()[0]
        self.assertEqual(dss_session.session_type.type, 'fixed')
        self.assertEqual(len(ps), len(dss_session.period_set.all()))

        expected_starts = [p.start for p in ps]
        dssPs = dss_session.period_set.all().order_by('start')
        self.assertEqual(expected_starts
                        , [dp.start for dp in dssPs])

        for i in range(len(ps)):
            self.assertEqual(dssPs[i].accounting.scheduled, ps[i].duration)

    def test_exportElectiveSession(self):
        self.genPeriods()
        ps = self.session.period_set.all().order_by('start')
        self.session.session_type = SessionType.objects.get(type = 'Elective')
        self.session.save()

        export   = DssExport()
        project  = export.exportProposal(self.proposal.pcode)
        dss_session = project.sesshun_set.all()[0]
        self.assertEqual(dss_session.session_type.type, 'elective')
        self.assertEqual(1, len(dss_session.elective_set.all()))
        self.assertEqual(len(ps), len(dss_session.elective_set.all()[0].periods.all()))
        dssPs = dss_session.period_set.all().order_by('start')
        self.assertEqual(len(ps), len(dssPs)) 

        for scheduled in [dp.accounting.scheduled for dp in dssPs]:
            self.assertEqual(0.0, scheduled)

    def test_exportWindowedSession(self):
        self.genPeriods()
        ps = self.session.period_set.all().order_by('start')
        self.session.session_type = SessionType.objects.get(type = 'Windowed')
        self.session.save()

        export   = DssExport()
        project  = export.exportProposal(self.proposal.pcode)
        dss_session = project.sesshun_set.all()[0]
        self.assertEqual(dss_session.session_type.type, 'windowed')
        self.assertEqual(0, len(dss_session.elective_set.all()))
        self.assertEqual(len(ps), len(dss_session.window_set.all()))
        self.assertEqual(len(ps), len(dss_session.period_set.all()))
        self.assertEqual(dss_session.window_set.all()[0].windowrange_set.all()[0].duration
                       , self.session.monitoring.window_size)
