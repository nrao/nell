from test_utils              import NellTestCase
from nell.utilities.FixedAlertNotifier import FixedAlertNotifier
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestFixedAlertNotifier(NellTestCase):

    def setUp(self):
        super(TestFixedAlertNotifier, self).setUp()

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
            Session_Type.objects.get(type = "fixed")
        self.sesshun.project = self.project

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

            period.save()

    def test_setFixed(self):

        en = FixedAlertNotifier(session = self.sesshun
                              , test = True
                              , log = False
                              )

        txt = en.email.GetText()
        self.failUnless("Subject: Blackout dates will prevent scheduling AGBT09C-047" in txt)
        self.failUnless("through 2009-04-09," in txt)

        en = FixedAlertNotifier(session = self.sesshun
                              , test = True
                              , log = False
                              )

        email = en.email
        txt = email.GetText()
        print txt
        self.failUnless("Subject: Blackout dates will prevent scheduling AGBT09C-047" in txt)

