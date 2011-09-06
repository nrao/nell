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

#! /usr/bin/env python

from django.core.management import setup_environ
import settings, sys
setup_environ(settings)

from datetime import datetime

from scheduler.models         import Elective
from utilities.notifiers.ElecAlertNotifier        import ElecAlertNotifier
from BlackoutAlerts import BlackoutAlerts


class ElectiveAlerts(BlackoutAlerts):

    """
    This class is responsible for both finding issues with electives and
    constraints (blackouts) and sending notifications
    concerning these issues.
    """
   
    def __init__(self, quiet = True, filename = None):
        BlackoutAlerts.__init__(self
                              , quiet = quiet
                              , filename = filename
                              , type = "Elective")
        self.lostPeriodCount = 0

    def getBlackedOutElectivePeriods(self, now = None, elecs = []):
        return self.getBlackedOutPeriods(now = now, objs = elecs)

    def findBlackoutAlerts(self, stage = 1, now = None, elecs = []):

        if len(elecs) == 0:
            # we really only care about electives that are not complete
            elecs = Elective.objects.filter(complete = False)
        return BlackoutAlerts.findBlackoutAlerts(self
                                        , stage = stage
                                        , now = now
                                        , objs = elecs
                                          )

    def raiseAlerts(self
                  , stage = 1
                  , now = None
                  , test = False
                  , quiet = True
                  , elecs = []):
        """
        Finds problems with electives, determines the proper type of
        emails, then sends the emails.
        """

        self.quiet = quiet
        for elective, periods, stage in self.findBlackoutAlerts(stage, now, elecs = elecs):
            
            # report this
            self.add("Alert for Elective # %d; stage = %d\n" % (elective.id, stage))
            
            ean = ElecAlertNotifier(elective = elective
                                 , test = test
                                  )
            #print ean.email.GetText()
            if not test:
                if ean.email is not None:
                    self.add("Notifying for Elective # %d: %s\n" % (elective.id, ean.email.GetRecipientString()))
                ean.notify()
        
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
The arguments to ElectiveAlerts are:
   [-pcode=pcode] [-stage=stage] [-test=test] [-quiet=quiet]
where:
   pcode = project code whose electives will be checked; otherwise, all incomplete electives are checked.
   stage = [1,2]; Stage 1: Emails will be sent to observers once per week (Monday morning) until 15 days before the elective start date; Stage 2: 15 days before elective start, emails are sent every day.
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
        pelecs = Elective.objects.filter(session__project__pcode = pcode)
        elecs = [e for e in pelecs if not e.complete]
        if elecs:
            print "Raising Elective Alerts for Project: %s" % pcode
        else:
            print "Project %s has no non-complete electives" % pcode
            sys.exit(3)
    else:
        elecs = []
        print "Raising Elective Alerts for all Projects"
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
    wa = ElectiveAlerts()
    cnt = wa.raiseAlerts(stage = stage
           , elecs = elecs
           , now = datetime.utcnow()
           , test = test
           , quiet = quiet)
    sys.exit(cnt)

