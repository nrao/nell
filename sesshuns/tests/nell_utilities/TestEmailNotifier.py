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

from utilities.notifiers.emailNotifier import emailNotifier
from test_utils                        import NellTestCase
from datetime                          import datetime
from nell.utilities                    import TimeAgent

class TestEmailNotifier(NellTestCase):

    def setUp(self):
        super(TestEmailNotifier, self).setUp()
        self.notifier = emailNotifier()

    def tearDown(self):
        super(TestEmailNotifier, self).tearDown()
        self.notifier = None

    def test_SetSmtp(self):
        self.notifier.SetSmtp("stuff")
        self.assertEquals("stuff", self.notifier.smtp)

    def test_GetFailures(self):
        self.assertEquals({}, self.notifier.GetFailures())

