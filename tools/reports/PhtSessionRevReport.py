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

from pht.models import *
from reversion.models import Version
from RevisionReport import RevisionReport

class PhtSessionRevReport(RevisionReport):

    def __init__(self, filename = None):
        super(PhtSessionRevReport, self).__init__(filename)
       
        self.relatedClasses = ['Backend'
                             , 'Receiver'
                             , 'Monitoring'
                             , 'Target'
                             , 'Flags'
                             , 'Allotment'
                              ]

    def getRelatedObjectVersions(self, sesshun, time = None):
        "We want to look for revisions with allotment, & other objs."

        vs = []
        vs.extend(Version.objects.get_for_object(sesshun.allotment))
        vs.extend(Version.objects.get_for_object(sesshun.monitoring))
        vs.extend(Version.objects.get_for_object(sesshun.flags))
        vs.extend(Version.objects.get_for_object(sesshun.target))
        return vs    

         
    def getPhtSession(self, pcode, name):
        p = Proposal.objects.get(pcode = pcode)
        for s in p.session_set.all().order_by('id'):
            if s.name == name:
                return s
        return None        

    def getSessionRcvrDiffs(self, pcode, name):
        """
        Rcvrs for Session and Periods are deleted and readded every time a 
        change is made,  so tracking their changes takes a lot of
        interpretation.
        """
        diffs = []
        s = self.getPhtSession(pcode, name)
        # get current recievrs for last check
        currentRgs = s.receiver_group_set.all()
        # get all the deleted Rcvr_Groups for this session
        id = s.id
        vs = Version.objects.get_deleted(Receiver_Group)
        svs = []
        for v in vs:
            if v.field_dict['session'] == id:
                svs.append(v)
                #print v.field_dict['receivers']
    
        # Now get the diffs, but keep only those that pertain to receivers
        if len(svs) < 2:
           return diffs
        vprev = svs[0]
        for v in svs[1:]:
            ds = self.diffVersions(vprev, v)
            for d in ds:
                if d.field == "receivers":
                    diffs.append(self.interpretRcvrGrpDiff(d))
            vprev = v
    
        # see if the last diff is different then our current rcvrs
        if len(currentRgs) == 1 and len(diffs) > 0:
            # anything else is too complicated 
            rcvrs = [r.abbreviation for r in currentRgs[0].receivers.all()]
            rcvrs.sort()
            lastRs = diffs[-1][3]
            lastRs.sort()
            if rcvrs != lastRs:
                diff = VersionDiff(dt = datetime.now()
                                 , field = "receivers"
                                 , value1 = lastRs
                                 , value2 = rcvrs
                                  )
                diffs.append(diff)
    
        return diffs             
    
    def getSessionRcvrDiffsBad(self, pcode, name):
    
        diffs = []
        s = self.getPhtSession(pcode, name) 
        vs = Version.objects.get_for_object(s)
        if len(vs) < 2:
            return []
        vprev = vs[0]
        for v in vs[1:]:
            print "v: ", v
            prevS = vprev.object_version.object
            currS = v.object_version.object
            v1 = prevS.receiver_list()
            v2 = currS.receiver_list()
            print "comparing: ", v1, v2
            if v1 != v2:
                dt = vprev.revision.date_created
                diffs.append((dt, "receivers", v1, v2))
        
    
        return diffs
            
    
    def reportSessionDiffs(self, pcode, name): #, periods = False):
    
        self.add("Differences for Session: %s (%s)\n\n" % (name, pcode))

        diffs = []
        s = self.getPhtSession(pcode, name) 
        if s is None:
            print "Could not find Session"
            return
        diffs.extend(self.getObjectDiffs(s)) 
        diffs.extend(self.getObjectDiffs(s.allotment))
        diffs.extend(self.getObjectDiffs(s.monitoring))
        diffs.extend(self.getObjectDiffs(s.flags))
        diffs.extend(self.getObjectDiffs(s.target))
        #diffs.extend(self.getSessionRcvrDiffs(pcode, name))
        diffs.sort(key=lambda v: v.dt)
        for d in diffs:
            self.add("%s\n" % d)
        #if periods:
        #    ps = s.period_set.all()
        #    for p in ps:
        #        self.add("\n****** Diffs for Period: %s\n" % p)
        #        self.reportPeriodDiffs(p.id)

        self.write()


    
    def reportSession(self
                    , pcode
                    , name
                    , time = None
                    , field = None
                    #, periods = False):
                      ):

        self.add("Revision Report for Session: %s (%s)\n\n" % (name, pcode))

        s = self.getSession(pcode, name) 
        self.reportObject(s, time, field)
        self.add("\nDiffs: \n")
        self.reportSessionDiffs(pcode, name) #periods)

        self.write()

    def reportSessionForTime(self, pcode, name, timeStr):
        self.add("Session: %s (%s) at %s\n\n" % (name, pcode, timeStr))
        s = self.getSession(pcode, name) 
        self.reportObjectForTime(s, timeStr)
        self.write()

    def runFromCommandLine(self, args):

        msg = None
        keys = ['pcode', 'name', 'type']
        types = ['history', 'diffs', 'time']

        # first check of arguments
        opts, msg = self.parseOptions(args[1:], keys)
        if msg is not None:
            return msg
        type  = opts['type']    
        pcode = opts['pcode']    
        name  = opts['name']    
        if type not in types:
            return "type arg must be in type: %s" % (", ".join(types))

        # what type of report to run?
        if type == 'history':
            self.reportSession(pcode, name)
        elif type == 'diffs':
            self.reportSessionDiffs(pcode, name)
        elif type == 'time':
            timeStr = opts.get('time', None)
            if timeStr is None:
                return "type=time must include time option"
            self.reportSessionForTime(pcode, name, timeStr)
        else:
            return "Type %s not supported" % type
        return msg


def show_help(program):
    print "\nThe arguments to", program, "are:"
    print "\t-pcode=pcode -name=name -type=type [-time=time]"
    print "\nwhere:"
    print "\tpcode = project code, in double quotes"
    print "\tname  = session name, in double quotes"
    print "\ttype  = one of [history, diffs, time]"
    print "\ttime  = if 'time' type chosen, the time in YY-mm-dd HH:MM:SS"
    print "\nAll required arguments are required.  Anything else is optional :)"

if __name__ == '__main__':

    import sys

    if len(sys.argv) < 2:
        show_help(sys.argv[0])
        sys.exit()
    else:    
        filename = "SessionRevReport.txt"
        sr = PhtSessionRevReport(filename = filename)                 
        msg = sr.runFromCommandLine(sys.argv)
            
        if msg is not None:
            print msg
            print ""
            show_help(sys.argv[0])
            sys.exit()
            
