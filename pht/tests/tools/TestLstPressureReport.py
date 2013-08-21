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
from scheduler.models  import Sponsor as DSSSponsor
from pht.tools.LstPressures import LstPressures
from pht.utilities import *
from pht.models import *

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
    
        # I'm too lazy to fix the scheduler.json - missing commissioning
        c = Observing_Type.objects.get_or_create(type = 'commissioning')
        
        self.sponsor = DSSSponsor(name = "WVU", abbreviation = "WVU")
        self.sponsor.save()

        # get the one proposal and it's one session
        self.proposal = Proposal.objects.all()[0]
        s = self.proposal.session_set.all()[0]

        # give it some values so it will show up 
        s.grade = SessionGrade.objects.get(grade = 'A')
        s.target.min_lst = 0.0
        s.target.max_lst = hr2rad(12.5)
        s.target.save()
        time = 6.5 # hrs
        s.allotment.allocated_time = time # hrs
        s.allotment.allocated_repeats = 1 
        s.allotment.save()
        s.save()
        self.session = s

    def test_report(self):

        f = file('LstPressures.pdf', 'w')
        lst = LstPressureReport(f)
        lst.report(debug = True)

    def test_report_sponsored(self):

        f = file('LstPressures.pdf', 'w')
        r = LstPressureReport(f)
        # Make sure are session belongs to the next semester,
        # no matter when we are running this test.
        # This is a 12A session, that starts 2012-02-01.
        today = datetime(2012, 1, 15)
        r.lst = LstPressures(today = today)

        # make this session sponsored
        self.session.proposal.sponsor = self.sponsor
        self.session.proposal.save()

        r.report(debug = True, hideSponsors = False)
        
