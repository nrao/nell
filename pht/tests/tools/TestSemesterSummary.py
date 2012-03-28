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

from pht.tools.reports import SemesterSummary
from scheduler.models  import Observing_Type

class TestSemesterSummary(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def test_report(self):

        # I'm too lazy to fix the scheduler.json - missing commissioning
        c = Observing_Type.objects.get_or_create(type = 'commissioning')

        ss = SemesterSummary.SemesterSummary('test_SemesterSummary.pdf'
                                            , semester = '11A')
