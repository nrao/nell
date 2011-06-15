from Notifier import Notifier
from datetime import datetime, timedelta
from sets     import Set
from Email    import Email

from utilities import TimeAgent

class SessionAlertEmail(Email):

    def __init__(self, sender, unknown):

        Email.__init__(self, sender = sender, recipients = [])
        self.createRecipients(unknown.session)
        self.date = None

    def createRecipients(self, session):
        "Determine emails from window's project's observers"
        obs = [o.user for o in session.project.get_observers()]
        pc = session.project.principal_contact()
        if pc is not None and pc not in obs:
            obs.append(session.project.principal_contact())
        emails = []
        for o in obs:
            for e in o.getEmails():
                if e not in emails:
                    emails.append(e)
        if len(emails) > 0:            
            self.SetRecipients(emails)

    @staticmethod
    def getRange(unknown):
        if unknown.session.session_type.type == "windowed":
            return "from %s through %s" % (unknown.start_date(), unknown.last_date())
        elif unknown.session.session_type.type == "elective":
            return "on %s" % ", ".join([str(p.start) for p in unknown.periods.all().order_by("start")])
        elif unknown.session.session_type.type == "fixed":
            return "on %s" % unknown.start

    def createDisabledObservers(self, unknown):
        "Create email to be sent to observers with disabled sessions."
        self.SetSubject(
           "Warning, GBT %s session %s is not enabled will likely not be scheduled" \
               % (unknown.session.session_type.type, unknown.session.name))

        self.SetBody("""
Dear Observers,  

GBT %s session %s which runs %s is not yet enabled to be scheduled.   As a result it is nearly certain that this session will not be observed.  If you do not enable this session, the window *will not be rescheduled*.

If you have any questions, please contact the GBT scheduling team (helpdesk-dss@nrao.edu).  

Thanks very much,  

The GBT scheduling team 
        """ % (unknown.session.session_type.type
             , unknown.session.name
             , SessionAlertEmail.getRange(unknown)
             )
        )

    def createDisabledDssTeam(self, unknown, flag):
        "Create email to be sent to the DSS team about inactive sessions."
        self.SetSubject(
           "Warning - un%s %s session(s) about to begin" % (flag, unknown.session.session_type.type))
        self.SetBody(
           "%s session %s runs %s and is un%s." % (
                                       unknown.session.session_type.type
                                     , unknown.session.name
                                     , SessionAlertEmail.getRange(unknown)
                                     , flag
                                                  ))

class SessionAlertNotifier(Notifier):

    """
    This class is responsible for sending email notifications
    regarding issues with windows.
    Because each subject line is specific to the project, and each
    email body is dependent on the actual blackout involved, we 
    need a new object of this class for each window alert.
    This class passes on the responsibilty of the formatting of each
    email to special email classes.
    """

    def __init__(self, unknown, test = False, log = False, type = "dss_team", flag = "enabled"):
        Notifier.__init__(self, [], test, log)

        self.sender = "helpdesk-dss@gb.nrao.edu"
        self.type   = type
        self.setUnknown(unknown, flag)
 
    def setUnknown(self, unknown, flag):
        
        self.unknown = unknown

        self.email = SessionAlertEmail(self.sender, unknown) 
        if self.type == "observers":
            self.email.createDisabledObservers(unknown)
        elif self.type == "dss_team":
            self.sender = "dss@gb.nrao.edu"
            self.email.createDisabledDssTeam(unknown, flag)
            self.email.SetRecipients(['gbdyn@nrao.edu'])

    def notify(self):
        "send out all the different emails"

        if self.email is None:
            return

        self.post(self.email)

        Notifier.notify(self) # send all the queued messages out!
        self.flushQueue()     # just in case.  If queue is empty, does nothing.
        
