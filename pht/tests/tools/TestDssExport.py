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
from pht.tools.database import DssExport

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

    def test_exportProposal(self):
        export   = DssExport()
        project  = export.exportProposal(self.proposal.pcode)

        self.assertEqual(self.proposal.pcode, project.pcode)
        a = project.allotments.all()[0]
        self.assertEqual(a.psc_time, self.session.allotment.allocated_time)

        self.assertTrue(project.investigator_set.filter(
              user__pst_id = self.proposal.pi.pst_person_id)[0].principal_investigator)

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
        self.assertEqual(expected_starts
                       , [dp.start for dp in dss_session.period_set.all().order_by('start')])

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
        self.assertEqual(len(ps), len(dss_session.period_set.all()))

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
