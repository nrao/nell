from test_utils.NellTestCase import NellTestCase
from nell.utilities.WinAlertNotifier import WinAlertNotifier
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestWinAlertNotifier(NellTestCase):

    def setUp(self):
        super(TestWinAlertNotifier, self).setUp()

        self.project = Project()
        self.project_adapter = ProjectHttpAdapter(self.project)
        pdata = {"semester"   : "09A"
               , "pcode"      : "WTF"
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
                 , start_date   = date(2009, 4, 5)
                 , duration    = 7
                 , total_time = 4.0
                 , complete = False)
        self.window.save()

    def test_setWindow(self):

        wn = WinAlertNotifier(window = self.window
                            , level = 1 # level
                            , stage = 1 # stage
                            , test = True
                            , log = False
                            )

        email = wn.email
        txt = email.GetText()
        self.failUnless("Subject: Blackout dates may prevent scheduling WTF" in txt)
        self.failUnless(">10% of the  possible time for scheduling" in txt)
        self.failUnless("2009-04-05 through" in txt)

        wn = WinAlertNotifier(window = self.window
                            , level = 2 # level
                            , stage = 1 # stage
                            , test = True
                            , log = False
                            )

        email = wn.email
        txt = email.GetText()
        self.failUnless("Subject: Blackout dates will prevent scheduling WTF" in txt)
                            
