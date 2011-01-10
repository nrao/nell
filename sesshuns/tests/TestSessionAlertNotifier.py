from test_utils.NellTestCase import NellTestCase
from nell.utilities.SessionAlertNotifier import SessionAlertNotifier
from sesshuns.models         import *
from TestSessionAlertBase    import TestSessionAlertBase

class TestSessionAlertNotifier(TestSessionAlertBase):

    def setUp(self):
        super(TestSessionAlertNotifier, self).setUp()

    def test_setWindowDisabledDssTeam(self):
        self.makeWindowedSession(start_date = date(2009, 4, 5), duration = 7)
        sn = SessionAlertNotifier(unknown = self.window
                                , test   = True
                                , type   = "disabled_dss_team"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unenabled windowed session(s) about to begin" in txt)

    def test_setWindowDisabledObservers(self):
        self.makeWindowedSession(start_date = date(2009, 4, 5), duration = 7)
        sn = SessionAlertNotifier(unknown = self.window
                                , test   = True
                                , type   = "disabled_observers"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning, GBT windowed session Low Frequency With No RFI is not enabled will likely not be scheduled" in txt)
        self.failUnless("2009-04-05 through 2009-04-11 is not yet enabled" in txt)

    def test_setElectiveDisabledDssTeam(self):
        self.makeElectiveSession()
        sn = SessionAlertNotifier(unknown = self.elective
                                , test   = True
                                , type   = "disabled_dss_team"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unenabled elective session(s) about to begin" in txt)

    def test_setElectiveDisabledObservers(self):
        self.makeElectiveSession()
        sn = SessionAlertNotifier(unknown = self.elective
                                , test   = True
                                , type   = "disabled_observers"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning, GBT elective session Low Frequency With No RFI is not enabled will likely not be scheduled" in txt)
        self.failUnless("runs on 2011-01-05 00:00:00, 2011-01-07 00:00:00, 2011-01-09 00:00:00 is not yet enabled" in txt)

    def test_setFixedDisabledDssTeam(self):
        self.makeFixedSession()
        sn = SessionAlertNotifier(unknown = self.fixed
                                , test    = True
                                , type    = "disabled_dss_team"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning - unenabled fixed session(s) about to begin" in txt)

    def test_setFixedDisabledObservers(self):
        self.makeFixedSession()
        sn = SessionAlertNotifier(unknown = self.fixed
                                , test    = True
                                , type    = "disabled_observers"
                                )
        txt = sn.email.GetText()
        self.failUnless("Subject: Warning, GBT fixed session Low Frequency With No RFI is not enabled will likely not be scheduled" in txt)
        self.failUnless("runs on 2011-01-09 is not yet enabled" in txt)

