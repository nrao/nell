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

from pht.models import *
from LstPressures import LstPressures
from LstPressureWeather import Pressures

import numpy
import time
import sys

ALLOCATED = 'allocated'
REQUESTED = 'requested'

class NraoPhtPressures(object):

    """
    Responsible for preparing pressures for NRAO PHT's pressure plot.
    Also contains methods for testing that we can use this product we
    are supplying them to get the correct plots.
    """

    def __init__(self):

        self.lst = LstPressures(adjustWeatherBins = False)

        # TBF: unsued
        all = 'All'
        self.grades = [all, 'A', 'B', 'C']
        self.weatherTypes = [all, 'Poor', 'Good', 'Excellent']
        self.types = [all, 'R', 'T', 'L']

    def getNraoPhtSessions(self, sessFltr = None, pcodeFltr = None, gradeFltr = None, ptypeFltr = None):
        "We don't need to calculate pressures for ALL the sessions in our DB"

        # use the different filters to figure out the minimum query:
        # session filter wins out
        if sessFltr is not None:
            ss = [Session.object.get(id = sessFltr)]
        else:
            # now, find just requested and allocated
            # make sure you don't pick up:
            #    * ignored sessions cause of bad target objects
            #    * sponsored proposals
            querySet = Session.objects.filter(semester__semester = self.lst.nextSemester.semester).exclude(target = None).exclude(target__min_lst = None).exclude(target__max_lst = None).order_by('id')
            if pcodeFltr is not None:
                querySet = querySet.filter(proposal__pcode = pcodeFltr)
            if gradeFltr is not None:
                querySet = querySet.filter(grade__grade = gradeFltr)
            if ptypeFltr is not None:
                querySet = querySet.filter(proposal__proposal_type__type = ptypeFltr)
            ss = querySet.order_by('id')

            # but remember, we have to filter out the sponsored sessions
            ss = [s for s in ss if not s.proposal.isSponsored()]

        # now figure out which of these sessions are part of the subset
        # that even gets plotted by the NRAO PHT:
        print len(ss)
        st = time.time()
        ss = [s for s in ss if self.lst.getSessionCategories(s)[0] in [ALLOCATED, REQUESTED]]
        e = time.time()
        print "time for cats: ", e - st
        print len(ss)

        #ps = self.lst.getPressures(sessions = ss)
        return ss

    def getNraoPhtPressures(self
                   , grade = None
                   , weatherType = None
                   , ptype = None
                   , pcode = None):

        ss = self.getNraoPhtSessions(gradeFltr = grade
                                   , pcodeFltr = pcode
                                   , ptypeFltr = ptype
                                     )
        self.lst.getPressures(sessions = ss)                             
        # TBF: convert this to JSON
        return self.lst.weatherPsBySession

    def testGetNraoPhtPressures(self
                   , grade = None
                   , weatherType = None
                   , ptype = None
                   , pcode = None):

        """Test method: see if we can use our list of pressures to produce their plot"""

        # TBF: assert options choosen
        
        # Make this code run a lot faster when a specific proposal has been choosen 
        #if pcode is not None:
        #    ss = Session.objects.filter(proposal__pcode = pcode)
        #    self.lst.getPressures(ss)
        #else:
        #    self.lst.getPressures()

        ss = self.getNraoPhtSessions(gradeFltr = grade
                                   , pcodeFltr = pcode
                                   , ptypeFltr = ptype
                                     )
        self.lst.getPressures(sessions = ss)                             
        ps = self.lst.weatherPsBySession

        # Okay, here's our proof of concept:

        # before we do anything, see if we need to worry about
        # adjustments to Grade A time across weather types
        HRS = 24
        allocatedPs = dict(A = numpy.zeros(HRS)
                         , B = numpy.zeros(HRS)
                         , C = numpy.zeros(HRS))
        requestedPs = numpy.zeros(HRS)
        # we need to take all grade A pressures into account because
        # we have to adjust across weather types
        if grade is None or grade == 'A':
            nonFilteredGradeA = Pressures()
            lst2 = LstPressures()
            lst2.getPressures()
            carryover = lst2.carryoverPs
            availability = lst2.weather.availability

        # iterate throught the info store per session
        for sessHandle in sorted(ps.keys()):
            cat, sessPcode, sessPtype, gr, wps = ps[sessHandle]
            # effecitvely filter by grade and other things
            if cat == ALLOCATED and gr is not None:
                if (pcode is None or pcode == sessPcode) \
                  and (grade is None or gr == grade) \
                  and (ptype is None or sessPtype == ptype):
                    if gr == 'A':
                        nonFilteredGradeA += wps
                    # filter by weather
                    if weatherType is not None:
                        allocatedPs[gr] += wps.getType(weatherType)
                    else:
                        allocatedPs[gr] += wps.allTypes()
            if cat == REQUESTED:
                # requested pressures disapper when filtering by grade
                if (pcode is None or pcode == sessPcode) \
                  and (ptype is None or sessPtype == ptype) \
                  and grade is None:
                    # filter by weather
                    if weatherType is not None:
                        requestedPs += wps.getType(weatherType)
                    else:
                        requestedPs += wps.allTypes()

        if grade is None or grade == 'A':
            # TBF: we need to use a cache of the availability and carryover
            # like they will in Socorro
            lst2 = LstPressures()
            lst2.getPressures()
            carryover = lst2.carryoverPs
            availability = lst2.weather.availability
            print 'carryover: ', carryover
            print 'available: ', availability
            print "original: ", allocatedPs['A']
            print "nonFiltered: ", nonFilteredGradeA

            newGrA, changes = self.lst.adjustForOverfilledWeather(nonFilteredGradeA
                                              , carryover
                                              , availability)

            print "changes: ", changes
            print "new: ", newGrA

        #    adjustedAllocated, adjustments = self.lst.adjustForOverfilledWeather(
        #        nonFilteredGradeA
        #      , self.lst.carryoverPs
        #      , self.lst.weather.availability
        #     )                
        #print "adjusted: ", adjustedAllocated    
        #print "adjustments: ", adjustments


        return (allocatedPs, requestedPs)
        
            
if __name__ == '__main__':

    # TBF: this is basically working, but:
       # we aren't doing adjustments yet, for which we need the carryover & availability
       # we can improve performance by caching carryover & availability, and only calculating pressures ALLOCATED & REQUESTED

    
    nrao = NraoPhtPressures()

    #allocated, unscheduled = nrao.getPressures(pcode = 'GBT14A-025')
    wtype = 'Poor'
    #allocated, unscheduled = nrao.getPressures(weatherType = None, grade = 'C')
    #allocated, unscheduled = nrao.getPressures(ptype = 'Large')
    s = time.time()
    #allocated, unscheduled = nrao.getNraoPhtPressures(ptype = 'Regular',  weatherType = 'Poor')
    allocated, unscheduled = nrao.getNraoPhtPressures()
    e = time.time()
    print "elapsed time: ", e - s
    #sys.exit(1) 
    
    for g in ['A', 'B', 'C']:
        print g
        print allocated[g]
        print "VS:"
        print nrao.lst.gradePs[g].allTypes() #getType(wtype) #allTypes()
        print "diff: ",  allocated[g] - nrao.lst.gradePs[g].allTypes() #getType(wtype) #allTypes()
    print "unscheduled: "    
    print unscheduled
    print "vs."
    print nrao.lst.requestedPs.allTypes()
    print "diff: ",  unscheduled -  nrao.lst.requestedPs.allTypes() #getType(wtype) #allTypes()



            


