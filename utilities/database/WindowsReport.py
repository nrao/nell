#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models      import *

# from PR2Q2:
#    *  total # of windowed sessions
#    * total # of windows
#    * total # of 'initialized' windows vs. non-initialized ones
#    * for each windowed session:
#          o report periods outside of any windows, or not assigned to any window
#          o overlapping windows
#          o for each window report
#                + start_date
#                + duration
#                + default_period
#                + period
#                + flags, including:
#                      # no default_period
#                      # default_period (and/or period) outside of any window 

class WindowsReport():

    def __init__(self, filename = None):

        self.reportLines = []
        self.quietReport = False
        self.filename = filename

    def add(self, lines):
        "For use with printing reports"
        if not self.quietReport:
            print lines
        self.reportLines += lines

    def printData(self, data, cols, header = False):
        "For use with printing reports."
        self.add(" ".join([h[0:c].rjust(c) for h, c in zip(data, cols)]) + "\n")
        if header:
            self.add(("-" * (sum(cols) + len(cols))) + "\n")

    def isInitialized(self, window):
        if window.start_date is None or window.duration is None \
            or window.default_period is None or window.session is None:
            return False
        else:
            return True

    def periodStr(self, period):
        if period is not None:
            return "%s for %5.2f hrs (%s)" % (period.start
                                            , period.duration
                                            , period.state.abbreviation)
        else:
            return "None"

    def report(self):

        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")
        deleted   = Period_State.get_state("D")

        wins = Window.objects.all().order_by("start_date")
        wss  = Sesshun.objects.filter(session_type__type = "windowed").order_by("name")
        fss  = Sesshun.objects.filter(session_type__type = "fixed").order_by("name")
        oss  = Sesshun.objects.filter(session_type__type = "open").order_by("name")
        ss  = Sesshun.objects.order_by("name")

        # any type of session could have windows
        ss_wins = [s for s in ss if len(s.window_set.all()) != 0]

        # which of these *are not* windowed?
        ss_wins_not_windowed = [s for s in ss_wins \
            if s.session_type.type != "windowed"]
        
        badWins = [w for w in wins if not self.isInitialized(w)]
        goodWins = [w for w in wins if self.isInitialized(w)]

        # windowed sessions with no windoes?
        no_wins = [s for s in wss if len(s.window_set.all()) == 0]

        # number of windows that are in pending
        pending_wins = [w for w in goodWins if w.state() == pending]

        # number of windows that are in scheduled
        scheduled_wins = [w for w in goodWins if w.state() == scheduled]

        # number of windows that have been scheduled before their default
        scheduled_early_wins = [w for w in scheduled_wins \
                                  if w.default_period.state == deleted]

        self.add("Number of Windowed Sessions: %d\n" % len(wss)) 
        self.add("Number of Fixed Sessions: %d\n" % len(fss)) 
        self.add("Number of Open Sessions: %d\n" % len(oss)) 
        self.add("Number of Sessions w/ Windows: %d\n" % len(ss_wins)) 
        self.add("Number of Sessions w/ Windows that aren not windowed (BAD): %d\n" % len(ss_wins_not_windowed)) 
        self.add("Number of Windowed Sessions w/ out Windows (VERY BAD): %d\n" % len(no_wins))
        self.add("Number of Windows: %d\n" % len(wins)) 
        self.add("Number of uninitialized Windows: %d\n" % len(badWins))
        self.add("Number of pending windows: %d\n" % len(pending_wins))
        self.add("Number of scheduled windows: %d\n" % len(scheduled_wins))
        self.add("Number of scheduled early windows: %d\n" % \
            len(scheduled_early_wins))

        for ws in ss_wins:
            numWins = len(ws.window_set.all()) 
            self.add("\nSession: %s, type: %s, # windows: %d\n" % \
                (ws.name, ws.session_type.type, numWins))
            # TBF: any bad periods? 
            ps = ws.period_set.order_by("start")
            badPs = [p for p in ps if not p.has_valid_windows()]
            if len(badPs) != 0:
                self.add("%d of %d periods not assigned to windows properly.\n" \
                    % (len(badPs), len(ps)))
                for b in badPs:
                    self.add("    %s\n" % self.periodStr(b))
            if numWins > 0:
                cols = [5, 12, 5, 40, 40, 20]
                data = ["id", "start", "# days", "default", "period", "notes"]
                self.printData(data, cols, True)
            wins = list(ws.window_set.all())
            wins.sort(key = lambda x:(x.start_date, x.start_date))
            for win in wins:
                flags = ""
                if win.default_period is not None:
                    flags += "Default ~in." \
                        if not win.isInWindow(win.default_period) else ""
                if win.period is not None:        
                    flags += " Period ~in." \
                        if not win.isInWindow(win.period) else ""
                data = [str(win.id)
                      , win.start_date.strftime("%Y-%m-%d")
                      , str(win.duration)
                      , self.periodStr(win.default_period) 
                      , self.periodStr(win.period)
                      , flags
                        ]
                self.printData(data, cols)   

        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)

if __name__ == '__main__':
    WindowsReport(filename = "WindowsReport.txt").report()            
