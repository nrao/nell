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

from   Notifier import Notifier 
import nose
import os
import unittest

class TestNotifier(unittest.TestCase):

    def test_enabledLogging(self):
        # Don't send emails, but write out the log file.
        message  = "test test test"
        notifier = Notifier(test = True, log = True)
        notifier.startLogging()
        notifier.logMessage(message)
        notifier.stopLogging()

        file     = open(notifier.logfilename, "r")
        contents = file.read()
        self.assertTrue(message in contents)
        self.assertTrue("Notification sent on" in contents)
        file.close()

        os.remove(notifier.logfilename)

    def test_disbledLogging(self):
        # Don't send emails, and don't write out the log file.
        message  = "test test test"
        notifier = Notifier(test = True, log = False)
        notifier.startLogging()
        notifier.logMessage(message)
        notifier.stopLogging()

        self.assertEquals(None, notifier.logfilename)

    def test_getAndSetAddresses(self):
        notifier  = Notifier(skipEmails = "ashelton@nrao.edu"
                           , test       = True
                           , log        = False)
        addresses = ["ashelton@nrao.edu", "dora@explorer.com"]

        notifier.setAddresses(addresses)
        results = notifier.getAddresses()

        self.assertEquals(results, ["dora@explorer.com"])

    def test_getAndSetSubject(self):
        notifier  = Notifier(test = True, log = False)
        subject   = "Send cash now!"

        notifier.setSubject(subject)
        results = notifier.getSubject()

        self.assertEquals(results, subject)

    def test_getAndSetBody(self):
        notifier  = Notifier(test = True, log = False)
        body      = "Yadda yadda yadda"

        notifier.setBody(body)
        results = notifier.getBody()

        self.assertEquals(results, body)

    def test_notify(self):
        # Not much to test, just make sure it doesn't barf.
        Notifier(test = True, log = False).notify()

if __name__ == "__main__":
    unittest.main()
