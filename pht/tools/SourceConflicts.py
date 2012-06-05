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

from pht.models import *
from pht.utilities import *

class SourceConflicts(object):

    def __init__(self, semester = None):

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
        # and the level of the conflict
        self.conflicts = {}

    def initSearchRadi(self):
        "Map receivers to their Search Radi"

        self.hpbw = {
          'NS'  : 0.0 # TBF
        , 'Z'   : 0.0 # TBF
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
        , 'Hol' : 0.0 # TBF
        , 'K' : 0.830 # Ku?
        , 'KFPA' : 0.560
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
                proposals = Proposal.objects.filter(semester__semester = self.semester)
            else: 
                proposals = Proposal.objects.all().order_by('pcode')

        # which proposals to check against?
        if allProposals is None:
            allProposals = Proposal.objects.all().order_by('pcode')

        # start checking
        for p in proposals:
            self.findConflictsForProposal(p, allProposals)

    def findConflictsForProposal(self, proposal, allProposals):

        for p in allProposals:
            # don't check against one's self
            if p.id != proposal.id:
                self.findConflictsBetweenProposals(proposal, p)

    def findConflictsBetweenProposals(self, targetProp, searchedProp):
        """
        targetProp - the proposal that we use to determine the search rad
        searchedProp - checking srcs in targetProp against one's in here
        """

        #rad = self.getSearchRadius(targetProp)        
        lowestRx = self.getLowestRcvr(targetProp)
        rad = self.searchRadi.get(lowestRx.abbreviation, None)
        tpcode = targetProp.pcode
        # init the results
        self.conflicts[tpcode] = {'proposal' : targetProp
                                , 'lowestRx' : lowestRx
                                , 'searchRadius' : rad
                                , 'conflicts' : []
                                 }
        # now look for conflicts, source against source
        trgSrcs = targetProp.source_set.all().order_by('target_name')
        srchSrcs = searchedProp.source_set.all().order_by('target_name')
        for trgSrc in trgSrcs:
            for srchSrc in srchSrcs:
                d = self.getAngularDistance(trgSrc, srchSrc)
                if d <= rad:
                    srcConflict = {
                        'targetSrc' : trgSrc
                      , 'searchedSrc' : srchSrc
                      , 'searchedProp' : searchedProp
                      , 'distance' : d
                      , 'level' : 0
                    }
                    self.conflicts[tpcode]['conflicts'].append(srcConflict)


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
        

            

