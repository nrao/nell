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

from test_utils              import NellTestCase
from scheduler.tests.utils   import create_sesshun
from nell.utilities.notifiers import ElecAlertNotifier
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestElecAlertNotifier(NellTestCase):

    def setUp(self):
        super(TestElecAlertNotifier, self).setUp()

        self.project = Project()
        self.project_adapter = ProjectHttpAdapter(self.project)
        pdata = {"semester"   : "09A"
               , "pcode"      : "AGBT09C-047"
               , "type"       : "science"
               , "total_time" : "10.0"
               , "PSC_time"   : "10.0"
               , "sem_time"   : "10.0"
               , "grade"      : "4.0"
               , "notes"      : "notes"
               , "schd_notes" : "scheduler's notes"
        }
        self.project_adapter.update_from_post(pdata)

        # make a session
        self.sesshun = create_sesshun()
        self.sesshun.session_type = \
            Session_Type.objects.get(type = "elective")
        self.sesshun.project = self.project

        # make an elective
        self.elective = Elective(
                   session = self.sesshun
                 , complete = False)
        self.elective.save()

        # make a couple of periods
        dates = ['2009-04-02', '2009-04-09']
        for date in dates:
            fdata = {'session'  : self.sesshun.id
                   , 'date'     : date
                   , 'time'     : '10:00'
                   , 'duration' : 4.0
                   , 'backup'   : False}
            period = Period()
            period_adapter = PeriodHttpAdapter(period)
            period_adapter.init_from_post(fdata, 'UTC')

            # link the period and elective
            period.elective = self.elective
            period.save()

    def test_setElective(self):

        en = ElecAlertNotifier(elective = self.elective
                             , test = True
                             , log = False
                              )

        txt = en.email.GetText()
        self.failUnless("Subject: Blackout dates will prevent scheduling AGBT09C-047" in txt)
        self.failUnless("2009-04-02 through" in txt)

        en = ElecAlertNotifier(elective = self.elective
                             , test = True
                             , log = False
                              )

        email = en.email
        txt = email.GetText()
        self.failUnless("Subject: Blackout dates will prevent scheduling AGBT09C-047" in txt)

