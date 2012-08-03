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

from pht.tools.reports.LstPressureReport import LstPressureReport
from scheduler.models  import Observing_Type
from scheduler.models  import Semester as DSSSemester

class TestLstPressureReport(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):

        # too lazy to re create 'scheduler.json', so put in the
        # future semesters we need
        for i in range(13, 33):
            for sem in ['A', 'B']:
                semester = "%s%s" % (i, sem)
                s = DSSSemester(semester = semester)
                s.save()
    
    def test_report(self):

        # I'm too lazy to fix the scheduler.json - missing commissioning
        c = Observing_Type.objects.get_or_create(type = 'commissioning')

        f = file('LstPressures.pdf', 'w')
        lst = LstPressureReport(f)
        lst.report(debug = True)
        
