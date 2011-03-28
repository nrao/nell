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

from Notifier      import Notifier
from Email         import Email
from PeriodChanges import PeriodChanges
from datetime      import datetime, timedelta
from sets          import Set

from utilities import TimeAgent

class SchedulingNotifier(Notifier):

    """
    This class is responsible for both setting up the scheduling emails,
    and sending them.
    """

    def __init__(self
               , periods    = []
               , futurePeriods = []
               , skipEmails = []
               , test       = False
               , log        = False
                ):
        Notifier.__init__(self, skipEmails, test, log)

        self.periodChanges = PeriodChanges(test = test)

        self.sender = "helpdesk-dss@gb.nrao.edu"
        self.setPeriods(periods, futurePeriods)


    def setPeriods(self, periods, futurePeriods):
        "For the given periods, what should the emails looke like?"

        periods.sort(lambda x, y: cmp(x.start, y.start))
        self.examinePeriods(periods, futurePeriods)

        if self.periods != []:
            self.startdate = self.periods[0].start
            self.enddate   = self.periods[-1].end()
        else:
            self.startdate = datetime.utcnow()
            self.enddate   = self.startdate + timedelta(hours = 48)

        self.emailProjectMap = self.createAddresses(self.periods)
        self.registerTemplate("observer", Email(self.sender,
                                                self.createObservingAddresses(),
                                                self.createObservingSubject(),
                                                self.createObservingBody()))
        self.registerTemplate("staff", Email(self.sender,
                                             self.createStaffAddresses(),
                                             self.createStaffSubject(),
                                             self.createStaffBody()))     
        self.registerTemplate("changed", Email(self.sender,
                                               self.createChangedAddresses(),
                                               self.createChangedSubject(),
                                               self.createChangedBody()))

    def examinePeriods(self, periods, futurePeriods):
        """
        This class must: 
           * notify observers of imminent observations
           * remind observers of things that have changed
           * notify observers of rejected Elective Periods
        Here we filter out the many purposes from our generic list 
        of periods.
        """

        self.periods = periods

        # the list of periods for scheduling (upcoming observations) includes
        # everything *but* the deleted periods.
        self.observingPeriods = \
            sorted([p for p in periods if not p.isDeleted()])

        self.changes = {} 
        # maintain this list of periods because of other lists like
        # observingPeriods, etc.
        self.changedPeriods = []
        for p in futurePeriods:
            diffs = self.periodChanges.getChangesForNotification(p)
            if len(diffs) > 0:
                self.changes[p] = diffs
                self.changedPeriods.append(p)

        # deleted periods must also be tracked separately, because those
        # observers will get an email with a different subject
        self.deletedPeriods = sorted([p for p in periods if p.isDeleted() and \
                                                   (not p.session.isWindowed() and not p.session.isElective())])

        # deleted electives get special consideration
        self.deletedElectivePeriods = sorted([p for p in periods if p.isDeleted() and p.session.isElective()])

    def notify(self):
        "send out all the different emails"

        # notify the obs; subject = "Your GBT Project has been
        # scheduled..."  Because each observer will get a custom
        # 'subject' line with the pcode appended, each must get a
        # separate email.

        for i in self.getAddresses("observer"):
            try:
                pcodes = " - ".join(self.emailProjectMap[i])
            except KeyError: # You WILL get a key error if scheduler
                             # changes observer email addresses
                pcodes = None

            email = self.cloneTemplate("observer")

            if pcodes:
                subject = "%s (%s)" % (email.GetSubject(), pcodes)
            else:
                subject = email.GetSubject()

            email.SetRecipients(i)
            email.SetSubject(subject)
            self.post(email)

        # now let the people who aren't observing know, but who
        # might have been in scheduled in the past

        if len(self.getAddresses("changed")) != 0:
            email = self.cloneTemplate("changed")
            self.post(email)

        # now let the staff know - "GBT schedule for ..."

        if len(self.getAddresses("staff")) != 0:
            email = self.cloneTemplate("staff")
            self.post(email)

        Notifier.notify(self) # send all the queued messages out!
        self.flushQueue()     # just in case.  If queue is empty, does nothing.

    def utc2est(self, dt, frmt):
        return TimeAgent.utc2est(dt).strftime(frmt)

    def utc2estDate(self, dt):
        return self.utc2est(dt, '%b %d')

    def utc2estDT(self, dt):
        return self.utc2est(dt,'%b %d %H:%M')

    # *** Email Address Methods

    def createStaffAddresses(self):
        staff = ["gbtops@gb.nrao.edu", "gbtinfo@gb.nrao.edu", "gbtime@gb.nrao.edu"]
        # any electives that arent getting observed?
        deletedElecs = self.createAddresses(self.deletedElectivePeriods)
        staff.extend(deletedElecs)
        self.logMessage("Staff To: %s\n" % staff)
        return staff

    def createObservingAddresses(self):
        "get addresses of only those who are observing"
        return self.emailProjectMap.keys()

    def createChangedAddresses(self):
        return self.createAddresses(self.changedPeriods).keys()

    def createAddresses(self, periods):
        """
        Creates and returns a dictionary containing the addresses
        associated with the periods as keys, and maintaining the
        association of the projects to those addresses.  Projects
        associated with the addresses are stored in a set which is
        accessed using the address as a key.
        """
        eaddr = {}

        for p in periods:

            obs = [o.user for o in p.session.project.get_observers()]
            pc = p.session.project.principal_contact()

            if pc is not None and pc not in obs:
                obs.append(p.session.project.principal_contact())

            for o in obs:
                for e in o.getEmails():
                    if eaddr.has_key(e):
                        eaddr[e].add(p.session.project.pcode)
                    else:
                        eaddr[e] = set([p.session.project.pcode])

        self.logMessage("To: %s\n" % eaddr.keys())
        return eaddr


    # Email Subject Methods

    def createStaffSubject(self):
        subject = "GBT schedule for %s-%s" % \
                  (self.utc2estDate(self.startdate),
                   self.utc2estDate(self.enddate))
        self.logMessage("Staff Subject: %s\n" % subject)
        return subject



    def createObservingSubject(self):
        subject = "Your GBT project has been scheduled (%s-%s)" % \
                  (self.utc2estDate(self.startdate),
                   self.utc2estDate(self.enddate))
        self.logMessage("Observing Subject: %s\n" % subject)
        return subject

    def createChangedSubject(self):
        subject = "Reminder: GBT Schedule has changed."
        self.logMessage("Changed Subject: %s\n" % subject)
        return subject

    # *** Email Body Methods

    def createChangedBody(self):

        header = "The following periods have changed: "
        changes = self.getChangedTable() 
        footer = self.getStaffBodyFooter()

        body = \
"""
%s
%s
%s
%s
""" \
           % (header
           , changes
           , self.getSessionTable(self.observingPeriods)
           , footer)

        return body

    def getChangedTable(self):
        "How to display all the changes made to the schedule?"
        return "\n".join([self.getChangeLine(p, diffs) for p, diffs in self.changes.items()])

    def getChangeLine(self, p, diffs):
        "Given all the details about what's happened, what to say?"

        # Easy, either say this period has 'changed', or been deleted.
        # So, this means seeing if the last state was deleted.
        states = [d.value2 for d in diffs if d.field == 'state']
        deleted = True if len(states) > 0 and states[-1] == 3 else False
        start = "A period for project %s" % p.session.project.pcode
        if deleted:
            line = start + " has been deleted.\n"
        else:
            line = start + " has been changed.\n"
        return line    
           
    def getStaffBodyHeader(self):
        header = \
"""
Dear Colleagues,

The schedule for the period %s ET through %s ET is fixed and available.

""" \
        % (self.utc2estDT(self.startdate),
           self.utc2estDT(self.enddate))
        return header

    def getStaffBodyFooter(self):
        footer = \
"""
Please log into https://dss.gb.nrao.edu to view your observation
related information.

Any requests or problems with the schedule should be directed
to %s.

Happy Observing!
""" \
        % self.sender
        return footer

    def getStaffBodyNotes(self):
        notes = ""
        # any rejected electives to notify on?
        for p in self.deletedElectivePeriods:
            l = "Note: Project %s will not be scheduled on %s (ET)\n" % \
                (p.session.project.pcode
               , self.utc2estDT(p.start))
            notes += l   
        # any changes in the schedule?
        notes += self.getChangedTable()
        return notes

    def createStaffBody(self):
        """
        This email body will be based off the generic email, but may
        have added lines.
        """
        body = \
"""
%s
%s
%s
%s
""" \
        % (self.getStaffBodyHeader()
         , self.getStaffBodyNotes()
         , self.getSessionTable(self.observingPeriods)
         , self.getStaffBodyFooter()
          )
        return body

    def createObservingBody(self):
        """
        For now, this is identical to the staff body, but without
        the notes.
        """
        body = \
"""
%s
%s
%s
""" \
        % (self.getStaffBodyHeader()
         , self.getSessionTable(self.observingPeriods)
         , self.getStaffBodyFooter()
          )
        return body

    def getSessionTable(self, periods):
        table  = "Start (ET)   |      UT      |  LST  |  (hr) |    PI     | Rx        | Session\n"
        table += "------------------------------------------------------------------------------------\n"
        for p in periods:
            if p.session.project.pcode == "Maintenance":
                pi = ""
            else:
                pi = p.session.project.principal_investigator().last_name[:9] if p.session.project.principal_investigator() else "Unknown"

            table += "%s | %s | %s | %5s | %-9s | %-9s | %s\n" % (
                self.utc2estDT(p.start)
              , p.start.strftime('%b %d %H:%M')
              , TimeAgent.dt2tlst(p.start).strftime('%H:%M')
              , "%2.2f" % p.duration
              , pi
              , p.session.receiver_list_simple()[:9]
              , p.session.name
            )
        return table

