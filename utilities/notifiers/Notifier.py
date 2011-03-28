######################################################################
#
#  Notifier sends out a batch of emails to notify investigators and
#  staff concerning GBT projects.
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

from datetime      import datetime
from emailNotifier import emailNotifier
from Email         import Email
from Queue         import Queue, Empty
from copy          import deepcopy


class Notifier(object):

    """
    This abstract class is responsible for sending out a batch of emails to
    notify DSS investigators concerning issues with their project(s).
    Note: Children of this class should implement the stub method,
    sendNotifications.
    """

    class Prototype:
        """
        this class is used to keep prototype emails that the class
        user may wish to register, then clone for their own use.
        (copied from activestate.com,
        http://code.activestate.com/recipes/86651-prototype-pattern/)
        """
        def __init__(self):
            self._objs = {}

        def registerObject(self, name, obj):
            """
            register an object.
            """
            self._objs[name] = obj

        def unregisterObject(self, name):
            """unregister an object"""
            del self._objs[name]

        def clone(self, name, **attr):
            """clone a registered object and add/replace attr"""
            obj = deepcopy(self._objs[name])
            obj.__dict__.update(attr)
            return obj

        def getObject(self, name):
            """return a reference to the actual stored object"""
            return self._objs[name]


    def __init__(self, skipEmails = [], test = False, log = False):
        self.skipEmails  = skipEmails
        self.test        = test

        self.log         = log
        self.logfile     = None
        self.logfilename = None
        self.queue       = Queue(0)
        self.email_templates = Notifier.Prototype()


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

    def setAddresses(self, key, addresses):
        to = [a for a in addresses if a not in self.skipEmails]
        self.email_templates.getObject(key).SetRecipients(to)

    def getAddresses(self, key):
        return self.email_templates.getObject(key).GetRecipientList()

    def setSubject(self, key, subject):
        self.email_templates.getObject(key).SetSubject(subject)

    def getSubject(self, key):
        return self.email_templates.getObject(key).GetSubject()

    def setBody(self, key, body):
        self.email_templates.getObject(key).SetBody(body)

    def getBody(self, key):
        return self.email_templates.getObject(key).GetBody()

    def setSender(self, key, sender):
        self.email_templates.getObject(key).SetSender(sender)

    def getSender(self, key):
        return self.email_templates.getObject(key).GetSender()

    def registerTemplate(self, key, email):
        self.email_templates.registerObject(key, email)

    def cloneTemplate(self, key):
        return self.email_templates.clone(key)

    def unregisterTemplate(self, key):
        self.email_templates.unregisterObject(key)

    def post(self, email):
        self.queue.put(email)

    def flushQueue(self):
        try:
            while not self.queue.empty():
                email = self.queue.get_nowait()
        except Empty:
            pass

    def notify(self):
        "Send out the emails."

        self.startLogging()

        try:
            emailer = emailNotifier(smtp = "smtp.gb.nrao.edu")

            while not self.queue.empty():
                email = self.queue.get_nowait()
##                 emailer.TestSend(email)
                emailer.Send(email)
        except Empty:
            pass
        except:
            print "Error: Could not send mail!"
            self.logMessage("Error: Could not send mail!\n")

        self.stopLogging()
