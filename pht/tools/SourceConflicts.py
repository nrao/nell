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
import copy

class SourceConflicts(object):

    def __init__(self, semester = None, quiet = True, now = None):

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

        self.now = now

        # caches
        self.includeProposals = {}

    def setSemester(self, semester):
        self.semester = semester

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

        if not self.quiet:
            print "Searching %d proposals in %d other proposals." % (len(proposals), len(allProposals))

        # start checking
        for p in proposals:
            if not self.quiet:    
                print "Checking: %s, # srcs: %d" % (p.pcode, len(p.source_set.all()))
            self.findConflictsForProposal(p, allProposals)

    def findConflictsForProposal(self, proposal, allProposals):

        # init the results
        lowestRx = self.getLowestRcvr(proposal)


        if lowestRx is None:
            print "skipping findConflictsForProposal (lowestRx is None) for ", proposal
            return 

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
                passesInc =  self.passesInclusionCheck(searchedProp, now = self.now)
                try:
                    d = self.getAngularDistance(trgSrc, srchSrc)
                    if d <= searchRadius and passesInc: 
                        conflict = True
                        srcConflict = {'targetSrc' : trgSrc
                                     , 'searchedSrc' : srchSrc
                                     , 'searchedProp' : searchedProp
                                     , 'distance' : d
                                     , 'level' : 0
                        }
                        self.conflicts[tpcode]['conflicts'].append(srcConflict)
                except:
                    if not self.quiet:
                        print "could not calc distance"
                    srcConflict = {'targetSrc' : trgSrc
                                 , 'searchedSrc' : srchSrc
                                 , 'searchedProp' : searchedProp
                    }
                    self.badDistances.append(srcConflict)
                if conflict:
                    lastObsDate, proprietaryPeriod = self.withinProprietaryDate(searchedProp, targetProp)
                    self.conflicts[tpcode]['conflicts'][-1]['lastObsDate'] = lastObsDate
                    # see if it's even worse - check the other levels
                    if self.hasSameRcvrConflict(targetProp, searchedProp):
                        self.conflicts[tpcode]['conflicts'][-1]['level'] = 1
                        # check the next level - proprietary period!
                        if proprietaryPeriod:
                            self.conflicts[tpcode]['conflicts'][-1]['level'] = 2
                            
    def filterConflicts(self, level):
        self.filteredConflicts = {}
        for k, v in self.conflicts.iteritems():
            self.filteredConflicts[k] = copy.copy(self.conflicts[k])
            self.filteredConflicts[k]['conflicts'] = [c for c in self.conflicts[k]['conflicts'] if level <= c['level']]

    def hasSameRcvrConflict(self, targetProp, searchedProp):
        """
        This couldn't be simpler: compare the union of the 
        receivers used at the proposal level.
        """
        targetRcvrs = Set(list(targetProp.bands()))
        searchedRcvrs = Set(list(searchedProp.bands()))
        return len(list(targetRcvrs.intersection(searchedRcvrs))) > 0

    def getMaxGrade(self, proposal):
        """
        The order of the grades (from maximum to minimum is)
        A
        B
        C
        H
        Blank
        N
        N*
        W 
        """
        grades = sorted(list(set([s.grade.grade if s.grade is not None else '' \
            for s in proposal.session_set.order_by('grade')])))
        # this should return order of ['', 'A', 'B', 'C', 'H', 'N', 'N*', 'W']
        # so, we need to get that '' in the right spot
        if len(grades) == 0:
            return None
        elif len(grades) == 1:
            return grades[0]
        else:
            if '' not in grades:
                # no blank grade to worry about
                return grades[0]
            else:
                if 'A' in grades or 'B' in grades or 'C' in grades or 'H' in grades:
                    # if it's one of the higher ones, pick it as the max
                    return grades[1]
                else:
                    # all the other's are below it, so '' is the max
                    return grades[0]

    def getLastObsDate(self, prop):
        "Returns (date that this proposal/project last observed, list of obs. periods)"

        none = (None, [])
        if prop is None:
            return none

        if prop.dss_project is None:
            return none

        ps = prop.dss_project.get_observed_periods()
        lps = len(ps)
 
        if lps == 0:
            return none
        elif lps == 1:
            return (ps[0].start, ps)
        else:
            # don't trust the sort order!!!
            # the last observed date is either the first, or last!
            dt1 = ps[0].start
            dt2 = ps[lps-1].start
            if dt1 > dt2:
                return (dt1, ps)
            else:
                return (dt2, ps)

    def passesInclusionCheck(self, searchedProp, now = None):
        """
        #1: If maximum grade is N, N* or W then ignore (never observed).
        #2: If last observed date is more than 1 year ago (today - 1 year) then ignore
        (proprietary period is over).
        #3: If last observed date is blank and the grade is B or C and the project is
        marked as complete then ignore (project never observed).
        #4: If project passes above checks then there is a potential conflict - keep it.
        """
        
        # use a cache!
        pcode = searchedProp.pcode
        if self.includeProposals.has_key(pcode):
            return self.includeProposals[pcode]

        if now is None:
            now = datetime.now()
        else:
            now = self.now

        # get grades, but DONT ignore non-graded sessions
        maxGrade = self.getMaxGrade(searchedProp)
        
        # Rule #1
        ignoreGrades = ['W', 'N', 'N*']
        if maxGrade in ignoreGrades:
            self.includeProposals[pcode] = False
            return False

        last_obs_date, _ = self.getLastObsDate(searchedProp)

        # Rule #3
        if last_obs_date is None and maxGrade in ['B', 'C'] and searchedProp.dss_project is not None and searchedProp.dss_project.complete:
            self.includeProposals[pcode] = False
            return False 

        # Rule #2
        a_year_ago = now - timedelta(days = 365)
        if last_obs_date is not None and last_obs_date < a_year_ago:
            self.includeProposals[pcode] = False
            return False

        # we passed the above tests!
        self.includeProposals[pcode] = True
        return True

    def withinProprietaryDate(self, searchedProp, targetProp, now = datetime.now()):
        "Any observations within a year?"
        lastObsDate = None
        if searchedProp.dss_project is not None:
            lastObsDate, periods = self.getLastObsDate(searchedProp)
            refTime = now - timedelta(days = 365)
            periods     = [p for p in periods if p.start > refTime]
        else: 
            if searchedProp.semester == targetProp.semester:
                # same semester so cheat
                periods = ['a','b']
            else:    
                # No dss_project, no periods
                periods = []
        return lastObsDate, len(periods) > 0
                    
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
                self.write("    Target: %s; Checked: %s; Prop: %s; Dist. ('): %s; DeltaRa('): %s; DeltaDec ('): %s; Level: %d"\
                    % (c['targetSrc'].target_name
                     , c['searchedSrc'].target_name
                     , c['searchedProp'].pcode
                     , rad2arcMin(c['distance'])
                     , rad2arcMin(abs(c['targetSrc'].ra - c['searchedSrc'].ra))
                     , rad2arcMin(abs(c['targetSrc'].dec - c['searchedSrc'].dec))
                     , c['level']))
        
        self.write("")
        self.write("Found %d individual source conflicts" % numConflicts)
        self.write("Number of distances that could not be calculated: %d" % len(self.badDistances))

    def write(self, line):
        # anything fancy?  nope ...
        print line

        
if __name__ == '__main__':
    #semester = '12B'
    #sc = SourceConflicts(semester = semester, quiet = False)
    #sc.findConflicts()
    #sc.report()

            
    pc = 'GBT14A-093'
    pc2 = 'GBT13B-213'
    #from pht.models import *
    #from pht.tools.SourceConflicts import SourceConflicts
    sc = SourceConflicts()
    sc.quiet = False
    p1 = Proposal.objects.get(pcode = pc)
    p2 = Proposal.objects.get(pcode = pc2)
    sc.findConflictsForProposal(p1, [p2])

