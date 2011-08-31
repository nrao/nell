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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models         import Window, Elective, Period
from utilities.notifiers.SessionAlertNotifier import *

class SessionInActiveAlerts(object):

    """
    This class is responsible for finding issues with constrained
    sessions (of type Fixed, Elective or Windowed) due to their
    being inactive (unenabled, or unauthorized), and one of their
    opportunities to observe is in the near future.
    """

    def __init__(self, quiet = True, filename = None, stageBoundary = 15):

        # the nature of the alerts change as the event gets closer,
        # and that change's boundary is set here.
        self.stageBoundary = stageBoundary
        self.now = datetime.utcnow()
        
        # for reporting results
        self.quiet = quiet
        self.filename = filename if filename is not None else "SessionAlerts.txt"
        self.reportLines = []
       
    def findDisabledSessionAlerts(self, now = None):
        """
        For each constrained type (Fixed, Elective, Windowed)
        of disabled session, returns the compromised
        objects, if any.
        For example, if a session is disabled, but an incomplete
        window is coming up soon enough, this window object
        will be added to the list of alerts.
        """

        now   = now if now is not None else datetime.utcnow()
        today = datetime(now.year, now.month, now.day)

        def withinWindowBoundary(w):
            daysTillStart   = abs((w.start_datetime() - today).days)
            return (daysTillStart <= self.stageBoundary and now < w.default_period.start) \
                   or (now >= w.start_datetime() and now <= w.default_period.start)
        # what windows risk not getting completed?
        retval  = [w for w in Window.objects.filter(complete = False
                                                  , session__status__enabled = False)
                     if withinWindowBoundary(w)]

        def withinElectiveBoundary(e):
            start, end    = e.periodDateRange()
            if start is None or end is None:
                return False

            daysTillStart = abs((start - today).days)
            return (daysTillStart <= self.stageBoundary and now <= end)
        # what electives risk not getting completed?
        retval.extend([e for e in Elective.objects.filter(complete = False
                                                        , session__status__enabled = False)
                         if withinElectiveBoundary(e)])

        def withinFixedBoundary(p):
            start = p.start
            daysTillStart = abs((start - today).days)
            return daysTillStart <= self.stageBoundary and now <= start

        # what fixed periods risk getting scheduled, even though
        # their session is disabled?
        retval.extend([p for p in Period.objects.filter(session__session_type__type = 'fixed'
                                                      , state__name = 'Pending'
                                                      , session__status__enabled = False)
                         if withinFixedBoundary(p)])

        return retval

    def findUnauthorizedSessionAlerts(self, now = None):
        """
        Is it me, or is this the same exact thing as
        findDisabledSessionAlerts, but instead of checking
        session__status__enabled, we're checking session__status__authorized?
        """
    
        now   = now if now is not None else datetime.utcnow()
        today = datetime(now.year, now.month, now.day)

        def withinWindowBoundary(w):
            daysTillStart   = abs((w.start_datetime() - today).days)
            return (daysTillStart <= self.stageBoundary and now < w.default_period.start) \
                   or (now >= w.start_datetime() and now <= w.default_period.start)

        retval  = [w for w in Window.objects.filter(complete = False
                                                  , session__status__authorized = False)
                     if withinWindowBoundary(w)]

        def withinElectiveBoundary(e):
            start, end    = e.periodDateRange()
            daysTillStart = abs((start - today).days)
            return (daysTillStart <= self.stageBoundary and now <= end)

        retval.extend([e for e in Elective.objects.filter(complete = False
                                                        , session__status__authorized = False)
                         if withinElectiveBoundary(e)])

        def withinFixedBoundary(p):
            start = p.start
            daysTillStart = abs((start - today).days)
            return daysTillStart <= self.stageBoundary and now <= start

        retval.extend([p for p in Period.objects.filter(session__session_type__type = 'fixed'
                                                      , state__name = 'Pending'
                                                      , session__status__authorized = False)
                         if withinFixedBoundary(p)])

        return retval

    def getRange(self, unknown):
        return SessionAlertEmail.getRange(unknown)

    def add(self, lines):
        "For use with printing reports"
        if not self.quiet:
            print lines
        self.reportLines += lines

    def write(self):        
        "For use with printing reports"
        # write it out
        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)
            f.close()

    def raiseAlertsDSSTeam(self, now = None, test = False):
        self.stageBoundary = 4
        for unknown in self.findDisabledSessionAlerts(now):
            
            # report this
            self.add("Alert for %s session # %d\n" % (unknown.session.session_type.type
                                                    , unknown.session.id))
            
            sa = SessionAlertNotifier(unknown = unknown
                                    , test = test
                                    , flag = "enabled"
                                     )
            
            # for now, *really* play it safe
            if not test:
                if sa.email is not None:
                    self.add("Notifying DSS Team about disabled %s session # %d: %s\n" % \
                         (unknown.session.session_type.type
                        , unknown.session.id
                        , sa.email.GetRecipientString()))
                #print sa.email.GetText()
                sa.notify()
        self.write()
        for unknown in self.findUnauthorizedSessionAlerts(now):
            
            # report this
            self.add("Alert for %s session # %d\n" % (unknown.session.session_type.type
                                                    , unknown.session.id))
            
            sa = SessionAlertNotifier(unknown = unknown
                                    , test = test
                                    , flag = "authorized"
                                     )
            
            # for now, *really* play it safe
            if not test:
                if sa.email is not None:
                    self.add("Notifying DSS Team about unauthorized %s session # %d: %s\n" % \
                         (unknown.session.session_type.type
                        , unknown.session.id
                        , sa.email.GetRecipientString()))
                #print sa.email.GetText()
                sa.notify()
        self.write()
        self.stageBoundary = 15

    def raiseAlerts(self, now = None, test = False):

        for unknown in self.findDisabledSessionAlerts(now):
            
            # report this
            self.add("Alert for %s session # %d\n" % (unknown.session.session_type.type
                                                    , unknown.session.id))
            
            sa = SessionAlertNotifier(unknown = unknown
                                    , test = test
                                    , type = "observers"
                                    , flag = "enabled"
                                     )
            
            # for now, *really* play it safe
            if not test:
                if sa.email is not None:
                    self.add("Notifying observers about disabled %s session # %d: %s\n" % \
                         (unknown.session.session_type.type
                        , unknown.session.id
                        , sa.email.GetRecipientString()))
                #print sa.email.GetText()
                sa.notify()
        self.write()

if __name__ == "__main__":
    sa = SessionAlerts()
    sa.raiseAlerts()
    sa.raiseAlertsDSSTeam()
