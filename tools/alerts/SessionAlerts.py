from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models         import Window, Elective, Period
from utilities.notifiers.SessionAlertNotifier import *

class SessionAlerts(object):

    def __init__(self, quiet = True, filename = None, stageBoundary = 15):

        self.stageBoundary = stageBoundary
        self.now = datetime.utcnow()
        
        # for reporting results
        self.quiet = quiet
        self.filename = filename if filename is not None else "SessionAlerts.txt"
        self.reportLines = []
       
    def findDisabledSessionAlerts(self, now = None):
        now   = now if now is not None else datetime.utcnow()
        today = datetime(now.year, now.month, now.day)

        def withinWindowBoundary(w):
            daysTillStart   = abs((w.start_datetime() - today).days)
            return (daysTillStart <= self.stageBoundary and now < w.default_period.start) \
                   or (now >= w.start_datetime() and now <= w.default_period.start)

        retval  = [w for w in Window.objects.filter(complete = False
                                                  , session__status__enabled = False)
                     if withinWindowBoundary(w)]

        def withinElectiveBoundary(e):
            start, end    = e.periodDateRange()
            daysTillStart = abs((start - today).days)
            return (daysTillStart <= self.stageBoundary and now <= end)

        retval.extend([e for e in Elective.objects.filter(complete = False
                                                        , session__status__enabled = False)
                         if withinElectiveBoundary(e)])

        def withinFixedBoundary(p):
            start = p.start
            daysTillStart = abs((start - today).days)
            return daysTillStart <= self.stageBoundary and now <= start

        retval.extend([p for p in Period.objects.filter(session__session_type__type = 'fixed'
                                                      , state__name = 'Pending'
                                                      , session__status__enabled = False)
                         if withinFixedBoundary(p)])

        return retval

    def findUnauthorizedSessionAlerts(self, now = None):
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

    def raiseAlertsDSSTeam(self, now = None, test = False, quiet = True):

        self.stageBoundary = 4
        self.quiet = quiet
        for unknown in self.findDisabledSessionAlerts(now):
            
            # report this
            self.add("Alert for %s session # %d\n" % (unknown.session.session_type.type
                                                    , unknown.session.id))
            
            sa = SessionAlertNotifier(unknown = unknown
                                    , test = test)
            
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
        self.stageBoundary = 15

    def raiseAlerts(self, now = None, test = False, quiet = True):

        self.quiet = quiet
        for unknown in self.findDisabledSessionAlerts(now):
            
            # report this
            self.add("Alert for %s session # %d\n" % (unknown.session.session_type.type
                                                    , unknown.session.id))
            
            sa = SessionAlertNotifier(unknown = unknown
                                    , test = test
                                    , type = "disabled_observers")
            
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
