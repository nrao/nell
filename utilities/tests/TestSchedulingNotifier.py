# Copyright (C) 2008 Associated Universities, Inc. Washington DC, USA.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 675 Mass Ave Cambridge, MA 02139, USA.
#
# Correspondence concerning GBT software should be addressed as follows:
#     GBT Operations
#     National Radio Astronomy Observatory
#     P. O. Box 2
#     Green Bank, WV 24944-0002 USA

if __name__ == "__main__":
    import sys
    sys.path[1:1] = [".."]

from   datetime           import datetime
from   SchedulingNotifier import SchedulingNotifier 
import unittest

class DummyPeriod:
    def __init__(self, deleted = False):
        self.start      = datetime(2009, 9, 28, 9)
        self.duration   = 4.5
        self.session    = DummySession()
        self.accounting = DummyAccounting()
        self.deleted    = deleted

    def isDeleted(self):
        return self.deleted

    def end(self):
        return datetime(2009, 9, 28, 13, 30)

class DummySession:
    def __init__(self):
        self.project = DummyProject()
        self.name    = "TestSession 1"

    def receiver_list_simple(self):
        return "L AND S"

class DummyProject:
    def __init__(self):
        self.observers = [DummyObserver()]
        self.pcode = "GBT09C-001"

    def get_sanctioned_observers(self):
        return self.observers
        
    def get_observers(self):
        return self.observers

    def principal_contact(self):
        return DummyUser("Paul Marganian", ["pmargani@nrao.edu"])

    def principal_investigator(self):
        return DummyUser("Paul Marganian", ["pmargani@nrao.edu"])

class DummyObserver:
    def __init__(self, user = None):
        self.user = user or DummyUser("Amy Shelton", ["ashelton@nrao.edu"])

class DummyUser:
    def __init__(self, name, emails):
        self.first_name, self.last_name = name.split(" ")
        self.emails = emails

    def getStaticContactInfo(self, use_cache = True):
        return {"emails": self.emails}

class DummyAccounting:
    def __init__(self, interesting = False):
        self.interesting = interesting 

    def of_interest(self):
        return self.interesting

class TestSchedulingNotifier(unittest.TestCase):
  
    def setUp(self):
        self.periods  = [DummyPeriod()]
        self.notifier = SchedulingNotifier(self.periods
                                         , test = True
                                         , log  = False)

    def test_createSubject(self):
        subject = self.notifier.getSubject()
        self.assertTrue('Your GBT project has been scheduled' in subject)

    def test_createStaffSubject(self):
        self.notifier.createStaffSubject()
        subject = self.notifier.getSubject()
        self.assertTrue('GBT schedule for' in subject)

    def test_createAddresses(self):
        addresses = self.notifier.getAddresses()
        self.assertTrue('ashelton@nrao.edu' in addresses)
        self.assertTrue('pmargani@nrao.edu' in addresses)

    def test_createStaffAddresses(self):
        self.notifier.createStaffAddresses()
        addresses = self.notifier.getAddresses()
        self.assertTrue('gbtinfo@gb.nrao.edu' in addresses)
        self.assertTrue('gbtops@gb.nrao.edu' in addresses)
        self.assertTrue('gbtime@gb.nrao.edu' in addresses)

    def test_createBody(self):
        body = self.notifier.getBody()
        self.assertTrue('The schedule for the period' in body)
        self.assertTrue('Changes' not in body)
        self.assertTrue('removed' not in body)

    def test_getSessionTable(self):
        info = self.notifier.getSessionTable(self.periods)

        self.assertTrue('Start' in info)
        self.assertTrue('ET' in info)
        self.assertTrue('UT' in info)
        self.assertTrue('LST' in info)

        for p in self.periods:
            self.assertTrue(p.start.strftime('%b %d %H:%M') in info)
            self.assertTrue(str(p.duration) in info)
            self.assertTrue(p.session.project.principal_investigator().last_name[:9] in info)
            self.assertTrue(p.session.receiver_list_simple()[:9] in info)
            self.assertTrue(p.session.name in info)

    def test_notify(self):
        # Not much to test, just make sure it doesn't barf.
        self.notifier.notify()

    def test_rescheduled_periods(self):
        self.periods[0].accounting = DummyAccounting(True) # Modify

        notifier = SchedulingNotifier(self.periods
                                    , test = True
                                    , log  = False)
        body     = notifier.getBody()

        self.assertTrue('Changes' in body)
        self.assertTrue('rescheduled' in body)
        self.assertTrue('removed' not in body)
        self.assertEqual([], notifier.deletedPeriods)

        notifier.createDeletedAddresses()
        self.assertEqual([], notifier.getAddresses())

        self.periods[0].accounting = DummyAccounting() # Reset

    def test_deleted_periods(self):
        periods  = [DummyPeriod(True)]
        notifier = SchedulingNotifier(periods
                                    , test = True
                                    , log  = False)
        body     = notifier.getBody()

        self.assertTrue('Changes' in body)
        self.assertTrue('removed' in body)
        self.assertEqual(periods, notifier.deletedPeriods)

        notifier.createDeletedAddresses()
        addresses = notifier.getAddresses()
        self.assertTrue('ashelton@nrao.edu' in addresses)
        self.assertTrue('pmargani@nrao.edu' in addresses)

if __name__ == "__main__":
    unittest.main()
