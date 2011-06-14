#! /usr/bin/env python

from django.core.management import setup_environ
import settings, sys
setup_environ(settings)
from datetime import datetime

from scheduler.models            import *
from utilities.notifiers.WinAlertNotifier import WinAlertNotifier

class WindowAlerts():

    """
    This class is responsible for both finding issues with windows and
    constraints (enable flag, blackouts, etc.), and sending notifications
    concerning these issues.
    """
   
    def __init__(self, quiet = True, filename = None):

        # two stages for alerts; how many days before start of window 
        # to go from stage I to stage II?
        self.stageBoundary = 15
 
        # for reporting results
        self.quiet = quiet
        self.filename = filename if filename is not None else "WinAlerts.txt"
        self.reportLines = []
        self.lostWindowTime = 0
       

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

    def getWindowTimes(self, now, wins = []):
        """
        Returns the stats on windows.
        For use in determining if alerts are raised.
        stat = (Window, (
            (
             total schedulable time ignoring blacked out
           , total schedulable time but blacked out
           , [schedulable ranges ignoring blacked out]
           , [schedulable ranges but blacked out]
            )
                        )
        """
        if len(wins) == 0:
            # we really only care about windows that are not complete
            # and that have ranges
            wins = Window.objects.filter(complete = False)
            wins = [w for w in wins if len(w.windowrange_set.all()) > 0]
        self.add("Retrieving Times for %d Windows\n" % len(wins))    
        times = []
        for w in wins:
            time = w.getBlackedOutSchedulableTime(now)
            times.append((w, time))
            self.add("Times for (%d) %s\n" % (w.id, w.__str__()))
            self.add("Schedulable, Blacked Hrs: (%5.2f, %5.2f)\n" % \
                (time[0], time[1]))
            self.lostWindowTime += time[1] > 0.0
        return times    

    def findAlertLevels(self, now, wins = []):
        """
        Gets the stats on windows, and examines them to see if
        an alarm needs to be raised.
        """

        stats = self.getWindowTimes(now, wins = wins)
        alerts = []
        for w, stat in stats:
            hrsSchedulable = stat[0]
            hrsBlacked = stat[1]
            if hrsSchedulable == 0.0:
                ratio = 0.0 # TBF: or 1.0? Depends on details ...
            else:    
                ratio = hrsBlacked/hrsSchedulable
            if ratio > .10 and ratio < .50:
                alerts.append((w, stat, 1))
            elif ratio > .50:
                alerts.append((w, stat, 2))
            else:
                pass
        return alerts 

    def findBlackoutAlerts(self, stage = 1, now = None, wins = []):
        """
        Finds problems with windows, and returns the proper response.
        Emails will be sent to observers once per week (Monday morning)
        until 15 days before the window start date. (Stage I)
        Emails will be sent daily to all project investigators =< 15 
        days before the window end date. (Stage II)
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

        return [(w, stat, level, stage)
                for w, stat, level in self.findAlertLevels(now, wins = wins)
                    if withinBoundary(w.start_datetime(), stage, now)
               ]

    def raiseAlerts(self
                  , stage = 1
                  , now = None
                  , test = False
                  , quiet = True
                  , wins = []):
        """
        Finds problems with windows, determines the proper type of
        emails, then sends the emails.
        """

        self.quiet = quiet
        for window, stats, level, stg in  self.findBlackoutAlerts(stage, now, wins = wins):
            
            # report this
            self.add("Alert for Window # %d; level = %d, stage = %d\n" % (window.id, level, stg))
            
            wa = WinAlertNotifier(window = window
                                , level = level
                                , stage = stg
                                , test = test)
            
            #print ean.email.GetText()
            if not test:
                if wa.email is not None:
                    self.add("Notifying for Window # %d: %s\n" % (window.id, wa.email.GetRecipientString()))
                wa.notify()
        
        self.write()

        return self.lostWindowTime

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
The arguments to WindowAlerts are:
   [-pcode=pcode] [-stage=stage] [-test=test] [-quiet=quiet]
where:
   pcode = project code whose windows will be checked; otherwise, all incomplete windows are checked.
   stage = [1,2]; Stage 1: Emails will be sent to observers once per week (Monday morning) until 15 days before the window start date; Stage 2: 15 days before window start, emails are sent every day.
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
        pwins = Window.objects.filter(session__project__pcode = pcode)
        wins = [w for w in pwins if not w.complete]
        if elecs:
            print "Raising Window Alerts for Project: %s" % pcode
        else:
            print "Project %s has no non-complete windows\n" % pcode
            sys.exit(3)
    else:
        wins = []
        print "Raising Window Alerts for all Projects"
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
    wa = WindowAlerts()
    wa.raiseAlerts(stage = stage
                 , wins = wins
                 , now = datetime.utcnow()
                 , test = test
                 , quiet = quiet)

                



       
