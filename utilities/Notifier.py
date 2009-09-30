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

from datetime      import datetime
from emailNotifier import emailNotifier

class Notifier(object):

    """
    This abstract class is responsible for sending out a batch of emails to
    notify DSS investigators concerning issues with their project(s).  
    Note: Children of this class should implement the stub method, 
    sendNotifications.
    """
    
    def __init__(self, skipEmails = [], test = False, log = False):
        self.skipEmails  = skipEmails
        self.test        = test

        self.to          = []
        self.subject     = ""
        self.body        = ""

        self.log         = log
        self.logfile     = None
        self.logfilename = None

    def startLogging(self):    
        if not self.log:
            return

        self.logfilename = \
            "notification_%s" % datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        self.logFile = open(self.logfilename, 'w')
        self.logFile.write('Notification sent on: %s\n\n' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.logFile.flush()

    def logMessage(self, message):
        if self.log:
            self.logFile.write(message)

    def stopLogging(self):
        if self.log:
            self.logFile.close()

    def setAddresses(self, addresses):
        self.to = [a for a in addresses if a not in self.skipEmails]

    def getAddresses(self):
        return self.to

    def setSubject(self, subject):
        self.subject = subject

    def getSubject(self):
        return self.subject

    def setBody(self, body):
        self.body = body

    def getBody(self):
        return self.body

    def notify(self):
        "Send out the emails."
        if self.test:
            return 

        self.startLogging()

        try:
            emailer = emailNotifier(smtp = "smtp.gb.nrao.edu"
                                  , frm  = "helpdesk-dss@gb.nrao.edu")
            emailer.SetTo(self.getAddresses())
            emailer.SetSubject(self.getSubject())
            emailer.SetMessage(self.getBody())
            emailer.Notify()
        except:
            print "Error: Could not send mail!"
            self.logMessage("Error: Could not send mail!\n")

        self.stopLogging()
