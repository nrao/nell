from Notifier             import Notifier
from datetime             import datetime, timedelta
from sets                 import Set
from Email                import Email

class ElecAlertEmail(Email):
    """
    These children of this class are just easy ways to organize
    the different text that we want in the emails according to the
    level of the elective alert.
    """
    def __init__(self, sender, elective):

        Email.__init__(self, sender = sender, recipients = []
                     , bcc = "gbdyn@nrao.edu")
        self.createRecipients(elective)
        self.date = None

    def createRecipients(self, elective):
        "Determine emails from elective's project's observers"
        obs = [o.user for o in elective.session.project.get_observers()]
        pc = elective.session.project.principal_contact()
        if pc is not None and pc not in obs:
            obs.append(elective.session.project.principal_contact())
        emails = []
        for o in obs:
            for e in o.getEmails():
                if e not in emails:
                    emails.append(e)
        if len(emails) > 0:            
            self.SetRecipients(emails)

    def createMessage(self, elective, subject):
        self.SetSubject(subject)
        start, end = elective.getRange()
        body = """
Dear Observers,

%s's elective session, whose candidate periods runs from
%s through %s, has one or more periods blacked out.
As a result it is very possible this project will not be scheduled.
At this point three options are available:

     (1) Change one or more blackout dates affecting the project
         so that this situation is remedied.
     (2) Leave all blackout dates as they are, and accept that your
         project may not be scheduled.  In this case the elective
         *will not be rescheduled*.
     (3) Contact the GBT scheduling team (helpdesk-dss@nrao.edu) to
         determine if the elective parameters for this project should
         be changed.    

Regards,

The GBT scheduling team 
        """ % (elective.session.project.pcode
             , start.date()
             , end.date()
              )
        self.SetBody(body)

class ElecAlertNotifier(Notifier):

    """
    This class is responsible for sending email notifications
    regarding issues with electives.
    Because each subject line is specific to the project, and each
    email body is dependent on the actual blackout involved, we 
    need a new object of this class for each elective alert.
    This class passes on the responsibilty of the formatting of each
    email to special email classes.
    """

    def __init__(self, elective, test = False, log = False):
        Notifier.__init__(self, [], test, log)

        self.sender = "helpdesk-dss@gb.nrao.edu"
        self.type   = type
        self.setElective(elective)
 
    def setElective(self, elective):
        """
        From the elective, and stage of the alert, we can determine
        who gets what kind of message.
        """
        
        self.elective = elective

        self.email = ElecAlertEmail(self.sender, elective) 
        subject = "Blackout dates will prevent scheduling %s" % elective.session.project.pcode
        self.email.createMessage(elective, subject)

    def notify(self):
        "send out all the different emails"

        if self.email is None:
            return

        self.post(self.email)

        Notifier.notify(self) # send all the queued messages out!
        self.flushQueue()     # just in case.  If queue is empty, does nothing.
        
