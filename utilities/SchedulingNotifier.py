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

class SchedulingNotifier(Notifier):


    def __init__(self
               , periods    = []
               , skipEmails = []
               , test       = False
               , log        = False):
        Notifier.__init__(self, skipEmails, test, log)

        self.sender = "helpdesk-dss@gb.nrao.edu"
        self.setPeriods(periods)


    def setPeriods(self, periods):

        periods.sort(lambda x, y: cmp(x.start, y.start))
        self.examinePeriods(periods)

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
                                                self.createBody()))
        self.registerTemplate("deleted", Email(self.sender,
                                               self.createDeletedAddresses(),
                                               self.createDeletedSubject(),
                                               self.createDeletedBody()))
        self.registerTemplate("staff", Email(self.sender,
                                             self.createStaffAddresses(),
                                             self.createStaffSubject(),
                                             self.createBody()))     

    def examinePeriods(self, periods):
        """
        This class must notify observers of imminent observations, *and*
        remind observers of things that have changed.  Here we filter out
        the two purposes from our generic list of periods.
        """

        self.periods = periods

        # the list of periods for scheduling (upcoming observations) includes
        # everything *but* the deleted periods.
        self.observingPeriods = \
            sorted([p for p in periods if not p.isDeleted()])

        # the list of periods that we must list to remind obs. of changes:
        self.changedPeriods = sorted([p for p in periods if p.isDeleted() or \
                                   p.accounting.of_interest()])

        # deleted periods must also be tracked separately, because those
        # observers will get an email with a different subject
        self.deletedPeriods = sorted([p for p in periods if p.isDeleted()])

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

        if len(self.getAddresses("deleted")) != 0:
            email = self.cloneTemplate("deleted")
            self.post(email)

        # now let the staff know - "GBT schedule for ..."

        if len(self.getAddresses("staff")) != 0:
            email = self.cloneTemplate("staff")
            self.post(email)

        Notifier.notify(self) # send all the queued messages out!
        self.flushQueue()     # just in case.  If queue is empty, does nothing.

    def createStaffAddresses(self):
        staff = ["gbtops@gb.nrao.edu", "gbtlocal@gb.nrao.edu", "gbtime@gb.nrao.edu"]
        self.logMessage("Staff To: %s\n" % staff)
        return staff

    def createObservingAddresses(self):
        "get addresses of only those who are observing"
        return self.emailProjectMap.keys()

    def createDeletedAddresses(self):
        "get addresses of only those who had periods originally scheduled"
        return self.createAddresses(self.deletedPeriods).keys()

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
                for e in o.getStaticContactInfo()['emails']:
                    if eaddr.has_key(e):
                        eaddr[e].add(p.session.project.pcode)
                    else:
                        eaddr[e] = set([p.session.project.pcode])

        self.logMessage("To: %s\n" % eaddr.keys())
        return eaddr

    def createStaffSubject(self):
        subject = "GBT schedule for %s-%s" % \
                  (TimeAgent.utc2est(self.startdate).strftime('%b %d'),
                   TimeAgent.utc2est(self.enddate).strftime('%b %d'))
        self.logMessage("Staff Subject: %s\n" % subject)
        return subject

    def createDeletedSubject(self):
        subject = "Reminder: GBT Schedule has changed."
        self.logMessage("Deleted Subject: %s\n" % subject)
        return subject

    def createObservingSubject(self):
        subject = "Your GBT project has been scheduled (%s-%s)" % \
                  (TimeAgent.utc2est(self.startdate).strftime('%b %d'),
                   TimeAgent.utc2est(self.enddate).strftime('%b %d'))
        self.logMessage("Observing Subject: %s\n" % subject)
        return subject

    def createBody(self):
        body = \
"""
Dear Colleagues,

The schedule for the period %s ET through %s ET is fixed and available.

%s
%s
Please log into https://dss.gb.nrao.edu to view your observation
related information.

Any requests or problems with the schedule should be directed
to %s.

Happy Observing!
""" \
        % (TimeAgent.utc2est(self.startdate).strftime('%b %d %H:%M'),
           TimeAgent.utc2est(self.enddate).strftime('%b %d %H:%M'),
           self.getSessionTable(self.observingPeriods),
           self.getChanges(), self.sender)

        self.logMessage("Observing and Staff Body: %s\n" % body)
        return body

    def createDeletedBody(self):
        body = \
"""
Dear Colleagues,

This is a reminder that the following projects had been scheduled
between %s ET through %s ET, but have been removed from the schedule.

%s

Please log into https://dss.gb.nrao.edu to view your observation
related information.

Any requests or problems with the schedule should be directed
to helpdesk-dss@gb.nrao.edu.

Thank You.
""" \
        % (TimeAgent.utc2est(self.startdate).strftime('%b %d %H:%M'),
           TimeAgent.utc2est(self.enddate).strftime('%b %d %H:%M'),
           self.getSessionTable(self.deletedPeriods))

        self.logMessage("Body: %s\n" % body)
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
                TimeAgent.utc2est(p.start).strftime('%b %d %H:%M')
              , p.start.strftime('%b %d %H:%M')
              , TimeAgent.dt2tlst(p.start).strftime('%H:%M')
              , "%2.2f" % p.duration
              , pi
              , p.session.receiver_list_simple()[:9]
              , p.session.name
            )
        return table

    def getChanges(self):
        if len(self.changedPeriods) == 0:
            changes = ""
        else:
            changes = "Changes made to the schedule:\n%s" % \
                self.getChangeTable()
        return changes

    def getChangeTable(self):
        table  = "Start (ET)   |      UT      |  LST  |  (hr) |    PI     "
        table += "| Rx        | Session       | Change\n"
        table += "-------------------------------------------------------"
        table += "-------------------------------------------\n"
        
        for p in self.changedPeriods:
            if p.session.project.pcode == "Maintenance":
                pi = ""
            else:
                try:
                    pi = p.session.project.investigator_set.filter(principal_investigator=True)[0].user.last_name[:9]
                except:
                    pi = "unknown"

            table += "%s | %s | %s | %5s | %-9s | %-9s | %-13s | %s\n" % (
                TimeAgent.utc2est(p.start).strftime('%b %d %H:%M')
              , p.start.strftime('%b %d %H:%M')
              , TimeAgent.dt2tlst(p.start).strftime('%H:%M')
              , "%2.2f" % p.duration
              , pi
              , p.session.receiver_list_simple()[:9]
              , p.session.name
              , "rescheduled" if not p.isDeleted() else "removed"
            )
        return table
