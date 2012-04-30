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

from scheduler  import models as dss
from pht.models import *
from pht.tools.database import DssExport

class TestDssExport(TestCase):

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def test_exportProposal(self):
        proposal  = Proposal.objects.get(pcode = 'GBT12A-002')
        session   = proposal.session_set.all()[0]
        session.allotment.allocated_time = session.allotment.requested_time
        session.allotment.save()
        session.grade = SessionGrade.objects.get(grade = 'A')
        session.save()

        export   = DssExport()
        project  = export.exportProposal(proposal.pcode)

        self.assertEqual(proposal.pcode, project.pcode)
        a = project.allotments.all()[0]
        self.assertEqual(a.psc_time, session.allotment.allocated_time)

        self.assertTrue(project.investigator_set.filter(
              user__pst_id = proposal.pi.pst_person_id)[0].principal_investigator)
