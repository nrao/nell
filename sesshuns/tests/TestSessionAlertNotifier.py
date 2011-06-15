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

from datetime  import date

from test_utils.NellTestCase import NellTestCase
from nell.utilities.notifiers import SessionAlertNotifier
from scheduler.models         import *
from TestSessionAlertBase    import TestSessionAlertBase

class TestSessionAlertNotifier(TestSessionAlertBase):

    def setUp(self):
        super(TestSessionAlertNotifier, self).setUp()

    def test_setWindowDisabledDssTeam(self):
        self.makeWindowedSession(start_date = date(2009, 4, 5), duration = 7)
        sn = SessionAlertNotifier(unknown = self.window
                                , test   = True
                                , type   = "dss_team"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unenabled windowed session(s) about to begin" in txt)

    def test_setWindowDisabledObservers(self):
        self.makeWindowedSession(start_date = date(2009, 4, 5), duration = 7)
        sn = SessionAlertNotifier(unknown = self.window
                                , test   = True
                                , type   = "observers"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning, GBT windowed session Low Frequency With No RFI is not enabled will likely not be scheduled" in txt)
        self.failUnless("2009-04-05 through 2009-04-11 is not yet enabled" in txt)

    def test_setElectiveDisabledDssTeam(self):
        self.makeElectiveSession()
        sn = SessionAlertNotifier(unknown = self.elective
                                , test   = True
                                , type   = "dss_team"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unenabled elective session(s) about to begin" in txt)
        sn = SessionAlertNotifier(unknown = self.elective
                                , test   = True
                                , type   = "dss_team"
                                , flag   = "authorized"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unauthorized elective session(s) about to begin" in txt)

    def test_setElectiveDisabledObservers(self):
        self.makeElectiveSession()
        sn = SessionAlertNotifier(unknown = self.elective
                                , test   = True
                                , type   = "observers"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning, GBT elective session Low Frequency With No RFI is not enabled will likely not be scheduled" in txt)
        self.failUnless("runs on 2011-01-05 00:00:00, 2011-01-07 00:00:00, 2011-01-09 00:00:00 is not yet enabled" in txt)

    def test_setFixedDisabledDssTeam(self):
        self.makeFixedSession()
        sn = SessionAlertNotifier(unknown = self.fixed
                                , test    = True
                                , type    = "dss_team"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unenabled fixed session(s) about to begin" in txt)

    def test_setFixedDisabledObservers(self):
        self.makeFixedSession()
        sn = SessionAlertNotifier(unknown = self.fixed
                                , test    = True
                                , type    = "observers"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning, GBT fixed session Low Frequency With No RFI is not enabled will likely not be scheduled" in txt)
        self.failUnless("runs on 2011-01-09 is not yet enabled" in txt)

