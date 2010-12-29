######################################################################
#
#  rescal_notifier.py - Handles email messaging from the resource
#  calendar.
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

from nell.utilities.Notifier import Notifier
from datetime                import datetime, timedelta
from sets                    import Set
from nell.utilities.Email    import Email as EmailMessage
from nell.utilities          import TimeAgent

class RescalNotifier(Notifier):


    def __init__(self, skipEmails = [], test = False, log = False):
        Notifier.__init__(self, skipEmails, test, log)

        activities = {"new"      : ("A new activity was added for the maintenance period"
                                    " on %s\nClick to view: %s") ,
                      "modified" : ("A previously approved activity has been modified for"
                                    " the maintenance period on %s\nClick to view: %s"),
                      "deleted"  : ("An activity has been deleted from the maintenance"
                                    "period on %s\nClick to view: %s"),
                      "approved" : ("Your activity for the maintenance period for %s"
                                    " has been approved.\nClick to view: %s")}

        sender = "helpdesk-dss@gb.nrao.edu"
        subject = "GBT Resource Calendar Activity"

        for i in activities:
            em_templ = EmailMessage(sender, "", subject, activities[i])
            self.registerTemplate(i, em_templ)

    ######################################################################
    # This general function can be used to notify recipients of
    # changes in the resource calendar:
    #
    # who: recipient (eg cat@hat.edu)
    # what: "new", "modified", "deleted", "moved", "approved" (?)
    #       The email sent will depend on this key.
    #
    # xxx.notify(supervisor, "new", url)
    # xxx.notify(user, "approved", url)
    #  etc.
    ######################################################################

    def notify(self, who, what, date, url, changes = None):
        recipients = []
        
        try:
            for i in who:
                recipients += self.__get_reciptients(i)
        except TypeError: # 'who' is not a list, but a single user
            recipients += self.__get_recipients(who)
                                 
        email = self.cloneTemplate(what)
        email.SetRecipients(recipients)
        body = email.GetBody();

        if changes:
            body += "\n\nList of changes:\n\n"
            for i in changes:
                body += i + (":\t" if len(i) < 8 else ":") + changes[i] + "\n"

        email.SetBody(body % (date, url))
        self.post(email)
        Notifier.notify(self)

    def __get_reciptients(self, user):
        eml = user.email_set.all()
        recipient = []
        # If no contacts listed, assume nrao.edu email address
        # with the given username:
        if len(eml) == 0:
            recipient.append(user.auth_user.username + "@nrao.edu")
        else:
            for i in eml:
                recipient.append(i.email)

        return recipient
