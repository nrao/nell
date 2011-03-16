from datetime    import date, datetime, timedelta

from test_utils.NellTestCase import NellTestCase
from nell.utilities.database import SessionAlerts
from scheduler.models         import *
from scheduler.httpadapters   import *
from scheduler.tests.utils                   import create_sesshun
from TestSessionAlertBase    import TestSessionAlertBase

class TestSessionAlerts(TestSessionAlertBase):

    def setUp(self):
        super(TestSessionAlerts, self).setUp()

    def testFindDisabledWindowedSessionAlerts(self):
        self.makeWindowedSession(start_date = date(2009, 4, 5)
                               , duration   = 7
                                )

        sa = SessionAlerts.SessionAlerts()
        w  = first(Window.objects.all())
        w.session.status.enabled = False
        w.session.status.save()

        # Find alerts 20 days before window
        alerts = sa.findDisabledSessionAlerts(now = w.start_datetime() - timedelta(days = 20))
        self.assertEqual(len(alerts), 0)

        # Find alerts 10 days before window
        alerts = sa.findDisabledSessionAlerts(now = w.start_datetime() - timedelta(days = 10))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the start of the window
        alerts = sa.findDisabledSessionAlerts(now = w.start_datetime())
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the default period
        alerts = sa.findDisabledSessionAlerts(now = w.default_period.start)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts after the default period, should be zero
        alerts = sa.findDisabledSessionAlerts(now = w.default_period.start + timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

    def testFindDisabledWindowedSessionAlertsCritical(self):
        """
            Critical being within 4 days of the window.
        """
        self.makeWindowedSession(start_date = date(2009, 4, 5)
                               , duration   = 7
                                )

        sa = SessionAlerts.SessionAlerts()
        sa.stageBoundary = 4
        w  = first(Window.objects.all())
        w.session.status.enabled = False
        w.session.status.save()

        # Find alerts 10 days before window
        alerts = sa.findDisabledSessionAlerts(now = w.start_datetime() - timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

        # Find alerts 4 days before window
        alerts = sa.findDisabledSessionAlerts(now = w.start_datetime() - timedelta(days = 4))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the start of the window
        alerts = sa.findDisabledSessionAlerts(now = w.start_datetime())
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the default period
        alerts = sa.findDisabledSessionAlerts(now = w.default_period.start)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts after the default period, should be zero
        alerts = sa.findDisabledSessionAlerts(now = w.default_period.start + timedelta(days = 4))
        self.assertEqual(len(alerts), 0)

    def testFindDisabledElectiveSessionAlerts(self):
        self.makeElectiveSession() 

        sa = SessionAlerts.SessionAlerts()
        e  = first(Elective.objects.all())
        e.session.status.enabled = False
        e.session.status.save()
        start, end = e.periodDateRange()

        # Find alerts 20 days before window
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 20))
        self.assertEqual(len(alerts), 0)

        # Find alerts 10 days before window
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 10))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the start of the window
        alerts = sa.findDisabledSessionAlerts(now = start)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the end of the elective
        alerts = sa.findDisabledSessionAlerts(now = end)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts after the end of the elective, should be zero
        alerts = sa.findDisabledSessionAlerts(now = end + timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

    def testFindDisabledElectiveSessionAlertsCritical(self):
        """
            Critical being within 4 days of the elective.
        """
        self.makeElectiveSession() 

        sa = SessionAlerts.SessionAlerts()
        sa.stageBoundary = 4
        e  = first(Elective.objects.all())
        e.session.status.enabled = False
        e.session.status.save()
        start, end = e.periodDateRange()

        # Find alerts 10 days before window
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

        # Find alerts 4 days before window
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 4))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the start of the window
        alerts = sa.findDisabledSessionAlerts(now = start)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the end of the elective
        alerts = sa.findDisabledSessionAlerts(now = end)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts after the end of the elective, should be zero
        alerts = sa.findDisabledSessionAlerts(now = end + timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

    def testFindDisabledFixedSessionAlerts(self):
        self.makeFixedSession() 

        sa = SessionAlerts.SessionAlerts()
        p  = first(Period.objects.filter(session__session_type__type = 'fixed'))
        p.session.status.enabled = False
        p.session.status.save()
        start = p.start

        # Find alerts 20 days before fixed period
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 20))
        self.assertEqual(len(alerts), 0)

        # Find alerts 10 days before fixed period
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 10))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the start of the fixed period
        alerts = sa.findDisabledSessionAlerts(now = start)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts after the fixed period, should be zero
        alerts = sa.findDisabledSessionAlerts(now = start + timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

    def testFindDisabledFixedSessionAlertsCritical(self):
        self.makeFixedSession() 

        sa = SessionAlerts.SessionAlerts()
        sa.stageBoundary = 4
        p  = first(Period.objects.filter(session__session_type__type = 'fixed'))
        p.session.status.enabled = False
        p.session.status.save()
        start = p.start

        # Find alerts 10 days before fixed period
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 10))
        self.assertEqual(len(alerts), 0)

        # Find alerts 4 days before fixed period
        alerts = sa.findDisabledSessionAlerts(now = start - timedelta(days = 4))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts at the start of the fixed period
        alerts = sa.findDisabledSessionAlerts(now = start)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].id, 1)

        # Find alerts after the fixed period, should be zero
        alerts = sa.findDisabledSessionAlerts(now = start + timedelta(days = 4))
        self.assertEqual(len(alerts), 0)

    def xtestRaiseAlerts(self):
        self.makeFixedSession() 

        sa = SessionAlerts.SessionAlerts(stageBoundary = 4)
        p  = first(Period.objects.filter(session__session_type__type = 'fixed'))
        p.session.status.enabled = False
        p.session.status.save()
        start = p.start

        sa.raiseAlerts(now = start - timedelta(days = 4))
