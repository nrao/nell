# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from Notifier             import Notifier
from datetime             import datetime, timedelta
from sets                 import Set
from Email                import Email

class FixedAlertEmail(Email):
    """
    These children of this class are just easy ways to organize
    the different text that we want in the emails according to the
    level of the alert.
    """
    def __init__(self, sender, sess):

        Email.__init__(self, sender = sender, recipients = []
                     , bcc = "gbdyn@nrao.edu")
        self.createRecipients(sess)
        self.date = None

    def createRecipients(self, sess):
        "Determine emails from session's project's observers"
        obs = [o.user for o in sess.project.get_observers()]
        pc = sess.project.principal_contact()
        if pc is not None and pc not in obs:
            obs.append(sess.project.principal_contact())
        emails = []
        for o in obs:
            for e in o.getEmails():
                if e not in emails:
                    emails.append(e)
        if len(emails) > 0:            
            self.SetRecipients(emails)

    def createMessage(self, sess, subject):
        self.SetSubject(subject)
        start, end = sess.getPeriodRange()
        body = """
Dear Observers,

%s's fixed session, whose periods runs from %s
through %s, has one or more periods blacked out.
As a result these periods will not be scheduled.
At this point three options are available:

     (1) Change one or more blackout dates affecting the project
         so that this situation is remedied.
     (2) Leave all blackout dates as they are, and accept that your
         project will not be scheduled.  In this case the period
         *will not be rescheduled*.
     (3) Contact the GBT scheduling team (helpdesk-dss@nrao.edu) to
         determine if the parameters for this project should
         be changed.    

Regards,

The GBT scheduling team 
        """ % (sess.project.pcode
             , start.date()
             , end.date()
              )
        self.SetBody(body)

class FixedAlertNotifier(Notifier):

    """
    This class is responsible for sending email notifications
    regarding issues with fixed sessions.
    Because each subject line is specific to the project, and each
    email body is dependent on the actual blackout involved, we 
    need a new object of this class for each session alert.
    This class passes on the responsibilty of the formatting of each
    email to special email classes.
    """

    def __init__(self, session, test = False, log = False):
        Notifier.__init__(self, [], test, log)

        self.sender = "helpdesk-dss@gb.nrao.edu"
        self.type   = type
        self.setFixed(session)
 
    def setFixed(self, session):
        """
        From the session, and stage of the alert, we can determine
        who gets what kind of message.
        """
        
        self.session = session

        self.email = FixedAlertEmail(self.sender, session) 
        subject = "Blackout dates will prevent scheduling %s" % session.project.pcode
        self.email.createMessage(session, subject)

    def notify(self):
        "send out all the different emails"

        if self.email is None:
            return

        self.post(self.email)

        Notifier.notify(self) # send all the queued messages out!
        self.flushQueue()     # just in case.  If queue is empty, does nothing.
        
