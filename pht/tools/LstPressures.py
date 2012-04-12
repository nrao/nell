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

from datetime import date, datetime, timedelta
from utilities import SLATimeAgent as sla
from utilities import TimeAgent
from utilities import AnalogSet
from utilities import TimeAccounting

from pht.utilities    import *
from pht.models       import *
from scheduler.models import Observing_Type
from scheduler.models import Period as DSSPeriod
from scheduler.models import Semester as DSSSemester
from pht.tools.Sun    import Sun
from pht.tools.LstPressureWeather import LstPressureWeather
from pht.tools.LstPressureWeather import Pressures

import numpy

class LstPressures(object):

    """
    From Toney Minter:

    Calculating the LST pressure for a session
------------------------------------------

T_semster is the time in a session that is proposed to be observed in
the semester in question.  Note that some sessions, such as monitoring
project sessions, will have their time split between different semesters.

The LST range 0.0-23.99999... will be broken into a number (N) of
equal length segments.  The ith segment is given by T_i.  This
represents the total amount of time the session will need in segment i.
There will also be two weights given by w_i and f_i.

1) Minimum and maximum LST range.  This must take into account minimum 
elevation and users specified LST restrictions.  (LST exclusion will enter 
below.)  For a fixed time sessions the UT date and time range will be 
converted in the minimum LST (start time) and maximum LST (stop time).  

The calculation of the LST range can not be made automatically as 
observers sometimes list restrictions in the text of the proposal, 
the sources in the session can be changed (during session editing or as
a result of TAC decisions) , different observations can require different 
elevation restrictions, etc.  The minimum and maximum LST range should be 
obtained from the GB PHT tool.

2) Within minimum and maximum LST set w_i=1.0.  Outside the minimum and
maximum LST set w_i=0.0.

3) If there is an LST exclusion then set w_i=0.0 if the ith segment
is in the exclusion.

The LST exclusions are for night time (observing only from sunset to
sunrise), thermal nighttime (three hours after sunset to sunrise) and
RFI night time (from 8:00 pm to 8:00 am local time).  The sunrise and
sunset times for the GBT (location given in the GBT Proposer's Guide)
must be calculated for each day in the semester when these flags are
to be used.  The change between EDT/EST will have to be handled correctly
also.

4) If any flags are set (thermal night, rfi night, daylight night) then
we must calculate the fraction of time that a given LST segment meets
those criteria during the semester.  This will give f_i with f_i being
between 0 and 1.  If there are no flags set then f_i=1.0.
For example if 65 of 180 days meet the flag conditions for the ith LST
segment then f_i=65/180=0.3611....

5) Now calculate T_i using

T_i = [ (T_semester) * w_i * f_i ] / [ Sum_j (w_j * f_j) ]
    """
        

    def __init__(self, carryOverUseNextSemester = True):

        self.hrs = 24
        self.bins = [0.0]*self.hrs

        # when calculating carry over, use the next semester field,
        # OR the current time remaining?
        self.carryOverUseNextSemester = carryOverUseNextSemester


        # for computing pressures based on weather type, on 
        # holding these results
        self.weather = LstPressureWeather()

        # for reporting
        self.badSessions = []
        self.noPeriods = []
        self.noGrades = []
        self.carryoverSessions = []
        self.carryoverSessionPeriods = []
        self.pressuresBySession = {}
        self.pressures = [] 

        # for computing day light hours
        self.sun = Sun()
        
        # what example year do we compute flags for?
        self.year = 2012

        self.nextSemester = DSSSemester.getFutureSemesters()[0]
        self.nextSemesterStart = self.nextSemester.start()
        self.nextSemesterEnd   = self.nextSemester.end()

        # TBF: get from DB?
        self.grades = ['A', 'B', 'C']
        self.weatherTypes = ['Poor', 'Good', 'Excellent']

        self.initPressures()
        self.initFlagWeights()


    def newHrs(self):
        return numpy.array([0.0]*self.hrs)

    def initPressures(self):
        # init our buckets:
        # This is *everything* 
        self.totalPs  = numpy.array([0.0]*self.hrs)

        # Stuff left over from previous semester's, and the
        # next semesters committed time to maintenance, testing etc.
        self.carryoverTotalPs = numpy.array([0.0]*self.hrs)
        self.carryoverPs = Pressures() 

        # Available time for the semester - carryover
        self.remainingTotalPs = self.newHrs()
        self.remainingPs = Pressures()

        # The new stuff that people have submitted proposals for,
        # before having been allocated time
        self.requestedTotalPs = numpy.array([0.0]*self.hrs)
        self.requestedPs = Pressures() 

        # The new stuff htat people have submitted proposal for,
        # AFTER they've been allocated time.
        self.newAstronomyTotalPs = numpy.array([0.0]*self.hrs)
        self.gradePs = { 'A' : Pressures()
                 , 'B' : Pressures()
                 , 'C' : Pressures()
                 }


    def computeThermalNightWeights(self, numDays = 365, month = 1):
        "Computes the weights for the PTCS night time flag,"
        return self.computeRiseSetPressure(self.sun.getPTCSRiseSet
                                         , numDays = numDays
                                         , month = month)
       
    def computeOpticalNightWeights(self, numDays = 365, month = 1):
        "Computes the weights for the optical flag,"
        return self.computeRiseSetPressure(self.sun.getRiseSet
                                         , numDays = numDays
                                         , month = month)
   
    def computeRiseSetPressure(self, riseSetFn, numDays = 365, month = 1):
        "Computes the weights for a time of day constraint."
        # when is daytime for each day of the year? UTC?
        exCnt = [0]*24
        start = date(self.year, month, 1)
        for days in range(numDays):
            # when is day light for this day, UTC? 
            dt = start + timedelta(days = days)
            # use the given function to compute rise/set for this day
            r, s =riseSetFn(dt) 
            # LSTs for these UTC datetimes?
            minLst = sla.Absolute2RelativeLST(r) 
            maxLst = sla.Absolute2RelativeLST(s)
            # what bins do those fall into?
            minHr = int(math.floor(minLst))
            maxHr = int(math.floor(maxLst))
            if minHr > maxHr:
                ex = [(0,maxHr), (minHr, 24)]
            else:
                ex = [(minHr, maxHr)]
                
            # now tally up the LST bins that get excluded    
            for s, e in ex:
                for h in range(s,e):
                    exCnt[h] += 1
        # finally convert these counts to weights
        weights = [e/float(numDays) for e in exCnt]
        return (weights, exCnt)

    def computeRfiWeights(self, numDays = 365, month = 1):
        return self.computeRiseSetPressure(self.getRfiRiseSet
                                         , numDays = numDays
                                         , month = month)

    def getRfiRiseSet(self, date):
        "Gives the time high RFI start and ends for the given date."

        # DSS definition says this is between 8 AM - 8 PM EST.
        # Takes into account DST
        rise = datetime(date.year, date.month, date.day, 8)
        set  = datetime(date.year, date.month, date.day, 20)
        rise = TimeAgent.est2utc(rise)
        set  = TimeAgent.est2utc(set)
        return (rise, set)


        # convert this to UT
        
    def getLstWeightsForSession(self, session):
        "Simple: LST's within min/max are on, rest are off."
        ws = self.newHrs() #[0.0] * self.hrs
        minLst = int(math.floor(rad2hr(session.target.min_lst)))
        maxLst = int(math.floor(rad2hr(session.target.max_lst)))
        if (0 > minLst or minLst > 24.0) or (0 > maxLst or maxLst > 24.0):
            print "Illegal LST min/max: ", minLst, maxLst, session
            return ws
        # wrap around?
        if minLst > maxLst:
            ons = [(0, maxLst), (minLst, self.hrs)]
        else:
            ons = [(minLst, maxLst)]
        for minLst, maxLst in ons:
            for b in range(minLst, maxLst):
                ws[b] = 1.0
        return ws

    def modifyWeightsForLstExclusion(self, session, ws):
        "Modify given weights to be zero within the exclusion."
        # save some time if they don't even have this set
        if not session.has_lst_exclusion():
            return ws
        lstRanges = session.get_lst_parameters()
        exclusions = lstRanges['LST Exclude']
        for lowEx, hiEx in exclusions:
            lowEx = int(math.floor(lowEx))
            hiEx = int(math.floor(hiEx))
            for b in range(lowEx, hiEx):
                ws[b] = 0.0
        return ws

    def getFlagWeightsForSession(self, session):
        "Different flags affect LST pressure differently."

        fs = [1.0]*self.hrs
        if session.flags.thermal_night:
            fs = fs * self.thermalNightWeights 
        elif session.flags.optical_night:
            fs = fs * self.opticalNightWeights  
        elif session.flags.rfi_night:
            fs = fs * self.rfiWeights 
        return fs

    def useCarryOverPeriods(self, session):
        """
        We figure out the carry over for Maintenance
        and Shutdown sessions from their periods.
        """

        # TBF: needs improvement
        pcodes = ['Maintenance', 'Shutdown']
        return session.proposal.pcode in pcodes

    def getPressuresFromSessionsPeriods(self, session):
        """
        We figure out the carry over for Maintenance
        and Shutdown sessions from their periods.
        """
        periods = self.getSessionNextSemesterPeriods(session)
        return self.getPressuresFromPeriods(periods)

    def getPressuresFromPeriods(self, periods):    
        total = self.newHrs() 
        for period in periods:
            ps = self.getPressuresFromPeriod(period)
            total += ps 
        return total

    def getSessionNextSemesterPeriods(self, session): 
        """
        A session that has periods for the next semester should
        be either fixed, windowed, or elective.  For fixed,
        all periods count; for windowed, default periods 
        count, but they should be the only one's setup.
        Handle electives distinctly.
        """
        if session.dss_session.session_type.type == 'elective':
            periods = self.getElectiveSessionPeriods(session)
        else:
            periods = self.getSessionPeriods(session)
        # for reporting
        if len(periods) == 0:
            self.noPeriods.append(session)
        else:
            self.carryoverSessionPeriods.append(session)
        return periods    

    def getElectiveSessionPeriods(self, session):
        """
        Only one period per elective will probably get 
        scheduled, so arbitrarily choose one.
        """
        # only look at electives in our time range
        es = [e for e in session.dss_session.elective_set.all() \
            if len(e.periods.exclude(state__abbreviation = 'D')) > 0 and \
            e.getRange()[0] < self.nextSemesterEnd and \
            e.getRange()[1] > self.nextSemesterStart]

        # just get the first period    
        ps = [e.periods.exclude(state__abbreviation = 'D')[0] \
            for e in es]
        return ps

    def getSessionPeriods(self, session):
        #assert session.session_type.type != 'Elective'
        return DSSPeriod.objects.filter( \
            session = session.dss_session
          , start__gt = self.nextSemesterStart
          , start__lt = self.nextSemesterEnd).exclude( \
              state__name = 'Deleted').order_by('start') 

    def getPressuresFromPeriod(self, period):
        """
        In a way, a much simpler calculation then
        figuring out pressure from a session.  Here
        we know exactly what LST hours are getting
        blocked.
        """

        ps = [0.0] * self.hrs

        start = period.start
        dur   = period.duration
        end   = period.end()
        
        # convert local time range to LST range
        lstStart = sla.Absolute2RelativeLST(start)
        lstEnd = sla.Absolute2RelativeLST(end)

        # how does this overlap with 24 hours?
        if lstStart > lstEnd:
            ex = [(0,lstEnd), (lstStart, 24)]
        else:
            ex = [(lstStart, lstEnd)]

        # convert this to the fraction of each 24 hour
        # bin covered by the period
        for hr in range(self.hrs):
            for s, e in ex:
                # we add to the pressure only if this
                # hour is in the periods range
                if AnalogSet.overlaps((hr, hr+1), (s, e)):
                    # by how much?
                    if hr >= s and hr+1 < e:
                        # the whole thing
                        ps[hr] = 1.0
                    elif hr < s and (hr+1) > s:
                        ps[hr] = (hr+1) - s
                    else:
                        ps[hr] = e - hr
            
        return ps 


    def getPressuresForSession(self, session, carryover = False):
        """
        Take into account different attributes of given session
        to return it's LST Pressure at each LST (0..23)
        """
        
        # first, is this session setup so we can do this?
        if session.target is None or session.allotment is None \
            or session.target.min_lst is None \
            or session.target.max_lst is None:
            self.badSessions.append(session)
            return [0.0] * self.hrs

        # TBF: is this right?
        # Carryover we get the time differently
        if carryover:
            # how is carryover to be added to?
            if self.carryOverUseNextSemester:
                totalTime = 0.0
                if session.next_semester is not None \
                    and session.next_semester.complete == False:
                    totalTime = session.next_semester.time
            else:
                ta = TimeAccounting()
                totalTime = ta.getTimeRemaining(session.dss_session)
            # reporting
            self.carryoverSessions.append(session)
        else:    
            # allocated or requested time?
            if session.allotment.allocated_time is not None:
                totalTime = session.allotment.allocated_time
            else:
                totalTime = session.getTotalRequestedTime()

        hrs = 24
        bins = [0.0] * hrs 
        w = [0.0] * hrs
        f = [1.0] * hrs
        
        ws = self.getLstWeightsForSession(session)

        # now take into account LST exclusion
        ws = self.modifyWeightsForLstExclusion(session, ws)

        # now look at the flags
        fs = self.getFlagWeightsForSession(session)

        # put it all togethor to calculate pressures
        weightSum = sum(ws * fs)
        if weightSum != 0:
            ps = [(totalTime * ws[i] * fs[i]) / weightSum \
                for i in range(self.hrs)]
        else:
            ps = [0.0]*self.hrs

        return numpy.array(ps)    

    def getPressures(self, sessions = None):
        """
        Returns a dictionary of pressures by LST for different 
        categories.  This format is specified to easily convert
        to the format expected by the web browser client (Ext store).
        For example:
        [
         {'LST': 0.0, 'total': 2.0, 'A': 1.0, 'B': 1.0},
         {'LST': 1.0, 'total': 3.0, 'A': 2.0, 'B': 1.0},
        ]
        """
        
        self.initPressures()

        # what sessions are we doing this for?
        if sessions is None:
            sessions = Session.objects.all().order_by('name')

        # fill the buckets
        for s in sessions:
            carryover = s.dss_session is not None
            if self.useCarryOverPeriods(s):
                ps = self.getPressuresFromSessionsPeriods(s)
            else:
                ps = self.getPressuresForSession(s, carryover)

            # accum pressure in total 
            self.totalPs += ps
            # for reporting
            self.pressuresBySession[s.name] = (carryover, ps, sum(ps))
            # We really keep carryover separate
            # Also track carryover by weather type
            if carryover:
                self.carryoverTotalPs += ps
                self.carryoverPs += self.weather.binSession(s, ps)
            else:
                if s.allotment.allocated_time is not None: 
                    self.newAstronomyTotalPs += ps
                    wps = self.weather.binSession(s, ps)
                    if s.grade is not None:
                        grade = s.grade.grade
                        self.gradePs[grade] += wps
                    else:    
                        # for reporting    
                        self.noGrades.append(s)    
                else:
                    # this goes into the requested bucket
                    self.requestedTotalPs += ps
                    self.requestedPs += self.weather.binSession(s, ps)

        # now figure out the availability        
        changes = self.weather.getAvailabilityChanges(self.gradePs['A'])
        self.gradePs['A'] += changes

        # What's *really* available for this semester?
        self.remainingTotalPs = self.weather.availabilityTotal - \
            self.carryoverTotalPs
        self.remainingPs = self.weather.availability - self.carryoverPs
            

        # now convert the buckets to expected output
        return self.jsonDict()

    def jsonDict(self):
        """
        Convert our numpy arrays to the format expected by the client:
        A list of dictionaries, where LST is a key.
        """
       
        output = []
        for i in range(self.hrs):
            # init the dictionary with the simple stuff, including LST
            lstDict = dict(LST = i
                         , Total = self.totalPs[i] 
                         , Available = self.weather.availabilityTotal[i]
                         , Carryover = self.carryoverTotalPs[i] 
                         , Requested = self.requestedTotalPs[i] 
                          )
            # now add in the weather details              
            for weather in self.weatherTypes: 
                # availability
                availType = "Available_%s" % weather
                lstDict[availType] = self.weather.availability.getType(weather)[i]
                # carry over
                carryoverType = "Carryover_%s" % weather
                lstDict[carryoverType] = self.carryoverPs.getType(weather)[i]
                # requested
                requestedType = "Requested_%s" % weather
                lstDict[requestedType] = self.requestedPs.getType(weather)[i]

                # new astronomy is further subdivied by grade
                for grade in self.grades: 
                    type = "%s_%s" % (weather, grade)
                    lstDict[type] = self.gradePs[grade].getType(weather)[i]
            output.append(lstDict)
           
        self.pressures = output   
        return output        

    def almostEqual(self, xs, ys):
        "Two numpy arrays are almost equal?"
        eps = 0.001
        return abs(sum(xs) - sum(ys)) < eps

    def checkPressures(self):
        "Bookeeping should be self-consistent"

        msgs = []
        # total total
        total = self.carryoverTotalPs + self.newAstronomyTotalPs + \
            self.requestedTotalPs
        if not self.almostEqual(self.totalPs, total):
            msgs.append("Total Pressure ! = Carryover Total + New Astro. Total")  


        # carryover
        totalCarryover = numpy.array([0.0]*self.hrs)
        for w in self.weatherTypes:
            totalCarryover += self.carryoverPs.getType(w)
        if not self.almostEqual(totalCarryover, self.carryoverTotalPs):
            msgs.append("Total Carry Over != All Weather Types")
        
        # new astronomy requested
        totalRequested = self.newHrs() #numpy.array([0.0]*self.hrs)
        for w in self.weatherTypes:
            totalRequested += self.requestedPs.getType(w)
        if not self.almostEqual(totalRequested, self.requestedTotalPs):
            msgs.append("Total Requested != All Weather Types")

        # new astronomy allocated
        totalNewAstro = numpy.array([0.0]*self.hrs)
        for g in self.grades:
            for w in self.weatherTypes:
                totalNewAstro += self.gradePs[g].getType(w)
        if not self.almostEqual(totalNewAstro, self.newAstronomyTotalPs):
            msgs.append("New Astro. Total != All Weather/Grade Types")

        return (len(msgs) == 0, msgs)

    def report(self):
        "Report on pressure results - mostly for debugging."
        
        print self.formatResults('Total', self.totalPs)

        self.reportPressures("Availability"
                           , self.weather.availabilityTotal
                           , self.weather.availability)
        
        self.reportPressures("Carryover"
                           , self.carryoverTotalPs
                           , self.carryoverPs)
        
        self.reportPressures("Remaining"
                           , self.remainingTotalPs
                           , self.remainingPs)

        self.reportPressures("Requested"
                           , self.requestedTotalPs
                           , self.requestedPs)
        
        print ""
        print "Next Semester Astromony: "
        print self.formatResults("      Total" 
                               , self.newAstronomyTotalPs)
        for w in self.weatherTypes:
            print "    %s" % w
            for g in self.grades:
                print self.formatResults("      %s_%s" % (w, g)
                                       , self.gradePs[g].getType(w))

        # warnings
        valid, msgs = self.checkPressures()
        if not valid:
            print ""
            print "WARNINGS: "
            for m in msgs:
                print m 

        # more debugging
        print ""
        print "Carry over sessions: %d" % len(self.carryoverSessions)
        for s in self.carryoverSessions:
            print "    ", s, s.weather_type
        print "Carry over sessions w/ periods: %d" % \
            len(self.carryoverSessionPeriods)
        for s in self.carryoverSessionPeriods:
            print "    ", s, s.weather_type
        print "No Periods for Sessions: %d" % len(self.noPeriods)
        for s in self.noPeriods:
            print "    ", s
        print "Sessions counted towards astronomy w/ out grades: %d" % len(self.noGrades)    
        for s in self.noGrades:
            print "    ", s
        print "Bad Sessions: %d" % len(self.badSessions)
        for b in self.badSessions:
            print "    ", b

        # everybodies pressure!
        print ""
        print "Pressures by Session: "
        for k in sorted(self.pressuresBySession.keys()):
            carryover, ps, total = self.pressuresBySession[k]
            lbl = "%s (%s, %5.2f)" % (k, carryover, total)
            print self.formatResults(lbl, ps, lblFrmt = "%35s")
        print ""
        print "Non-Zero Pressures by Session: "
        for k in sorted(self.pressuresBySession.keys()):
            carryover, ps, total = self.pressuresBySession[k]
            if sum(ps) > 0.0:
                lbl = "%s (%s, %5.2f)" % (k, carryover, total)
                print self.formatResults(lbl, ps, lblFrmt = "%35s")

        # for Brian Truitt:
        print "Remaining Hours by LST (0-23)"
        for r in self.remainingTotalPs:
            print "%5.2f" % r

    def reportPressures(self, label, total, wTypes):
        "Report on pressures and how they break down by weather."
        print ""
        print "%s: " % label 
        print self.formatResults('    Total', total)
        for w in self.weatherTypes:
            print self.formatResults('    %s' % w, wTypes.getType(w))

    def formatResults(self, label, results, lblFrmt = "%18s"):
        label = lblFrmt % label
        rs = ["%7.2f" % results[i] for i in range(len(results))]
        return label + ": " + ' '.join(rs)
            

    def initFlagWeights(self):

        # TBF: These get computed by methods in this class,
        # but no need to do it at start up every time.
        self.thermalNightWeights = numpy.array([0.61643835616438358
                          , 0.61369863013698633
                          , 0.61095890410958908
                          , 0.61369863013698633
                          , 0.61369863013698633
                          , 0.61643835616438358
                          , 0.61917808219178083
                          , 0.61643835616438358
                          , 0.61643835616438358
                          , 0.61643835616438358
                          , 0.61643835616438358
                          , 0.61369863013698633
                          , 0.61643835616438358
                          , 0.62191780821917808
                          , 0.62739726027397258
                          , 0.64383561643835618
                          , 0.66301369863013704
                          , 0.68493150684931503
                          , 0.70136986301369864
                          , 0.70136986301369864
                          , 0.68219178082191778
                          , 0.66027397260273968
                          , 0.63835616438356169
                          , 0.62465753424657533
                          ])
        self.opticalNightWeights = numpy.array([0.50958904109589043
                            , 0.51232876712328768
                            , 0.51232876712328768
                            , 0.51506849315068493
                            , 0.51506849315068493
                            , 0.51780821917808217
                            , 0.51780821917808217
                            , 0.51780821917808217
                            , 0.51506849315068493
                            , 0.51506849315068493
                            , 0.51506849315068493
                            , 0.51232876712328768
                            , 0.51232876712328768
                            , 0.50958904109589043
                            , 0.50684931506849318
                            , 0.50684931506849318
                            , 0.50410958904109593
                            , 0.50136986301369868
                            , 0.50136986301369868
                            , 0.50136986301369868
                            , 0.50136986301369868
                            , 0.50410958904109593
                            , 0.50684931506849318
                            , 0.50958904109589043
                            ])
        self.rfiWeights     = numpy.array([0.54246575342465753
                             , 0.54520547945205478
                             , 0.54520547945205478
                             , 0.54246575342465753
                             , 0.54246575342465753
                             , 0.54246575342465753
                             , 0.50136986301369868
                             , 0.50136986301369868
                             , 0.50136986301369868
                             , 0.48493150684931507
                             , 0.46027397260273972
                             , 0.45753424657534247
                             , 0.46027397260273972
                             , 0.46027397260273972
                             , 0.46027397260273972
                             , 0.46027397260273972
                             , 0.45753424657534247
                             , 0.46301369863013697
                             , 0.50136986301369868
                             , 0.50136986301369868
                             , 0.49863013698630138
                             , 0.51780821917808217
                             , 0.54246575342465753
                             , 0.54246575342465753
                             ]) 
            


if __name__ == '__main__':
    lst = LstPressures()
    ps = lst.getPressures()
    lst.report()

    #exp = []
    #eps = 0.001
    #for i in range(len(ps)):
    #    keys = ps[i].keys()
    #    for k in keys:
    #        if not (abs(exp[i][k] - ps[i][k]) < eps):
    #            print "Lst: %f, Key: %s" % (i, k)
    #            print exp[i][k]
    #            print ps[i][k]
    #        assert abs(exp[i][k] - ps[i][k]) < eps


