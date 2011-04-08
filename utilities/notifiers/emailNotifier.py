######################################################################
#
#  emailNotifier.py -- sends out email objects using SMTP.
#
#  Copyright (C) 2008 Associated Universities, Inc. Washington DC, USA.
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
#  $Id:$
#
######################################################################

import smtplib
from datetime import datetime

class emailNotifier:

    def __init__(self, smtp = None):

        self.SetSmtp(smtp)
        self.failed = {}

        if self.smtp != None:
            self.server = smtplib.SMTP(self.smtp)

    def SetSmtp(self, smtp):
        self.smtp = smtp

    def InitServer(self, smtp = None):
        if smtp != None:
            self.SetSmtp(smtp)
        if self.smtp == None:
            raise 'must set smtp before initing server'
        else:
            self.server = smtplib.SMTP(self.smtp)

    def GetFailures(self):
        return self.failed

    def Send(self, email):

        # This loop is necessary due to a bug in smtplib.  It only
        # emails the first person in the "to" list.  So, we need to
        # send an email for each person in the "to" list.
        recp = email.GetRecipientList()
        email.SetDate(datetime.today())
        
        if recp is not None:
            for address in recp:
                print "sending"
                self.failed = self.server.sendmail(email.GetSender(), address, email.GetText())

            if len(self.failed) > 0:
                raise 'failure in notification:', self.failed
            
    def TestSend(self, email):
        recp = email.GetRecipientList()
        email.SetDate(datetime.today())

        if recp is not None:
            for address in recp:
                email.PrintMessage()

    def QuitServer(self):
        "destroys connection to smtp server; call on cleanup"
        self.server.quit()
