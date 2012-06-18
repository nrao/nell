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

from scheduler     import models as dss
from pht.models    import *
from pht.utilities import *
from sets          import Set
from datetime      import datetime, timedelta

class SourceConflicts(object):

    def __init__(self, semester = None, quiet = True):

        #if semester is None:
        #    self.semester = '12B'
        #else:
        self.semester = semester

        self.initSearchRadi()    

        # cache of src to src angular distance
        self.distances = {}

        # here's where we put conflicts when we find them
        # structure's first level: proposal being searched details
        # then for each proposal: a list of conflict descriptions,
        # including src's conflicting, the distance between them,
        # and the level of the conflict.  If this gets any bigger
        # we need to define some classes I think.
        self.conflicts = {}

        # for reporting
        self.quiet = quiet
        self.badDistances = []
        self.targetProposals = []
        self.checkedProposals = []

    def initSearchRadi(self):
        "Map receivers to their Search Radi"

        self.hpbw = {
          'NS'  : 0.0 
        , 'Z'   : 0.376 # same as Ka 
        , 'RRI' : 123.5
        , '342' : 36.5
        , '450' : 27.5
        , '600' : 20.7
        , '800' : 15.5
        , '1070' : 12.4
        , 'L' : 8.7
        , 'S' : 4.1
        , 'C' : 2.5
        , 'X' : 1.3
        , 'Hol' : 0.0 
        , 'Ku' : 0.830 
        , 'KFPA' : 0.560
        , 'K' : 0.560
        , 'Ka' : 0.376
        , 'Q' : 0.249
        , 'W' : 0.160
        , 'MBA' : 0.160 
        }

        self.searchRadi = {}
        for r in self.hpbw.keys():
            self.searchRadi[r] = self.calcSearchRadiusForRcvr(r)

    def findConflicts(self, proposals = None, allProposals = None):
        "Main entry point: find all source conflicts"

        # which proposals to check?
        if proposals is None:
            if self.semester is not None:
                proposals = Proposal.objects.filter(semester__semester = self.semester).order_by('pcode')

            else: 
                proposals = Proposal.objects.all().order_by('pcode')

        # which proposals to check against?
        if allProposals is None:
            allProposals = Proposal.objects.all().order_by('pcode')

        # for reporting
        self.targetProposals = [p.pcode for p in proposals]
        self.checkedProposals = [p.pcode for p in allProposals]

        # start checking
        for p in proposals:
            self.findConflictsForProposal(p, allProposals)

    def findConflictsForProposal(self, proposal, allProposals):

        # init the results
        lowestRx = self.getLowestRcvr(proposal)
        rad = self.searchRadi.get(lowestRx.abbreviation, None)
        pcode = proposal.pcode
        self.conflicts[pcode] = {'proposal' : proposal
                               , 'lowestRx' : lowestRx
                               , 'searchRadius' : rad
                               , 'conflicts' : []
                                 }
            
        for p in allProposals:
            # don't check against one's self
            if p.id != proposal.id:
                self.findConflictsBetweenProposals(proposal, p, rad)

    def findConflictsBetweenProposals(self
                                    , targetProp
                                    , searchedProp
                                    , searchRadius = None):
        """
        targetProp - the proposal that we use to determine the search rad
        searchedProp - checking srcs in targetProp against one's in here
        """

        tpcode = targetProp.pcode

        if searchRadius is None:
            lowestRx = self.getLowestRcvr(targetProp)
            searchRadius = self.searchRadi.get(lowestRx.abbreviation
                                             , None)

        # do we need to update our results cache?
        if not self.conflicts.has_key(tpcode):
            self.conflicts[tpcode] = {'proposal' : targetProp
                                    , 'lowestRx' : lowestRx
                                    , 'searchRadius' : searchRadius
                                    , 'conflicts' : []
                                     }

        # now look for conflicts, source against source
        trgSrcs = targetProp.source_set.all().order_by('target_name')
        srchSrcs = searchedProp.source_set.all().order_by('target_name')
        for trgSrc in trgSrcs:
            for srchSrc in srchSrcs:
                conflict = False
                try:
                    d = self.getAngularDistance(trgSrc, srchSrc)
                    if d <= searchRadius and self.passesInclusionCheck(searchedProp):
                        conflict = True
                        srcConflict = {
                        'targetSrc' : trgSrc
                      , 'searchedSrc' : srchSrc
                      , 'searchedProp' : searchedProp
                      , 'distance' : d
                      , 'level' : 0
                        }
                        self.conflicts[tpcode]['conflicts'].append(srcConflict)
                except:
                    print "could not calc distance"
                    srcConflict = {
                        'targetSrc' : trgSrc
                      , 'searchedSrc' : srchSrc
                      , 'searchedProp' : searchedProp
                        }
                    self.badDistances.append(srcConflict)
                if conflict:
                    # see if it's even worse - check the other levels
                    if self.hasSameRcvrConflict(targetProp, searchedProp):
                        self.conflicts[tpcode]['conflicts'][-1]['level'] = 1
                        # check the next level - proprietary period!
                        if self.withinPropietaryDate(srchSrc, searchedProp):
                            self.conflicts[tpcode]['conflicts'][-1]['level'] = 2
                            
    
    def hasSameRcvrConflict(self, targetProp, searchedProp):
        """
        This couldn't be simpler: compare the union of the 
        receivers used at the proposal level.
        """
        targetRcvrs = Set(list(targetProp.bands()))
        searchedRcvrs = Set(list(searchedProp.bands()))
        return len(list(targetRcvrs.intersection(searchedRcvrs))) > 0

    def passesInclusionCheck(self, searchedProp):
        """
        This method checks to see if the searched proposal pass an inclusion check.
        Exclusion Rule: If the grade is B or C and the semester is prior to the current 
                        semester (proposed semester - 1 year) and the proposal had no 
                        observing time then ignore the proposal. 
                        If no last observed date and grade A then include proposal. 
                        If no last observed date and the grade is B or C and proposal 
                        is in the current semester then include proposal.
        """
        # Get the grade of the proposal
        grades = sorted(searchedProp.grades())
        if len(grades) >= 1:
            grade = grades[0]
        else:
            return False # If there's no grade, ignore proposal.

        periods = searchedProp.dss_project.get_observed_periods() if searchedProp.dss_project is not None else []
        # Rule 1
        if grade in ('B', 'C') and \
           searchedProp.semester.semester < dss.Semester.getCurrentSemester().semester and \
           len(periods) == 0:
            print 'Too old and shitty'
            return False
        # Rule 2
        elif len(periods) == 0 and grade == 'A':
            return True
        # Rule 3
        elif len(periods) == 0 and grade in ('B', 'C') and \
           searchedProp.semester.semester == dss.Semester.getCurrentSemester().semester:
            return True
        return True # We shouldn't get here, but if we do might as well include proposal.

    def withinProprietaryDate(self, srchSrc, searchedProp, now = datetime.now()):
        "Any observations within a year?"
        refTime = now - timedelta(days = 365)
        periods = [p for p in searchedProp.dss_project.get_observed_periods() if p.start > refTime]
        return len(periods) > 0
                    
    def getLowestRcvr(self, proposal):
        """"
        Of all the receivers used by all given proposal's sessions, 
        which has the lowest frequency?
        """
        lowest = None
        for s in proposal.session_set.all():
            rxs = s.receivers.all().order_by('freq_low')
            if len(rxs) > 0:
                if lowest is None or lowest.freq_low > rxs[0].freq_low:
                    lowest = rxs[0]
        return lowest            

    def getSearchRadius(self, proposal):
        """
        Search Radius (arc-mins) = 2*HPBW of lowest receiver.
        """
        lowestRcvr = self.getLowestRcvr(proposal)
        if lowestRcvr is None:
            return None
        else:
            return self.searchRadi[lowestRcvr.abbreviation]

    def calcSearchRadiusForRcvr(self, rcvr):        
        "Search Radius (arc-mins) = 2*HPBW of lowest receiver."
        # get HPWB, *2, convert to degress, then to radians
        return arcMin2rad(self.hpbw[rcvr] * 2.0)            
                    
    def getAngularDistance(self, src1, src2):
        "Use a cache for the angular dist between two sources."
        # the cache is important because each proposal checks
        # against the others, we want to avoid recalculating
        # these symettrical distances.
        key1 = (src1.id, src2.id)
        key2 = (src2.id, src1.id)
        if self.distances.has_key(key1):
            dist = self.distances[key1]
        elif self.distances.has_key(key2):
            dist = self.distances[key2]
        else:
            dist = self.calcAngularDistance(src1, src2)
            self.distances[key1] = dist
        return dist    
                    
    def calcAngularDistance(self, src1, src2):
        "Ang. Dist. between two source objs: all in radians"
        return angularDistance(src1.ra
                             , src1.dec
                             , src2.ra
                             , src2.dec)
        
    def report(self):

        self.write("SOURCE CONFLICTS")
        self.write("Proposals targeted (%d):" % len(self.targetProposals))
        for p in self.targetProposals:
           self.write("    %s" % p)
        self.write("Proposals checked (%d):" % len(self.checkedProposals))
        for p in self.checkedProposals:
           self.write("    %s" % p)
        numConflicts = 0   
        for pcode in sorted(self.conflicts.keys()):
            pconflict = self.conflicts[pcode]
            self.write('')
            self.write("Sources Found in other Proposals for %s: (%d)" % \
                (pcode, len(pconflict['conflicts'])))
            self.write("    Lowest Rx: %s, Search Radius ('): %s" % \
                (pconflict['lowestRx']
               , rad2arcMin(pconflict['searchRadius'])))
            numConflicts += len(pconflict['conflicts'])    
            for c in pconflict['conflicts']:
                self.write("    Target: %s; Checked: %s; Prop: %s; Dist. ('): %s; Level: %d"\
                    % (c['targetSrc'].target_name
                     , c['searchedSrc'].target_name
                     , c['searchedProp'].pcode
                     , rad2arcMin(c['distance'])
                     , c['level']))
        
        self.write("")
        self.write("Found %d individual source conflicts" % numConflicts)
        self.write("Number of distances that could not be calculated: %d" % len(self.badDistances))

    def write(self, line):
        # anything fancy?  nope ...
        print line

        
if __name__ == '__main__':
    semester = '12B'
    sc = SourceConflicts(semester = semester, quiet = False)
    sc.findConflicts()
    sc.report()
            

