######################################################################
#
#  email.py: defines an email object that can be passed around and
#  sent out via the emailNotifier.
#
#  Copyright (C) 2010 Associated Universities, Inc. Washington DC, USA.
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

from datetime import datetime
from utilities import TimeAgent

class Email:

    def __init__(self, sender = None, recipients = None, subject = None, body = None, date = None, bcc = None):

        self.SetSender(sender)
        self.SetRecipients(recipients)
        self.SetSubject(subject)
        self.SetBody(body)
        self.SetBcc(bcc)
        self.SetDate(date)

    def SetSender(self, sender):
        """
        SetSender() is simple.  Only one sender.  
        """
        # Note: no error checking (valid email)
        self.sender = sender

    def GetSender(self):
        return self.sender
    

    def SetRecipients(self, recipients):
        """
        SetRecipient(self, recipients).  The recipients can be one or
        more email addresses, either in a comma or semicolon separated
        list or in a Python list.  It is converted internally to a
        list of strings (if it isn't already), each being an email
        address.  If there are no addresses, the internal list is
        empty.
        """

        if recipients is None:
            self.recipients = []
        elif type(recipients) == str:
            if recipients == "":
                self.recipients = []
            else:
                separator = None
                recipients = recipients.replace(" ", "")

                if "," in recipients:
                    separator = ","
                elif ";" in recipients:
                    separator = ";"

                self.recipients = recipients.split(separator)
        else:
            if len(recipients) == 1 and recipients[0] == "":
                self.recipients = []
            else:
                self.recipients = recipients

    def GetRecipientString(self):
        "Returns the list of recipients as a comma-separated string."

        return ",".join(self.recipients)
    

    def GetRecipientList(self):
        "Returns the list of recipients as a list."
        return self.recipients
    
    def SetSubject(self, subj):
        "The subject line of the email message"
        self.subject = subj

    def GetSubject(self):
        return self.subject

    def SetDate(self, date):
        if date:
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

            self.date = "%s, %s %s %s -0%d00" % (weekdays[date.strftime("%w")],
                                                 date.strftime("%d"),
                                                 months[str(int(date.strftime("%m")))],
                                                 date.strftime("%Y %H:%M:%S"),
                                                 TimeAgent.utcoffset())
        else:
            self.date = None


    def GetDate(self):
        return self.date


    def SetBody(self, body):
        self.body = body

    def GetBody(self):
        return self.body

    def SetBcc(self, bcc):
        self.bcc = bcc

    def GetBcc(self):
        return self.bcc

    def GetText(self):
        """Returns the entire text of the email, including the To:,
        From:, Date: etc. fields"""

        bccStr = "" if self.bcc is None else "Bcc: %s\r\n" % self.bcc
        text =  'From: %s\r\nTo: %s\r\n%sDate: %s\r\nSubject: %s\r\n\r\n%s\r\n' \
               % (self.sender, self.GetRecipientString(), bccStr, self.date
                , self.subject, self.body)

        return text

    def PrintMessage(self):
        print self.GetText()
