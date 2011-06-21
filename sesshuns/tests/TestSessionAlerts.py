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

from datetime    import date, datetime, timedelta

from test_utils.NellTestCase import NellTestCase
from tools.alerts import SessionAlerts
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

        sa = SessionAlerts()
        w  = Window.objects.all()[0]
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

        sa = SessionAlerts()
        sa.stageBoundary = 4
        w  = Window.objects.all()[0]
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

        sa = SessionAlerts()
        e  = Elective.objects.all()[0]
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

        sa = SessionAlerts()
        sa.stageBoundary = 4
        e  = Elective.objects.all()[0]
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

        sa = SessionAlerts()
        p  = Period.objects.filter(session__session_type__type = 'fixed')[0]
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

        sa = SessionAlerts()
        sa.stageBoundary = 4
        p  = Period.objects.filter(session__session_type__type = 'fixed')[0]
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

        sa = SessionAlerts(stageBoundary = 4)
        p  = Period.objects.filter(session__session_type__type = 'fixed')[0]
        p.session.status.enabled = False
        p.session.status.save()
        start = p.start

        sa.raiseAlerts(now = start - timedelta(days = 4))
