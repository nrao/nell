from datetime                import date

from test_utils              import NellTestCase
from nell.utilities.notifiers import WinAlertNotifier
from scheduler.tests.utils                   import create_sesshun
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestWinAlertNotifier(NellTestCase):

    def setUp(self):
        super(TestWinAlertNotifier, self).setUp()

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
            Session_Type.objects.get(type = "windowed")
        self.sesshun.project = self.project

        # make the first window
        self.window = Window(session = self.sesshun
                 , total_time = 4.0
                 , complete = False)
        self.window.save()
        wr = WindowRange(window     = self.window
                       , start_date = date(2009, 4, 5)
                       , duration   = 7)
        wr.save()               

    def test_setWindow(self):

        wn = WinAlertNotifier(window = self.window
                            , level = 1 # level
                            , stage = 1 # stage
                            , test = True
                            , log = False
                            )

        txt = wn.email.GetText()
        self.failUnless("Subject: Blackout dates may prevent scheduling AGBT09C-047" in txt)
        self.failUnless(">10% of its possible scheduling time" in txt)
        self.failUnless("2009-04-05 through" in txt)

        wn = WinAlertNotifier(window = self.window
                            , level = 2 # level
                            , stage = 1 # stage
                            , test = True
                            , log = False
                            )

        email = wn.email
        txt = email.GetText()
        self.failUnless("Subject: Blackout dates will prevent scheduling AGBT09C-047" in txt)

