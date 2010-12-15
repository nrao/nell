######################################################################
#
#
#
#  Copyright (C) 2009 Associated Universities, Inc. Washington DC, USA.
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

from Notifier import Notifier
from datetime import datetime, timedelta
from sets     import Set
from Email    import Email


import TimeAgent

# TBF: these Email children are here because no one else uses them.
# I tried to make them inner to WinAlerNotifier but it wasn't working

class WinAlertEmail(Email):
    """
    These children of this class are just easy ways to organize
    the different text that we want in the emails according to the
    level of the window alert.
    """
    def __init__(self, sender, window):

        Email.__init__(self, sender = sender, recipients = [])
        
        self.createRecepients(window)
        self.createSubject(window)
        self.createBody(window)

        self.date = None

    def createRecepients(self, window):
        "Determine emails from window's project's observers"
        obs = [o.user for o in window.session.project.get_observers()]
        pc = window.session.project.principal_contact()
        if pc is not None and pc not in obs:
            obs.append(window.session.project.principal_contact())
        emails = []
        for o in obs:
            for e in o.getStaticContactInfo()['emails']:
                if e not in emails:
                    emails.append(e)
        if len(emails) > 0:            
            self.SetRecipients(emails)

class WinAlertEmailLevelOne(WinAlertEmail):

    def createSubject(self, window):
        subj = "Blackout dates may prevent scheduling %s" % \
           window.session.project.pcode
        self.SetSubject(subj)    

    def createBody(self, window):
        body = """
Dear Observers,  

There is no observer available for >10%s of the  possible time for scheduling 
%s's windowed session which runs from %s through 
%s. As a result it is  very possible this project will not be 
scheduled during the windowed session. At this point three options are available:
     (1) Change the blackout dates for one or more observers of the project
         so that this situation is remedied
     (2) Leave all blackout dates as they are, and accept that your project
         may not be scheduled.  In this case the window *will not be rescheduled*.
     (3) Contact the GBT scheduling team (helpdesk-dss@nrao.edu) to determine
         if the window parameters for this project should be changed.    

Regards,
The GBT scheduling team 
        """ % ("%" # TBF WTF OMG!!!
             , window.session.project.pcode
             , window.start_date()
             , window.last_date())
        self.SetBody(body)

class WinAlertEmailLevelTwo(WinAlertEmail):

    def createSubject(self, window):
        subj = "Blackout dates will prevent scheduling %s" % \
           window.session.project.pcode
        self.SetSubject(subj)    

    def createBody(self, window):
        body = """
Dear Observers,  

There is no observer available for >50%s of the  possible time for scheduling 
%s's windowed session which runs  from %s through 
%s. As a result it is  nearly certain that this project will not 
be scheduled during the  windowed session.  

At this point three options are available:     

       (1) Change the blackout dates for one or more observers 
           of the project so that this situation is remedied     
       (2) Leave all blackout dates as they are, and accept that your
           project may not be scheduled.  In this case the window *will
           not be rescheduled*.
       (3) Contact the GBT scheduling team (helpdesk-dss@nrao.edu) to
           determine if the window parameters for this project should be
           changed.   

Regards, 
The GBT scheduling team 
        """ % ("%" # TBF WTF OMG !!!
             , window.session.project.pcode
             , window.start_date()
             , window.last_date())
        self.SetBody(body)

class WinAlertNotifier(Notifier):

    """
    This class is responsible for sending email notifications
    regarding issues with windows.
    Because each subject line is specific to the project, and each
    email body is dependent on the actual blackout involved, we 
    need a new object of this class for each window alert.
    This class passes on the responsibilty of the formatting of each
    email to special email classes.
    """

    def __init__(self, window, level, stage, test = False, log = False):
        Notifier.__init__(self, [], test, log)

        self.sender = "helpdesk-dss@gb.nrao.edu"
        self.level = level
        self.stage = stage
        self.setWindow(window)
 
    def setWindow(self, window):
        """
        From the window, and level of the alert, we can determine
        who gets what kind of message.
        """
        
        self.window = window

        self.email = WinAlertEmailLevelOne(self.sender, window) if self.level == 1 else \
            WinAlertEmailLevelTwo(self.sender, window)

    def notify(self):
        "send out all the different emails"

        if self.email is None:
            return

        self.post(self.email)

        Notifier.notify(self) # send all the queued messages out!
        self.flushQueue()     # just in case.  If queue is empty, does nothing.
        
