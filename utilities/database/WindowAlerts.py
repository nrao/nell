#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models         import *
from utilities.WinAlertNotifier import WinAlertNotifier

class WindowAlerts():

    """
    This class is responsible for both finding issues with windows and
    constraints (enable flag, blackouts, etc.), and sending notifications
    concerning these issues.
    """
   
    def __init__(self):

        # two stages for alerts; how many days before start of window 
        # to go from stage I to stage II?
        self.stageBoundary = 15
 
        self.now = datetime.utcnow()
        
        self.wins = Window.objects.all()

    def getWindowTimes(self, wins = []):
        """
        Returns the stats on windows.
        For use in determining if alerts are raised.
        """
       
        if len(wins) == 0:
            # we really only care about windows that are not complete
            wins = Window.objects.filter(complete = False)
        return zip(wins
                , [w.getBlackedOutSchedulableTime() for w in wins])

    def findAlertLevels(self, wins = []):
        """
        Gets the stats on windows, and examines them to see if
        an alarm needs to be raised.
        """

        stats = self.getWindowTimes(wins = wins)
        alerts = []
        for w, stat in stats:
            hrsSchedulable = stat[0]
            hrsBlacked = stat[1]
            ratio = hrsBlacked/hrsSchedulable

            if ratio > .10 and ratio < .50:
                alerts.append((w, stat, 1))
            elif ratio > .50:
                alerts.append((w, stat, 2))
            else:
                pass
        return alerts 

    def findAlerts(self, stage = 1, now = None, wins = []):
        """
        Finds problems with windows, and returns the proper response.
        Emails will be sent to observers once per week (Monday morning)
        until 15 days before the window start date. (Stage I)
        Emails will be sent daily to all project investigators =< 15 
        days before the window end date. (Stage II)
        """

        # Just two stages (see comment above)
        assert stage in (1, 2)

        alertLevels = self.findAlertLevels(wins = wins)

        now = now if now is not None else datetime.utcnow()
        today = datetime(now.year, now.month, now.day)

        alerts = []
        if stage == 1:
            for w, stat, level in alertLevels:
                daysTillStart = (w.start_datetime() - today).days
                if daysTillStart > self.stageBoundary:
                    alerts.append((w, stat, level, 1))
        elif stage == 2:
            for w, stat, level in alertLevels:
                daysTillStart = (w.start_datetime() - today).days
                if daysTillStart <= self.stageBoundary:
                    alerts.append((w, stat, level, 2))
                    
        return alerts                    

    def raiseAlerts(self
                  , stage = 1
                  , now = None
                  , test = False
                  , wins = []):
        """
        Finds problems with windows, determines the proper type of
        emails, then sends the emails.
        """

        alerts = self.findAlerts(stage, now, wins = wins)

        for window, stats, level, stg in alerts:
            
            wa = WinAlertNotifier(window = window
                                , level = level
                                , stage = stg
                                , test = test)
            
            # for now, *really* play it safe
            if not test:
                #print wa.email.GetText()
                wa.notify()


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
   [-pcode=pcode] [-stage=stage]
where:
   pcode = project code whose windows will be checked; otherwise, all incomplete windows are checked.
   stage = [1,2]; Stage 1: Emails will be sent to observers once per week (Monday morning) until 15 days before the window start date; Stage 2: 15 days before window start, emails are sent every day.
    """
    print hlp

if __name__ == '__main__':
    msg = None
    keys = ['pcode', 'stage']
    opts, msg = parseOptions(sys.argv[1:], keys)
    if msg is not None:
        print msg    
        showHelp()
        sys.exit(2)
    pcode = opts['pcode']    
    if pcode:
        wins = Window.objects.filter(session__project__pcode = pcode)
        print "Raising Window Alerts for Project: %s" % pcode
    else:
        wins = []
        print "Raising Window Alerts for all Projects"
    stage = int(opts['stage']) if opts['stage'] is not None else 1    
    print "Alerts at Stage %d" % stage
    if stage not in [1,2]:
        print "stage option must be in [1,2]"
        showHelp()
        sys.exit(2)
    wa = WindowAlerts()
    wa.raiseAlerts(stage = stage, wins = wins)

                



       
