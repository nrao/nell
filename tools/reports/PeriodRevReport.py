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
import settings
setup_environ(settings)

from scheduler.models import *
from reversion.models import Version
from RevisionReport import RevisionReport
from datetime       import datetime

class PeriodRevReport(RevisionReport):
    def __init__(self, filename = None):
        super(PeriodRevReport, self).__init__(filename)
       
        self.relatedClasses = ['Period_Accounting'
                              ]

    def reportSessionPeriods(self
                           , sesshun
                           , time = None
                           , field = None
                           , deleted = False
                             ):
        "Reports all periods for a given session"

        # get the periods for this session
        ps = sesshun.period_set.all()
        # include deleted?
        if not deleted:
            ps = [p for p in ps if p.state.abbreviation != "D"]
        for p in ps:
            self.reportPeriod(p.id, time, field)
            
    def reportPeriods(self, start, time = None, field = None, deleted = False):
        "Reports all periods that have given start time"

        # in practice, just one non-deleted period per start time, if any.
        ps = self.getPeriods(start, deleted)
        for p in ps:
            self.reportPeriod(p.id, time, field)

    def getPeriods(self, start, deleted = False):

        ps = Period.objects.filter(start = start)
        if not deleted:
            ps = [p for p in ps if p.state.abbreviation != "D"]
        return ps

    def reportPeriod(self, id, time = None, field = None):
        p = Period.objects.get(id = id)
        self.add("Revision Report for Period: %s\n\n" % p)
        self.reportObject(p, time, field)
        self.add("\nDiffs:\n ")
        self.reportPeriodDiffs(id)
        self.write()
    
    def reportPeriodDiffs(self, id):
        diffs = []
        p = Period.objects.get(id = id)
        self.add("Differences for Period: %s\n\n" % p)
        diffs.extend(self.getObjectDiffs(p)) 
        diffs.extend(self.getObjectDiffs(p.accounting)) 
        rps = Period_Receiver.objects.filter(period = p)
        for r in rps:
        #for r in p.receivers.all():
            diffs.extend(self.getObjectDiffs(r))
        diffs.sort(key=lambda d: d.dt)    
        for d in diffs:
            self.add("%s\n" % d)
        self.write()    

    def reportPeriodForTime(self, id, timeStr):
        p = Period.objects.get(id = id)
        self.add("Period: %s at %s\n\n" % (p, timeStr))
        self.reportObjectForTime(p, timeStr)
        self.write() 

    def runFromCommandLine(self, args):

        msg = None
        keys = ['type']
        types = ['session', 'start']

        # first check of arguments
        opts, msg = self.parseOptions(args[1:], keys)
        if msg is not None:
            return msg
        type  = opts['type']    
        if type not in types:
            return "type arg must be in type: %s" % (", ".join(types))

        # what type of report to run?
        if type == 'session':
            pcode = opts.get('pcode', None)
            name = opts.get('name', None)
            if pcode is None or name is None:
                return "type=session must include session name & pcode"
            s = self.getSession(pcode, name)    
            self.reportSessionPeriods(s)
        elif type == 'start':
            timeStr = opts.get('time', None)
            if timeStr is None:
                return "type=start must include time option"
            try:
                dt = datetime.strptime(timeStr, self.timeFormat)
            except:
                return "could not format time string: %s" % timeStr
            self.reportPeriods(dt)
        else:
            return "Type %s not supported" % type
        return msg


def show_help(program):
    print "\nThe arguments to", program, "are:"
    print "\t-type=type [-time=time] [-pcode=pcode] [-name=name]"
    print "\nwhere:"
    print "\ttype  = one of [session, start]"
    print "\tpcode = if type session, project code, in double quotes"
    print "\tname  = if type session, session name, in double quotes"
    print "\ttime  = if type start chosen, the start time in YY-mm-dd HH:MM:SS"
    print "\nAll required arguments are required.  Anything else is optional :)"

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 2:
        show_help(sys.argv[0])
        sys.exit()
    else:    
        filename = "PeriodRevReport.txt"
        pr = PeriodRevReport(filename = filename)                 
        msg = pr.runFromCommandLine(sys.argv)
            
        if msg is not None:
            print msg
            print ""
            show_help(sys.argv[0])
            sys.exit()
        
