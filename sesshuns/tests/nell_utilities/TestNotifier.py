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

from utilities.notifiers               import Notifier
from utilities.notifiers               import Email
from test_utils                        import NellTestCase
from datetime                          import datetime
from nell.utilities                    import TimeAgent

import os

class TestNotifier(NellTestCase):

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
        e1 = Email()
        e2 = Email()
        notifier.registerTemplate("test", e1)
        notifier.registerTemplate("frog", e2)
        notifier.setAddresses("test", addresses)
        notifier.setAddresses("frog", ["frog@pond", "toad@toadstool"])
        results = notifier.getAddresses("test")
        self.assertEquals(results, ["dora@explorer.com"])
        results = notifier.getAddresses("frog")
        self.assertEquals(results, ["frog@pond", "toad@toadstool"])

    def test_getAndSetSubject(self):
        notifier  = Notifier(test = True, log = False)
        subject1  = "Send cash now!"
        subject2  = "Flies are so yummy!"
        e1 = Email()
        e2 = Email()
        notifier.registerTemplate("test", e1)
        notifier.registerTemplate("frog", e2)
        notifier.setSubject("test", subject1)
        notifier.setSubject("frog", subject2)
        results = notifier.getSubject("test")
        self.assertEquals(results, subject1)
        results = notifier.getSubject("frog")
        self.assertEquals(results, subject2)

    def test_getAndSetBody(self):
        notifier  = Notifier(test = True, log = False)
        body1     = "Yadda yadda yadda"
        body2     = "Aren't they, though?"
        e1 = Email()
        e2 = Email()
        notifier.registerTemplate("test", e1)
        notifier.registerTemplate("frog", e2)
        notifier.setBody("test", body1)
        notifier.setBody("frog", body2)
        results = notifier.getBody("test")
        self.assertEquals(results, body1)
        results = notifier.getBody("frog")
        self.assertEquals(results, body2)

    def test_email_templates(self):
        notifier = Notifier(test = True, log = False)
        sender = "frog@pond"
        recipients = ["toad@toadstool", "salamander@leafpile"]
        subject = "Life is good!"
        body = "Living in the pond is heaven!"
        e1 = Email(sender = sender,
                   recipients = recipients,
                   subject = subject,
                   body = body)
        notifier.registerTemplate("pond", e1)
        e2 = notifier.cloneTemplate("pond")

        self.assertEquals(e2.GetSender(), sender)
        self.assertEquals(e2.GetRecipientList(), recipients)
        self.assertEquals(e2.GetSubject(), subject)
        self.assertEquals(e2.GetBody(), body)

        notifier.unregisterTemplate("pond")
        self.assertRaises(KeyError, notifier.cloneTemplate, "pond")

    def test_notify(self):
        # Not much to test, just make sure it doesn't barf.
        Notifier(test = True, log = False).notify()

