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

# Session Categories
CARRYOVER = 'carryover'
ALLOCATED = 'allocated'
REQUESTED = 'requested'
IGNORED = 'ignored'

# Session sub-Categories
BADLST = 'bad_lst'
FUTURE = 'future'
SEMESTER = 'semester'
PERIODS = 'periods'
CARRYOVER_BAD_GRADE = 'carryover_bad_grade'
CARRYOVER_NO_DSS = 'carryover_no_dss'

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
        

    def __init__(self, carryOverUseNextSemester = True, today = None):

        self.hrs = 24
        self.bins = [0.0]*self.hrs

        # when calculating carry over, use the next semester field,
        # OR the current time remaining?
        self.carryOverUseNextSemester = carryOverUseNextSemester

        # for computing pressures based on weather type, on 
        # holding these results
        self.weather = LstPressureWeather()

        # for reporting
        self.sessions = []
        self.badSessions = []
        self.pressuresBySession = {}
        self.futureSessions = []
        self.semesterSessions = []
        self.pressures = [] 

        # for computing day light hours
        self.sun = Sun()
        
        if today is None:
            today = datetime.today()

        self.currentSemester = DSSSemester.getCurrentSemester(today = today)
        sems = DSSSemester.getFutureSemesters(today = today)
        self.nextSemester = sems[0]
        self.nextSemesterStart = self.nextSemester.start()
        self.nextSemesterEnd   = self.nextSemester.end()
        # TBF: need future semesters in DSSSemester DB:
        self.futureSemesters = [s.semester for s in sems][1:] 
        #['13A', '13B', '14A', '14B', '15A', '15B']

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
        # the sum of grades A, B, C
        self.newAstronomyGradeTotalPs = numpy.array([0.0]*self.hrs)
        self.gradePs = { 'A' : Pressures()
                 , 'B' : Pressures()
                 , 'C' : Pressures()
                 }
        self.originalGradePs = { 'A' : Pressures()
                               , 'B' : Pressures()
                               , 'C' : Pressures()
                               }

        # for holding what to do with overfilled weather bins
        self.changes = Pressures()


    def computeThermalNightWeights(self, start = None, numDays = None): 
        "Computes the weights for the PTCS night time flag,"
        return self.computeRiseSetPressure(self.sun.getPTCSRiseSet
                                         , start = start
                                         , numDays = numDays)
       
    def computeOpticalNightWeights(self, start = None, numDays = None): 
        "Computes the weights for the optical flag,"
        return self.computeRiseSetPressure(self.sun.getRiseSet
                                         , start = start
                                         , numDays = numDays)
   
    def computeRiseSetPressure(self, riseSetFn, start = None, numDays = None): 
        "Computes the weights for a time of day constraint."

        if start is None:
            # start at start of semester
            start = self.nextSemesterStart 
        if numDays is None:
            # do the length of the semester
            numDays = (self.nextSemesterEnd - self.nextSemesterStart).days 
        # when is daytime for each day of the year? UTC?
        exCnt = [0]*24
        for days in range(numDays):
            # when is day light for this day, UTC? 
            dt = start + timedelta(days = days)
            # use the given function to compute rise/set for this day
            rise, set =riseSetFn(dt) 
            # LSTs for these UTC datetimes?
            # Note: set is the minLst, rise is the max, because
            # we want to penalize daytime
            minLst = sla.Absolute2RelativeLST(set) 
            maxLst = sla.Absolute2RelativeLST(rise) 
            # what bins do those fall into?
            ex = self.getLstRange(minLst, maxLst)    
            # now tally up the LST bins that are during night time    
            for s, e in ex:
                for h in range(s,e):
                    exCnt[h] += 1
            #todayStr = ",".join(["%d" % t for t in today])        
            #print "%s, %s, %5.2f, %5.2f, [%s]" % (rise.strftime("%H:%M:%S")
            #                            , set.strftime("%H:%M:%S")
            #                            , minLst, maxLst, todayStr)
        # Convert these counts to weights.
        weights = [(e/float(numDays)) for e in exCnt]
        return (weights, exCnt)

    def computeRfiWeights(self, start = None, numDays = None): 
        return self.computeRiseSetPressure(self.getRfiRiseSet
                                         , numDays = numDays
                                         , start = start)

    def getRfiRiseSet(self, date):
        "Gives the time high RFI start and ends for the given date."

        # DSS definition says this is between 8 AM - 8 PM EST.
        # Takes into account DST
        rise = datetime(date.year, date.month, date.day, 8)
        set  = datetime(date.year, date.month, date.day, 20)
        rise = TimeAgent.est2utc(rise)
        set  = TimeAgent.est2utc(set)
        return (rise, set)

    def getLstRange(self, minLst, maxLst):
        "How do we convert float min/max LST to int defined range?"
        minLst = self.binLst(minLst) 
        maxLst = self.binLst(maxLst) 
        if (0 > minLst or minLst > 24.0) or (0 > maxLst or maxLst > 24.0):
            print minLst, maxLst
            raise "Illegal LST min/max: ", minLst, maxLst #, session
        # special case?
        if minLst == maxLst:
            maxLst = minLst + 1
        # wrap around?
        if minLst > maxLst:
            ons = [(0, maxLst), (minLst, self.hrs)]
        else:
            ons = [(minLst, maxLst)]
        return ons

    def binLst(self, lstHrs):
        """
        We use floor to do this, but be careful of LSTs of 10:00:00
        in the UI coming back from rad2hr as 9.99999999999999
        """
        return int(math.floor(float("%.6f" % lstHrs))) #rad2hr(lstRads))))

    def getLstWeightsForSession(self, session):
        "Simple: LST's within min/max are on, rest are off."
        ws = self.newHrs() 
        ons = self.getLstRange(rad2hr(session.target.min_lst)
                             , rad2hr(session.target.max_lst))
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

    def usePeriodsForPressures(self, session):
        "What sessions should use their periods for computing pressures?"
        pcodes = ['Maintenance', 'Shutdown']
        return session.proposal.pcode in pcodes

    def getPressuresFromSessionsPeriods(self, session):
        """
        We figure out the carry over for Maintenance
        and Shutdown sessions from their periods.
        """
        periods = self.getSessionNextSemesterPeriods(session)
        ps = self.getPressuresFromPeriods(periods)
        return ps

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

    def calculatePressure(self, session, totalTime):
        """
        The heart of the algorithm for finding how a sessions
        time gets spread across it's LST range.
        """

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
        if weightSum != 0 and totalTime is not None:
            ps = [(totalTime * ws[i] * fs[i]) / weightSum \
                for i in range(self.hrs)]
        else:
            ps = [0.0]*self.hrs

        ps = numpy.array(ps)    

        return ps

    def isSessionForFutureSemester(self, session):
        """
        Large projects may have some sessions assigned to future semesters,
        in which case, we don't want to add them to the pressures.
        """
        if session.semester is not None:
            return session.semester.semester in self.futureSemesters 
        else:  
            return False

    def hasFailingGrade(self, session):
        if session.grade is not None:
            return session.grade.grade not in self.grades
        else:
            return True

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
        self.sessions = sessions         

        for s in sessions:
            # two distinct ways to compute pressures
            if not self.usePeriodsForPressures(s): 
                # compute pressures from LST and allotted time
                cat, subcat = self.getSessionCategories(s)
                if cat != IGNORED:
                    # which time to use depends on the categories
                    time = self.getSessionTime(s, cat, subcat)
                    # what's this sessions LST pressure?
                    ps = self.calculatePressure(s, time)
                    # how to track this pressure in the big picture?
                    self.accumulatePressure(s, cat, ps)
                else:
                    # ignored sessions get zeros for pressure
                    ps = self.newHrs()
            else:
                # compute pressures from periods
                cat = CARRYOVER 
                subcat = PERIODS 
                ps = self.getPressuresFromSessionsPeriods(s)
                self.accumulatePressure(s, cat, ps)

            #reporting
            self.pressuresBySession[s.__str__()] = (cat, subcat, ps, sum(ps))


        # make sure we have a record of what the original pressure was
        # before we adjusted for overfilled weather
        self.originalGradePs = self.gradePs.copy()
        self.gradePs['A'], self.changes = self.adjustForOverfilledWeather(\
            self.gradePs['A']
          , self.carryoverPs
          , self.weather.availability
         )

        # What's *really* available for this semester?
        self.remainingTotalPs = self.weather.availabilityTotal - \
            self.carryoverTotalPs
        self.remainingPs = self.weather.availability - self.carryoverPs
            
        # now convert the buckets to expected output
        return self.jsonDict()


    def accumulatePressure(self, session, category, ps):
        """
        Once we have the pressure for a particular session,
        how does it contribute to the big picture?
        """

        # accum pressure in total 
        self.totalPs += ps

        # use category like you think you would
        if category == CARRYOVER:
            self.carryoverTotalPs += ps
            self.carryoverPs += self.weather.binSession(session, ps)
        elif category == ALLOCATED:
            # TBF: a few of these totals and checks aren't
            # necessary anymore because we're not letting
            # sessions w/ out passing grades to fall into
            # this category
            self.newAstronomyTotalPs += ps
            if session.grade is not None and not self.hasFailingGrade(session):
                self.newAstronomyGradeTotalPs += ps
                wps = self.weather.binSession(session, ps)
                grade = session.grade.grade
                self.gradePs[grade] += wps
        elif category == REQUESTED:
            # this goes into the requested bucket
            self.requestedTotalPs += ps
            self.requestedPs += self.weather.binSession(session, ps)
        else:
            raise 'unhandled category'

    def getSessionTime(self, session, category, subCategory):
        """
        The time we use for the pressure depends on what
        category the session belongs to, among other things.
        """
        totalTime = 0.0
        if category == CARRYOVER:
           # which method for determining carryover time to use?
           if self.carryOverUseNextSemester:
                if session.next_semester is not None \
                    and session.next_semester.complete == False:
                    totalTime = session.next_semester.time
           else:
               if not session.dss_session.isComplete(): 
                   ta = TimeAccounting()
                   totalTime = ta.getTimeRemaining(session.dss_session)
                   totalTime = totalTime if totalTime >= 0.0 else 0.0
        elif category == ALLOCATED:    
            # which time attribute of the session to use?
            if subCategory == SEMESTER:
                totalTime = session.allotment.semester_time
            else:
                totalTime = session.allotment.allocated_time
        elif category == REQUESTED:
            totalTime = session.getTotalRequestedTime()
        return totalTime

    def getSessionCategories(self, session):
        "What category & sub-category to put this session into?"

        if session.target is None or session.target.min_lst is None or session.target.max_lst is None:
            return (IGNORED, BADLST)

        if session.dss_session is not None \
            and session.semester.semester <= self.currentSemester.semester \
            and session.grade is not None \
            and session.grade.grade in ['A', 'B', 'C']:
            return (CARRYOVER, '')
        elif session.semester.semester == self.nextSemester.semester \
            and session.allotment is not None \
            and session.allotment.allocated_time is not None \
            and session.grade is not None \
            and session.grade.grade in ['A', 'B', 'C']:
            if session.allotment.semester_time is not None and \
                session.allotment.semester_time > 0.0:
                return (ALLOCATED, SEMESTER)
            return (ALLOCATED, '')
        elif session.semester.semester == self.nextSemester.semester:
            return (REQUESTED, '')
        else:
            # ignored, now figure out why:
            if session.semester.semester > self.nextSemester.semester:
                return (IGNORED, FUTURE)
            elif session.semester.semester <= self.currentSemester.semester:
                if (session.grade is None or session.grade.grade not in ['A', 'B', 'C']):
                    return (IGNORED, CARRYOVER_BAD_GRADE)
                elif session.dss_session is None:
                    return (IGNORED, CARRYOVER_NO_DSS)
                else:
                    return (IGNORED, '')
            else:    
                return (IGNORED, '')    

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

    def adjustForOverfilledWeather(self, gradeA, carryover, availability):
        """
        When there's too much hours in the poor weather category, it
        eats up the good weather; and if there's too much good weather,
        that eats up the excellent weather.  Specifically:

        If Grade A (Poor Weather) + Carryover (Poor Weather) > Availability (Poor Weather) then
           * Remainder (Poor Weather) = Grade A (Poor Weather) + Carryover (Poor Weather) - Availability (Poor Weather)
           * Grade A (Poor Weather) = Availability (Poor Weather) - Carryover (Poor Weather)
           * and then consider the Remainder (Poor Weather) time for Good Weather (and so on to Excellent Weather):
           * if Grade A (Good Weather) + Carryover (Good Weather) + Remainder (Poor Weather) &gt; Availability (Good Weather) then 
               * Remainder (Good Weather) = Grade A (Good Weather) + Carryover (Good Weather) + Remainder (Poor Weather) - Availability (Good Weather)
               * Grade A (Good Weather) = Availability (Good Weather) - Carryover (Good Weather) 
           * else
               * Grade A (Good Weather) += Remainder (Poor Weather)
        """

        tmp = Pressures()
        allocated = Pressures()
        remainder = Pressures()
        changes = Pressures()

        for i in range(self.hrs):
            # init the allocation
            allocated.poor[i] = gradeA.poor[i]
            allocated.good[i] = gradeA.good[i]
            allocated.excellent[i] = gradeA.excellent[i]
            # too much poor?
            tmp.poor[i] = gradeA.poor[i] + carryover.poor[i]
            if tmp.poor[i] > availability.poor[i]:
                remainder.poor[i] = tmp.poor[i] - availability.poor[i]
                changes.poor[i] = remainder.poor[i]
                # take time out of poor
                allocated.poor[i] = availability.poor[i] - carryover.poor[i]
                # and give it to good 
                tmp.good[i] = gradeA.good[i] + carryover.good[i] + remainder.poor[i]
                # but is this too much?
                if tmp.good[i] > availability.good[i]:
                    remainder.good[i] = tmp.good[i] - availability.good[i]
                    # take time from good
                    allocated.good[i] = availability.good[i] - carryover.good[i]
                    # and give it to excellent
                    allocated.excellent[i] = gradeA.excellent[i] + remainder.good[i]
                    # record this change
                    changes.excellent[i] = remainder.good[i]
                    changes.good[i] = changes.poor[i] - changes.excellent[i]
                else:
                    # not too much to give all to good
                    allocated.good[i] = gradeA.good[i] + remainder.poor[i]
                    changes.good[i] = remainder.poor[i]

        return (allocated, changes)

    def findProcessedSessions(self, category, subCategory = None):
        "Grab sessions of certain category from the list"
        if subCategory is None:
            sessNames = [name for name, data in self.pressuresBySession.items() if category == data[0] ]
        else:
            sessNames = [name for name, data in self.pressuresBySession.items() if category == data[0] and subCategory == data[1]]
        return [s for s in self.sessions if s.__str__() in sessNames]

    def getIgnoredRequestedTime(self):
        """
        Goes through our pressure history, and returns the totla
        hours that got ignored.
        """
        #return sum([data[3] for name, data in self.pressuresBySession.items() if data[0] == IGNORED])
        ss = self.findProcessedSessions(IGNORED)
        return sum([s.allotment.requested_time for s in ss])

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
            msgs.append("Total Carry Over != All Weather Types ( %5.2f vs. %5.2f)" % (self.carryoverTotalPs.sum(), totalCarryover.sum()))
        
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
        if not self.almostEqual(totalNewAstro, self.newAstronomyGradeTotalPs):
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
        print ""
        print "Original (non-adjusted) Grade A Next Semester Astromony: "
        for w in self.weatherTypes:
            print self.formatResults("      %s" % w
                                   , self.originalGradePs['A'].getType(w))

        print ""
        print "Changes from overfilled Weather bins: "
        for w in self.weatherTypes:
            print self.formatResults("      %s" % (w)
                                   , self.changes.getType(w))

        if len(self.sessions) != len(self.pressuresBySession):
            print "R U Missing sessions?: ", len(self.sessions), len(self.pressuresBySession)

        # warnings
        valid, msgs = self.checkPressures()
        if not valid:
            print ""
            print "WARNINGS: "
            for m in msgs:
                print m 

        # more debugging
        print ""
        self.badSessions = self.findProcessedSessions(IGNORED, BADLST)
        print "Bad Sessions: %d" % len(self.badSessions)
        for b in self.badSessions:
            print "    ", b
        self.futureSessions = self.findProcessedSessions(IGNORED, FUTURE)
        print "Future Sessions: %d" % len(self.futureSessions)
        for s in self.futureSessions:
            print "    ", s
        self.semesterSessions = self.findProcessedSessions(ALLOCATED, SEMESTER)
        print "Sessions using semester time: %d" % len(self.semesterSessions)
        for s in self.semesterSessions:
            print "    ", s

        # everybodies pressure!
        print ""
        print "Pressures by Session: "
        for k in sorted(self.pressuresBySession.keys()):
            bucket, sb, ps, total = self.pressuresBySession[k]
            if sb == '':
                lbl = "%s (%s, %5.2f)" % (k, bucket, total)
            else:
                lbl = "%s (%s, %s, %5.2f)" % (k, bucket, sb, total)
            print self.formatResults(lbl, ps, lblFrmt = "%35s")
        print ""
        print "Non-Zero Pressures by Session: "
        for k in sorted(self.pressuresBySession.keys()):
            bucket, sb, ps, total = self.pressuresBySession[k]
            if sum(ps) > 0.0:
                lbl = "%s (%s, %5.2f)" % (k, bucket, total)
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
        "These are what you get from 12B"

        # TBF: These get computed by methods in this class,
        # but no need to do it at start up every time.
        self.thermalNightWeights = numpy.array([0.71584699453551914,
            0.77049180327868849,
            0.77595628415300544,
            0.77049180327868849,
            0.77049180327868849,
            0.70491803278688525,
            0.63934426229508201,
            0.57377049180327866,
            0.50819672131147542,
            0.44262295081967218,
            0.37704918032786883,
            0.31147540983606559,
            0.2404371584699454,
            0.16393442622950816,
            0.076502732240437132,
            0.0,
            0.0,
            0.0,
            0.010928961748633892,
            0.13114754098360659,
            0.27322404371584696,
            0.4098360655737705,
            0.53005464480874309,
            0.63387978142076506])
        self.opticalNightWeights = numpy.array([0.92896174863387981,
            0.97267759562841527,
            0.91256830601092898,
            0.84153005464480879,
            0.77595628415300544,
            0.70491803278688525,
            0.63934426229508201,
            0.57377049180327866,
            0.50819672131147542,
            0.44262295081967218,
            0.37704918032786883,
            0.31147540983606559,
            0.2404371584699454,
            0.16393442622950816,
            0.076502732240437132,
            0.010928961748633892,
            0.13661202185792354,
            0.27322404371584696,
            0.4098360655737705,
            0.53005464480874309,
            0.63387978142076506,
            0.72131147540983609,
            0.79234972677595628,
            0.86338797814207646])
        self.rfiWeights     = numpy.array([0.71584699453551914,
            0.79781420765027322,
            0.88524590163934425,
            0.91256830601092898,
            0.86338797814207646,
            0.78142076502732238,
            0.69398907103825136,
            0.61202185792349728,
            0.53005464480874309,
            0.48087431693989069,
            0.44808743169398912,
            0.36612021857923494,
            0.27868852459016391,
            0.19672131147540983,
            0.11475409836065575,
            0.081967213114754078,
            0.13661202185792354,
            0.21857923497267762,
            0.30054644808743169,
            0.38251366120218577,
            0.4699453551912568,
            0.51912568306010931,
            0.55191256830601088,
            0.63387978142076506])

    def initFlagWeightsBad(self):
        "These are what you get from 12B"

        # TBF: These get computed by methods in this class,
        # but no need to do it at start up every time.
        self.thermalNightWeights = numpy.array([0.28415300546448086,
            0.22950819672131148,
            0.22404371584699453,
            0.22950819672131148,
            0.22950819672131148,
            0.29508196721311475,
            0.36065573770491804,
            0.42622950819672129,
            0.49180327868852458,
            0.55737704918032782,
            0.62295081967213117,
            0.68852459016393441,
            0.7595628415300546,
            0.83606557377049184,
            0.92349726775956287,
            1.0,
            1.0,
            1.0,
            0.98907103825136611,
            0.86885245901639341,
            0.72677595628415304,
            0.5901639344262295,
            0.46994535519125685,
            0.36612021857923499])
        self.opticalNightWeights = numpy.array([0.071038251366120214,
            0.027322404371584699,
            0.087431693989071038,
            0.15846994535519127,
            0.22404371584699453,
            0.29508196721311475,
            0.36065573770491804,
            0.42622950819672129,
            0.49180327868852458,
            0.55737704918032782,
            0.62295081967213117,
            0.68852459016393441,
            0.7595628415300546,
            0.83606557377049184,
            0.92349726775956287,
            0.98907103825136611,
            0.86338797814207646,
            0.72677595628415304,
            0.5901639344262295,
            0.46994535519125685,
            0.36612021857923499,
            0.27868852459016391,
            0.20765027322404372,
            0.13661202185792351])
        self.rfiWeights     = numpy.array([0.28415300546448086,
            0.20218579234972678,
            0.11475409836065574,
            0.087431693989071038,
            0.13661202185792351,
            0.21857923497267759,
            0.30601092896174864,
            0.38797814207650272,
            0.46994535519125685,
            0.51912568306010931,
            0.55191256830601088,
            0.63387978142076506,
            0.72131147540983609,
            0.80327868852459017,
            0.88524590163934425,
            0.91803278688524592,
            0.86338797814207646,
            0.78142076502732238,
            0.69945355191256831,
            0.61748633879781423,
            0.5300546448087432,
            0.48087431693989069,
            0.44808743169398907,
            0.36612021857923499])
    
    def initFlagWeights2012(self):
        "These are what you get from 2012"

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
    #today = datetime(2012, 7, 30)
    #lst = LstPressures(today = today)
    lst = LstPressures()
    #lst = LstPressures(carryOverUseNextSemester = False)

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


