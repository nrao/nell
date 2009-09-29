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

from   emailNotifier import emailNotifier 
import os
import unittest

class TestEmailNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = emailNotifier()

    def tearDown(self):
        self.notifier = None

    def test_SetSmtp(self):
        self.notifier.SetSmtp("stuff")
        self.assertEquals("stuff", self.notifier.smtp)

    def test_SetFrom(self):
        self.notifier.SetFrom("stuff")
        self.assertEquals("stuff", self.notifier.frm)

    def test_SetTo(self):
        to = "ashelton@nrao.edu, dora@explorer.com"
        self.notifier.SetTo(to)
        self.assertEquals(["ashelton@nrao.edu", "dora@explorer.com"]
                        , self.notifier.to)

        to = "ashelton@nrao.edu; dora@explorer.com"
        self.notifier.SetTo(to)
        self.assertEquals(["ashelton@nrao.edu", "dora@explorer.com"]
                        , self.notifier.to)

        to = "ashelton@nrao.edu dora@explorer.com"
        self.notifier.SetTo(to)
        self.assertEquals(["ashelton@nrao.edu", "dora@explorer.com"]
                        , self.notifier.to)

        to = ["ashelton@nrao.edu", "dora@explorer.com"]
        self.notifier.SetTo(to)
        self.assertEquals(to, self.notifier.to)

        to = "ashelton@nrao.edu"
        self.notifier.SetTo(to)
        self.assertEquals([to], self.notifier.to)

    def test_SetSubject(self):
        self.notifier.SetSubject("stuff")
        self.assertEquals("stuff", self.notifier.subject)

    def test_SetDate(self):
        self.notifier.SetDate("stuff")
        self.assertEquals("stuff", self.notifier.date)

    def test_SetMessage(self):
        self.notifier.SetMessage("stuff")
        self.assertEquals("stuff", self.notifier.msg)

    def test_SetText(self):
        self.notifier.SetText("stuff")
        self.assertEquals("stuff", self.notifier.text)

    def test_GetFailures(self):
        self.assertEquals({}, self.notifier.GetFailures())

if __name__ == "__main__":
    unittest.main()
