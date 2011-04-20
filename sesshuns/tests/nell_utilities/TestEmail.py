######################################################################
#
#  TestEmail.py -- Tests the module 'Email.py', which encapsulates the
#  behavior of an email message.
#
#  Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

from utilities.notifiers.Email import Email
from test_utils                import NellTestCase
from datetime                  import datetime
from nell.utilities            import TimeAgent

class TestEmail(NellTestCase):

    def setUp(self):
        super(TestEmail, self).setUp()

        weekdays = {"0" : "Sun",
                    "1" : "Mon",
                    "2" : "Tue",
                    "3" : "Wed",
                    "4" : "Thu",
                    "5" : "Fri",
                    "6" : "Sat"}

        months = {"1"  : "Jan",
                  "2"  : "Feb",
                  "3"  : "Mar",
                  "4"  : "Apr",
                  "5"  : "May",
                  "6"  : "Jun",
                  "7"  : "Jul",
                  "8"  : "Aug",
                  "9"  : "Sep",
                  "10" : "Oct",
                  "11" : "Nov",
                  "12" : "Dec"}
        
        self.sender = "frog@pond"
        self.recipients_list = ["toad@toadstool", "newt@leaflitter"]
        self.recipients = "toad@toadstool,newt@leaflitter"
        self.subject = "Flies are yummy"
        self.body = "Delicious!"
        self.date = datetime.now()
        self.datestring = "%s, %s %s %s -0%d00" % (weekdays[self.date.strftime("%w")],
                                                   self.date.strftime("%d"),
                                                   months[str(int(self.date.strftime("%m")))],
                                                   self.date.strftime("%Y %H:%M:%S"),
                                                   TimeAgent.utcoffset())

        self.text =  'From: %s\r\nTo: %s\r\nDate: %s\r\nSubject: %s\r\n\r\n%s\r\n' \
            % (self.sender, self.recipients, self.datestring, self.subject, self.body)

        self.e1 = Email()
        self.e2 = Email(sender = self.sender,
                        recipients = self.recipients,
                        subject = self.subject,
                        body = self.body,
                        date = self.date)

    def tearDown(self):
        super(TestEmail, self).tearDown()

    def test_prefilled_email(self):
        self.assertEqual(self.sender, self.e2.GetSender())
        self.assertEqual(self.recipients, self.e2.GetRecipientString())
        self.assertEqual(self.recipients_list, self.e2.GetRecipientList())
        # you can set recipients as a list too
        self.e2.SetRecipients(self.recipients_list)
        self.assertEqual(self.recipients, self.e2.GetRecipientString())
        self.assertEqual(self.recipients_list, self.e2.GetRecipientList())

        self.assertEqual(self.subject, self.e2.GetSubject())
        self.assertEqual(self.body, self.e2.GetBody())
        self.assertEqual(self.datestring, self.e2.GetDate())
        self.assertEqual(self.text, self.e2.GetText())
        

    def test_set_email(self):
        self.e1.SetSender(self.sender)
        self.e1.SetRecipients(self.recipients_list)
        self.e1.SetSubject(self.subject)
        self.e1.SetBody(self.body)
        self.e1.SetDate(self.date)
        self.assertEqual(self.sender, self.e1.GetSender())
        self.assertEqual(self.recipients, self.e1.GetRecipientString())
        self.assertEqual(self.recipients_list, self.e1.GetRecipientList())
        self.assertEqual(self.subject, self.e1.GetSubject())
        self.assertEqual(self.body, self.e1.GetBody())
        self.assertEqual(self.datestring, self.e1.GetDate())
        self.assertEqual(self.text, self.e1.GetText())
