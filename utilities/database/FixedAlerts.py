#! /usr/bin/env python

from django.core.management import setup_environ
import settings, sys
setup_environ(settings)

from datetime import datetime

from sesshuns.models         import Sesshun
from sesshuns.models         import Session_Type
from utilities               import FixedAlertNotifier

class FixedAlerts():

    """
    This class is responsible for both finding issues with fixed periods and
    constraints (enable flag, blackouts, etc.), and sending notifications
    concerning these issues.
    """
   
    def __init__(self, quiet = True, filename = None):

        # two stages for alerts; how many days before start of elective 
        # to go from stage I to stage II?
        self.stageBoundary = 15
 
        self.now = datetime.utcnow()
        
        # for reporting results
        self.quiet = quiet
        self.filename = filename if filename is not None else "FixedAlerts.txt"
        self.reportLines = []
        self.lostPeriodCount = 0
       

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

    def getBlackedOutFixedPeriods(self, sessions = []):
        """
        Returns the stats on fixed sessions.  For use in determining
        if alerts are raised.  Returns a list of offending
        blacked-out periods, i.e.,
        [(session, [blacked out period])]
        where the list of periods are sorted by start times.
        """
       
        if len(sessions) == 0:
            sessions = Sesshun.objects.filter(project__pcode = pcode
                                            , session_type = fixed)
        self.add("Retrieving periods for %d Fixed Sessions\n" % len(sessions))    
        injured = []
        for s in sessions:
            self.add("Periods for (%d) %s\n" % (s.id, s.__str__()))
            periods = s.getBlackedOutSchedulablePeriods()
            cnt = len(periods)
            self.add("%d schedulable blacked-out periods\n" % cnt)
            self.lostPeriodCount += cnt
            if periods:
                injured.append((s, periods))
                self.add("Blacked-out periods for (%d) %s\n" % (s.id, s.__str__()))
                pstr = '; '.join(str(p) for p in periods)
                for p in periods:
                    self.add("%s" % pstr)
                self.add("\n")
        return injured    

    def findBlackoutAlerts(self, stage = 1, now = None, sessions = []):
        """
        Finds problems with fixed sessions, and returns the proper
        response.
        Stage is determined by the earliest offending period.
        Emails will be sent to observers once per week (Monday morning)
        until 15 days before the period start date. (Stage I)
        Emails will be sent daily to all project investigators =< 15 
        days before the period end date. (Stage II)
        """

        # Just two stages (see comment above)
        assert stage in (1, 2)

        def withinBoundary(st, stage, now):
            now   = now if now is not None else datetime.utcnow()
            today = datetime(now.year, now.month, now.day)

            daysTillStart = (st - today).days
            if stage == 1:
                return daysTillStart > self.stageBoundary
            else:
                return daysTillStart <= self.stageBoundary

        return [(s, ps, stage)
                for s, ps in self.getBlackedOutFixedPeriods(sessions)
                    if withinBoundary(ps[0].start, stage, now)]

    def raiseAlerts(self
                  , stage = 1
                  , now = None
                  , test = False
                  , quiet = True
                  , sessions = []):
        """
        Finds problems with fixed periods, determines the proper type of
        emails, then sends the emails.
        """

        self.quiet = quiet
        for sess, periods, stage in self.findBlackoutAlerts(stage, now, sessions = sessions):
            
            # report this
            self.add("Alert for Session # %d; stage = %d\n" % (sess.id, stage))
            
            san = FixedAlertNotifier(session = sess
                                   , test = test
                                    )
            #print san.email.GetText()
            if not test:
                if san.email is not None:
                    self.add("Notifying for Fixed Sesshun # %d: %s\n" % (sess.id, san.email.GetRecipientString()))
                san.notify()
        
        self.write()

        return self.lostPeriodCount

# command line interface
def parseOptions(args, keys):
    "For use with command line"
    options = {}
    # parse what's there
    for arg in args:
        parts = arg.split("=")
        if len(parts) != 2:
            return (options, "argument invalid: %s" % arg)
        if parts[0][0] != '-':
            return (options, "argument needs leading dash: %s" % arg)
        key = parts[0][1:]
        if key not in keys:
            return (options, "unknown argument: %s" % key)
        options[key] = parts[1]
    # anything missing?
    for k in keys:
        if k not in options.keys():
            #return (options, "args missing: %s" % k)
            options[k] = None
    return (options, None)

def showHelp():
    "How do I use this command line?"

    hlp = """
The arguments to FixedAlerts are:
   [-pcode=pcode] [-stage=stage] [-test=test] [-quiet=quiet]
where:
   pcode = project code whose fixed periods will be checked; otherwise, all undeleted periods are checked.
   stage = [1,2]; Stage 1: Emails will be sent to observers once per week (Monday morning) until 15 days before the period's start date; Stage 2: 15 days before periode start, emails are sent every day.
   test = if True, no emails are sent.
   quiet = if True, report is not sent to stdout.
    """
    print hlp

if __name__ == '__main__':
    msg = None
    keys = ['pcode', 'stage', 'test', 'quiet']
    opts, msg = parseOptions(sys.argv[1:], keys)
    if msg is not None:
        print msg    
        showHelp()
        sys.exit(2)
    pcode = opts['pcode']    
    if pcode:
        fixed = Session_Type.objects.filter(type = 'fixed')
        sessions = Sesshun.objects.filter(project__pcode = pcode
                                        , session_type = fixed)
        if sessions:
            print "Raising Fixed Alerts for Project: %s" % pcode
        else:
            print "Project %s has no fixed sessions" % pcode
            sys.exit(3)
    else:
        sessions = []
        print "Raising Fixed Alerts for all Projects"
    stage = int(opts['stage']) if opts['stage'] is not None else 1    
    print "Alerts at Stage %d" % stage
    if stage not in [1,2]:
        print "stage option must be in [1,2]"
        showHelp()
        sys.exit(2)
    if opts['test'] is not None and opts['test'] not in ['True', 'False']:
        print "test must be True or False"
        showHelp()
        sys.exit(2)
    test = opts['test'] == 'True' if opts['test'] is not None else True  
    print "Sending email notifications: %s" % (not test)
    if opts['quiet'] is not None and opts['quiet'] not in ['True', 'False']:
        print "quiet must be True or False"
        showHelp()
        sys.exit(2)
    quiet = opts['quiet'] == 'True' if opts['quiet'] is not None else True  
    wa = FixedAlerts()
    cnt = wa.raiseAlerts(stage = stage, sessions = sessions
                       , test = test, quiet = quiet)
    sys.exit(cnt)

