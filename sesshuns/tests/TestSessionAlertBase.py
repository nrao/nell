from datetime  import date
from test_utils.NellTestCase import NellTestCase
from scheduler.tests.utils                   import create_sesshun
from scheduler.httpadapters   import *
from scheduler.models  import *

class TestSessionAlertBase(NellTestCase):

    def setUp(self):
        super(TestSessionAlertBase, self).setUp()
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

    def makeSession(self):
        # make a session
        self.sesshun = create_sesshun()
        self.sesshun.project = self.project
        self.sesshun.save()

    def makeWindowedSession(self, start_date = date(2011, 1, 1), duration = 4):
        self.makeSession()
        self.sesshun.session_type = \
            Session_Type.objects.get(type = "windowed")
        self.sesshun.save()

        # make the first window
        self.window = Window(session = self.sesshun
                           , total_time = 4.0
                           , complete = False)
        self.window.save()
        wr = WindowRange(window     = self.window
                       , start_date = start_date
                       , duration   = duration)
        wr.save()               

        # make a period for it
        fdata = {'session'  : self.sesshun.id
               , 'date'     : start_date.strftime("%Y-%m-%d")
               , 'time'     : '10:00'
               , 'duration' : duration
               , 'backup'   : False}
        period = Period()
        period_adapter = PeriodHttpAdapter(period)
        period_adapter.init_from_post(fdata, 'UTC')

        # link the period and window
        period.window = self.window
        period.save()
        self.window.default_period = period
        self.window.save()

    def makeElectiveSession(self):
        self.makeSession()
        self.sesshun.session_type = \
            Session_Type.objects.get(type = "elective")
        self.sesshun.save()

        self.elective = Elective(session = self.sesshun, complete = False)
        self.elective.save()
        pa            = Period_Accounting(scheduled = 0.0)
        pa.save()
        period1 = Period(session  = self.sesshun
                       , start    = date(2011, 1, 5)
                       , duration = 4
                       , state    = Period_State.get_state("P")
                       , accounting = pa
                       , elective   = self.elective
                       )
        period1.save()

        pa            = Period_Accounting(scheduled = 0.0)
        pa.save()
        period2 = Period(session  = self.sesshun
                       , start    = date(2011, 1, 7)
                       , duration = 4
                       , state    = Period_State.get_state("P")
                       , accounting = pa
                       , elective   = self.elective
                       )
        period2.save()

        pa            = Period_Accounting(scheduled = 0.0)
        pa.save()
        period3 = Period(session  = self.sesshun
                       , start    = date(2011, 1, 9)
                       , duration = 4
                       , state    = Period_State.get_state("P")
                       , accounting = pa
                       , elective   = self.elective
                       )
        period3.save()

    def makeFixedSession(self):
        self.makeSession()
        self.sesshun.session_type = \
            Session_Type.objects.get(type = "fixed")
        self.sesshun.save()

        pa            = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.fixed = Period(session  = self.sesshun
                          , start    = date(2011, 1, 9)
                          , duration = 4
                          , state    = Period_State.get_state("P")
                          , accounting = pa
                           )
        self.fixed.save()

