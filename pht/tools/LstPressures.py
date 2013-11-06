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

from django.db.models import Q

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
from scheduler.models import Sponsor as DSSSponsor
from pht.tools.Sun    import Sun
from pht.tools.LstPressureWeather import LstPressureWeather
from pht.tools.LstPressureWeather import Pressures

from copy import deepcopy
import numpy
import sys

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
SPONSORED = 'sponsored'

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
        

    def __init__(self
               , carryOverUseNextSemester = True
               , adjustWeatherBins = True
               , initFlagWeights = True
               , hideSponsors = True
               , today = None):

        self.hrs = 24
        self.bins = [0.0]*self.hrs

        # do sponsored proposals for next semester get subsumed into carryover?
        self.hideSponsors = hideSponsors

        # when calculating carry over, use the next semester field,
        # OR the current time remaining?
        self.carryOverUseNextSemester = carryOverUseNextSemester

        # should we make adjustments when there's TOO much excellent
        # weather requested?
        self.adjustWeatherBins = adjustWeatherBins


        # for reporting
        self.pressures = [] 
        self.sessions = []
        self.badSessions = []
        self.pressuresBySession = {}
        self.weatherPsBySession = {}
        self.weatherPressuresBySession = {}
        self.futureSessions = []
        self.semesterSessions = []
        self.maintenancePs = Pressures() 
        self.shutdownPs = Pressures() 
        self.testingPs = Pressures() 


        # for computing day light hours
        self.sun = Sun()
        
        if today is None:
            today = datetime.today()

        # Example: if today is march 1, 2012, then the current semester
        # is 12A, but what we want to calculate things for is the
        # next semester, which is 12B.  All semesters after that are
        # 'future semesters' (13A, 13B, 14A, etc.)
        self.currentSemester = DSSSemester.getCurrentSemester(today = today)
        sems = DSSSemester.getFutureSemesters(today = today)
        self.nextSemester = sems[0]
        self.nextSemesterStart = self.nextSemester.start()
        self.nextSemesterEnd   = self.nextSemester.end()
        self.futureSemesters = [s.semester for s in sems][1:] 

        self.timeRange = (self.nextSemesterStart
                        , self.nextSemesterEnd)
        self.published = None

        # for computing pressures based on weather type, on 
        # holding these results
        self.weather = LstPressureWeather(semester = self.nextSemester.semester)

        # TBF: get from DB?
        self.grades = ['A', 'B', 'C']
        self.weatherTypes = ['Poor', 'Good', 'Excellent']
        self.weatherMap = {'poor' : 'Low Freq'
                         , 'good' : 'Hi Freq 1'
                         , 'excellent' : 'Hi Freq 2'
                          }
        # yeah, lets get these from the DB
        self.sponsors = [s.abbreviation for s in DSSSponsor.objects.all() if s.name != '']

        self.initPressures()
        if initFlagWeights:
            self.initFlagWeights()

        self.testSessions = self.getTestSessions()

        self.fixedType = SessionType.objects.get(type = 'Fixed')

    def newHrs(self):
        return numpy.array([0.0]*self.hrs)

    def newPressuresByGrade(self):
        return deepcopy({ 'A' : Pressures()
                        , 'B' : Pressures()
                        , 'C' : Pressures()
                        })
                        
    def sponsoredPsSummed(self):

        total = Pressures()
        for k, ps in self.sponsoredPs.items():
            total += ps
        return total

    def initPressures(self):
        """
        Here are the rules:
        totalAv = total available time for the semester; simply the days in the semester * 24 hours.
        preAssigned = pre assigned time for the semester; sum of the hours for Maintenance, Shutdown, and testing
        astroAv = totalAv - preAssigned
        carryover = hours from carryover - that is proposals from previous semesters *not* included in preAssigned. carryover = coA + coB + coC
        coA, coB, coC = the carryover broken down by grade; 
        newAstroAv = available for NEW astronomy in the semester.  newAstroAv = totalAv - preAssigned - carryover
        newAstroAvCoA = available for NEW astronomy in the semester only taking grade A carryover into account.  newAstroAvCoA = totalAv - preAssigned - coA
    
        Here's a summary of the rules:
        astroAv = totalAv - preAssigned
        newAstroAv = totalAv - preAssigned - carryover
        """
    
        # init our buckets:
        # This is *everything* 
        self.totalPs  = numpy.array([0.0]*self.hrs)

        # totalAv: self.weather.availability

        # the sponsored pressures are divided by sponsor name
        self.sponsoredTotalPs = {}
        self.sponsoredPs = {}
        for s in self.sponsors:
            self.sponsoredTotalPs[s] = self.newHrs()
            self.sponsoredPs[s] = Pressures()

        # pre-assigned:
        self.maintenancePs = Pressures() 
        self.shutdownPs = Pressures() 
        self.testingPs = Pressures() 
        self.preAssignedPs = self.maintenancePs \
                           + self.shutdownPs \
                           + self.testingPs

        self.postMaintAvailabilityPs = Pressures()

        # Stuff left over from previous semester's, and the
        # next semesters committed time to maintenance, testing etc.
        # totalCarryover = astroCarryover + preAssigned
        self.carryoverTotalPs = numpy.array([0.0]*self.hrs)
        self.carryoverPs = Pressures() 

        # astroCarryover = totalCarryover - preAssigned
        # astroCarryover = coA + coB + coC (sum of grades)
        self.carryoverGradePs = { 'fixed' : self.newPressuresByGrade()
                                , 'rest'  : self.newPressuresByGrade()
                                , 'total' : self.newPressuresByGrade()
                                }

        # Available time for the semester - all carryover
        # self.weather.availability - totalCarryover
        self.remainingTotalPs = self.newHrs()
        self.remainingPs = Pressures()

        # newAstroAv = available for NEW astronomy in the semester.  newAstroAv = totalAv - preAssigned - astroCarryover - sponsored
        self.remainingFromAllGradesCarryoverPs = Pressures()
        # newAstroAvCoA = available for NEW astronomy in the semester only taking grade A carryover into account.  newAstroAvCoA = totalAv - preAssigned - coA - sponsored
        self.remainingFromGradeACarryoverPs = Pressures()

        # The new stuff that people have submitted proposals for,
        # before having been allocated time
        self.requestedTotalPs = self.newHrs() 
        self.requestedPs = Pressures() 

        # The new stuff htat people have submitted proposal for,
        # AFTER they've been allocated time.
        self.newAstronomyTotalPs = numpy.array([0.0]*self.hrs)
        # the sum of grades A, B, C
        self.newAstronomyGradeTotalPs = numpy.array([0.0]*self.hrs)
        self.gradePs = self.newPressuresByGrade()
        self.originalGradePs = self.newPressuresByGrade()

        # for holding what to do with overfilled weather bins
        self.changes = Pressures()


    def assertPressures(self):
        "Asserts that we have self-consistency"

        assert self.postMaintAvailabilityPs == self.weather.availability - self.preAssignedPs
         
        totalCarryover = self.preAssignedPs \
                                + self.carryoverGradePs['total']['A'] \
                                + self.carryoverGradePs['total']['B'] \
                                + self.carryoverGradePs['total']['C'] 
        # these sums don't add up if we're hiding next semester's sponsored sessions
        # in the carry over - cause those sessions aren't graded properly yet.
        if not self.hideSponsors:                        
            assert abs(self.carryoverPs.total() - totalCarryover.total()) < 0.01

        total = self.carryoverTotalPs + self.newAstronomyTotalPs + \
            self.requestedTotalPs + self.sponsoredPsSummed().allTypes() 
        assert self.almostEqual(self.totalPs, total)
        assert self.almostEqual(self.carryoverPs.allTypes()
                              , self.carryoverTotalPs)
        assert self.almostEqual(self.requestedPs.allTypes()
                              , self.requestedTotalPs)

        # new astronomy allocated
        totalNewAstro = self.newHrs() 
        for g in self.grades:
            totalNewAstro += self.gradePs[g].allTypes()
        assert self.almostEqual(totalNewAstro, self.newAstronomyGradeTotalPs)

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
            rise, set = riseSetFn(dt) 

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

    def getTestSessions(self):
        "What are the testing sessions for this semester?"
        sem = self.nextSemester.semester
        testing = Observing_Type.objects.get(type='testing')
        commissioning = Observing_Type.objects.get(type='commissioning')
        calibration = Observing_Type.objects.get(type = 'calibration')
        ss = Session.objects.filter(Q(semester__semester = sem) 
                                    , Q(observing_type = testing) \
                                    | Q(observing_type = commissioning)\
                                    | Q(observing_type = calibration))
        return ss

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
        ps = [e.periods.exclude(state__abbreviation = 'D').order_by('start')[0] \
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


        start = period.start
        dur   = period.duration
        end   = period.end()
        
        # for periods < 24 hours long (99% of them), this will be 0.0
        days = (end - start).days
        ps = [days] * self.hrs

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
                        ps[hr] += 1.0
                    elif hr < s and (hr+1) > s:
                        ps[hr] += (hr+1) - s
                    else:
                        ps[hr] += e - hr
            
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

    def isSessionSponsored(self, session):
        "Its tagged as such and not from the past."
        return session.proposal.isSponsored()

        # TBF: since the first round of sponsored proposals include proposals from
        # previous semesters, we need to ignore this until next semester.
        #return session.proposal.isSponsored() \
        #    and (session.proposal.semester.semester == self.nextSemester.semester \
        #      or session.proposal.semester.semester in self.futureSemesters)

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

    def getOriginalRequestedPressures(self, sessions = None):
        """
        Specialty function needed only by Semester Summary Report.
        Get all sessions associated with proposals of the next semester,
        and find their pressures based off of their requested time.
        """

        if sessions is None:
            sessions = Session.objects.filter(proposal__semester = \
                self.nextSemester).order_by('name')
            # filter out the test sessions    
            sessions = [s for s in sessions if s not in self.testSessions and not s.proposal.isSponsored()]   

        self.originalRequestedPs = Pressures()
        for s in sessions:
            wps = self.getRequestedPressure(s)
            self.originalRequestedPs += wps

        return self.originalRequestedPs    

    def getRequestedPressure(self, session):
        "What was this session's original requested pressure?" 
        # get the requested time for this session
        time = self.getSessionTime(session, REQUESTED, "")
        # calculate the pressure
        ps = self.calculatePressure(session, time)
        # bin the pressure into the weather bins
        return self.weather.binSession(session, ps)

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
    
        self.published = datetime.now()

        self.initPressures()

        # what sessions are we doing this for?
        self.sessions = sessions or Session.objects.all().order_by('name')

        for s in self.sessions:
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
        if self.adjustWeatherBins:
            self.gradePs['A'], self.changes = self.adjustForOverfilledWeather(
                self.gradePs['A']
              , self.carryoverPs
              , self.weather.availability
             )

        
        # here's some more measures of 'availability':
        # what's available after all the pre-assigned maintenance,
        # testing, and shutdown?
        self.preAssignedPs = self.maintenancePs + self.shutdownPs + self.testingPs 
        self.postMaintAvailabilityPs = self.weather.availability - self.preAssignedPs 

        # what's available after just grade A carryover?
        self.remainingFromGradeACarryoverPs = self.postMaintAvailabilityPs - self.carryoverGradePs['total']['A'] - self.sponsoredPsSummed()

        # what's available after all grades?
        allGrades = self.carryoverGradePs['total']['A'] \
                  + self.carryoverGradePs['total']['B'] \
                  + self.carryoverGradePs['total']['C']
        self.remainingFromAllGradesCarryoverPs = self.postMaintAvailabilityPs - allGrades - self.sponsoredPsSummed() 


        # What's *really* available for this semester?
        # note that *this* carryover includes maint, shutdown, & testing
        self.remainingTotalPs = self.weather.availabilityTotal - \
            self.carryoverTotalPs - self.sponsoredPsSummed().allTypes()
        self.remainingPs = self.weather.availability - self.carryoverPs - self.sponsoredPsSummed() 

        # fail if shit doesn't add up?
        self.assertPressures()

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
            wps = self.weather.binSession(session, ps)
            self.carryoverPs += wps 

            # special cases that need the pressures binned by weather
            if self.usePeriodsForPressures(session):
                if session.proposal.pcode == 'Maintenance':
                    self.maintenancePs += wps 
                elif session.proposal.pcode == 'Shutdown':
                    self.shutdownPs += wps
                else:
                    raise "Only Maintenance and Shutdown should use periods"
            elif session in self.testSessions:                
                self.testingPs += wps
            else:
                # Maintenance, Shutdown and testing was pre-assigned (above)
                # , but we want to report on all the other carryover by grade
                grade = None
                if session.grade is not None and not self.hasFailingGrade(session):
                    grade = session.grade.grade
                elif session.proposal.isSponsored():
                    # sponsored proposals are assumed grade A
                    grade = 'A'

                if grade is not None:
                    self.carryoverGradePs['total'][grade] += wps 
                    if session.session_type is not None and \
                        session.session_type == self.fixedType:
                        self.carryoverGradePs["fixed"][grade] += wps
                    else:    
                        self.carryoverGradePs["rest"][grade] += wps

        elif category == ALLOCATED:
            # TBF: a few of these totals and checks aren't
            # necessary anymore because we're not letting
            # sessions w/ out passing grades to fall into
            # this category
            self.newAstronomyTotalPs += ps
            if session.grade is not None and not self.hasFailingGrade(session):
                self.newAstronomyGradeTotalPs += ps
                wps = self.weather.binSession(session, ps)
                # reporting: keep track of this for comparisons w/ Socorro
                self.weatherPressuresBySession[session.__str__()] = wps
                grade = session.grade.grade
                self.gradePs[grade] += wps
        elif category == REQUESTED:
            # this goes into the requested bucket
            self.requestedTotalPs += ps
            wps = self.weather.binSession(session, ps)
            self.requestedPs += wps 
        elif category == SPONSORED:
            wps = self.weather.binSession(session, ps)
            sponsor = session.proposal.sponsor.abbreviation
            self.sponsoredTotalPs[sponsor] += ps
            self.sponsoredPs[sponsor] += wps 
        else:
            raise 'unhandled category'

        # reporting
        self.weatherPsBySession[session.__str__()] = (category, wps)

    def getSessionTime(self, session, category, subCategory):
        """
        The time we use for the pressure depends on what
        category the session belongs to, among other things.
        """
        totalTime = 0.0
        if category == CARRYOVER:
           # which method for determining carryover time to use?
           # Test Sessions
           if session in self.testSessions:
               totalTime = session.getTotalAllocatedTime()
           # Sponsored Sessions    
           elif subCategory == SPONSORED:
               # TBF: or requested time?
               #totalTime = session.getTotalAllocatedTime()
               totalTime = session.getTotalRequestedTime()
           # All other Carryover    
           elif self.carryOverUseNextSemester:
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
                # TBF: getTotalSemesterTime ?
                totalTime = session.allotment.semester_time 
            else:
                totalTime = session.getTotalAllocatedTime() #session.allotment.allocated_time
        elif category == SPONSORED:
             totalTime = session.getTotalRequestedTime()
        elif category == REQUESTED:
            totalTime = session.getTotalRequestedTime()
        return totalTime

    def getSessionCategories(self, session):
        "What category & sub-category to put this session into?"

        if session.target is None or session.target.min_lst is None or session.target.max_lst is None:
            return (IGNORED, BADLST)

        if session in self.testSessions or (session.dss_session is not None \
            and session.semester.semester <= self.currentSemester.semester \
            and session.grade is not None \
            and session.grade.grade in ['A', 'B', 'C']):
            return (CARRYOVER, '')
        elif self.isSessionSponsored(session):
            if self.hideSponsors:
                return (CARRYOVER, SPONSORED)
            else:
                return (SPONSORED, session.proposal.sponsor.abbreviation)
        elif session.semester.semester == self.nextSemester.semester \
            and session.allotment is not None \
            and session.allotment.allocated_time is not None \
            and session.allotment.allocated_repeats is not None \
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
            #if not self.hideSponsors:              
            for s in self.sponsors:              
                lstDict[s] = self.sponsoredTotalPs[s][i]              
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
                # sponsored
                for s in self.sponsors:
                    spnType = "%s_%s" % (s, weather)
                    lstDict[spnType] = self.sponsoredPs[s].getType(weather)[i]

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
                if carryover.poor[i] < availability.poor[i]:
                    remainder.poor[i] = tmp.poor[i] - availability.poor[i]
                    # take time out of poor
                    allocated.poor[i] = availability.poor[i] - carryover.poor[i]
                else:
                    # just move grade A if carryover more than availability
                    remainder.poor[i] = gradeA.poor[i]
                    allocated.poor[i] = 0
                changes.poor[i] = remainder.poor[i]
                # take time out of poor
                #allocated.poor[i] = availability.poor[i] - carryover.poor[i]
                # and give it to good 
                tmp.good[i] = gradeA.good[i] + carryover.good[i] + remainder.poor[i]
                # but is this too much?
                if tmp.good[i] > availability.good[i]:
                    if carryover.good[i] < availability.good[i]:
                        remainder.good[i] = tmp.good[i] - availability.good[i] if carryover.good[i] < availability.good[i] else gradeA.good[i] + remainder.poor[i]
                        # take time from good
                        allocated.good[i] = availability.good[i] - carryover.good[i]
                    else:
                        remainder.good[i] = gradeA.good[i] + remainder.poor[i]
                        allocated.good[i] = 0
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
            self.requestedTotalPs + self.sponsoredPsSummed().allTypes()
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
        print "Next Semester Astronomy Summary: "
        for g in self.grades:
            print self.formatResults("      %s" % g
                                   , self.gradePs[g].allTypes())

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
        print "Adjusting Weather Bins? ", self.adjustWeatherBins
        print "Carryover using: ", 'Next Semester' if self.carryOverUseNextSemester else 'Time Remaining'
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
        print "Number of Testing Sessions: %d" % len(self.testSessions)    
        for s in self.testSessions:    
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
        print "Remaining Hours (poor, good, excellent) by LST (0-23)"
        for hr in range(self.hrs):
            print "%.2f,%.2f,%.2f" % (self.remainingPs.poor[hr]
                                    , self.remainingPs.good[hr]
                                    , self.remainingPs.excellent[hr])

        print "Carryover Hours (poor, good, excellent) by LST (0-23)"
        for hr in range(self.hrs):
            print "%.2f,%.2f,%.2f" % (self.carryoverPs.poor[hr]
                                    , self.carryoverPs.good[hr]
                                    , self.carryoverPs.excellent[hr])

        # for Toney
        print ""
        print "Preassigned pressures:"
        self.reportPressures("Maintenance"
                           , self.maintenancePs.allTypes()
                           , self.maintenancePs)
        self.reportPressures("Shutdown"
                           , self.shutdownPs.allTypes()
                           , self.shutdownPs)
        self.reportPressures("Testing"
                           , self.testingPs.allTypes()
                           , self.testingPs)

        if not self.hideSponsors:
            print ""
            print "Sponsored pressures: "
            for s in self.sponsors:
                self.reportPressures(s
                                   , self.sponsoredPs[s].allTypes()
                                   , self.sponsoredPs[s])


    def sessionKey2Id(self, key):
        "name (id) -> id"
        return int(key.split(' ')[-1][1:-1])

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
 
    def reportLstContributions(self, lst, grade, wtype):

        print "Contributors to Allocated pressure at LST: %d, Grade: %s, weather: %s" % \
            (lst, grade, wtype)
        total = 0.0    
        for name in sorted(self.weatherPsBySession.keys()):
            cat, wps = self.weatherPsBySession[name]
            sId = self.sessionKey2Id(name)
            s = Session.objects.get(id = sId)
            if cat == ALLOCATED and s.grade.grade == grade:
                ps = wps.getType(wtype)
                if ps[lst] > 0.0:
                    print name, ps[lst]
                    total += ps[lst]
        print "Total: ", total        

    def reportSemesterSummary(self):

        print "Time Analysis for Semester %s" % self.nextSemester.semester
        print "%s - %s" % (self.nextSemesterStart, self.nextSemesterEnd)
        print ""
        print "Hours in Semester: %5.2f    GC[%5.2f]" % (self.weather.availability.total()
                                                       , self.weather.availability.total(gc = True)
                                                        )
        print "Maintenance Hours: %5.2f    GC[%5.2f]" % (self.maintenancePs.total()
                                                       , self.maintenancePs.total(gc = True)
                                                        )
        print "Test, Comm, Calib Hours: %5.2f    GC[%5.2f]" % (self.testingPs.total()                                                 , self.testingPs.total(gc = True)
                                                        )
        print "Shutdown Hours: %5.2f    GC[%5.2f]" % (self.shutdownPs.total() 
                                                    , self.shutdownPs.total(gc =True)
                                                      )
        print ""
        label = "Avialbable for ALL Astronomy during %s" % self.nextSemester.semester
        self.reportSemesterSummaryTable(label, self.postMaintAvailabilityPs)
        for g in self.grades:
            print ""
            self.reportSemesterSummaryCarryover(g.upper()
                                              , self.carryoverGradePs) 


        print ""
        label = "Available for NEW Astronomy during 12B (Grade A Carry)"
        self.reportSemesterSummaryTable(label
                                      , self.remainingFromGradeACarryoverPs)

        print ""
        label = "Available for NEW Astronomy during 12B (All Grades)"
        self.reportSemesterSummaryTable(label
                                      , self.remainingFromAllGradesCarryoverPs)

    def reportSemesterSummaryCarryover(self, grade, ps):
        print "Group %s Time: " % grade
        g = grade.upper()
        print self.formatSummaryHrs("Hours Total:", ps['total'][g])
        print self.formatSummaryHrs("Hours Fixed:", ps['fixed'][g])
        for w in self.weatherTypes:
            print self.formatSummaryHrs("Hours for %s:" % self.weatherMap[w.lower()], ps['rest'][g], type = w.lower())
        
    def reportSemesterSummaryTable(self, label, ps):
        print label 
        print self.formatSummaryHrs("Hours Total:", ps)
        for w in self.weatherTypes:
            print self.formatSummaryHrs("Hours for %s:" % self.weatherMap[w.lower()], ps, type = w.lower())
        
        


    def formatSummaryHrs(self, label, ps, type = None):
        
        return "%25s %5.2f    GC[%5.2f]" % (label
                                          , ps.total(type = type)
                                          , ps.total(type = type
                                                   , gc = True))

    def compareNewAstronomyPressures(self):
        
        self.compareNewAstronomyPressuresAll()
        for w in self.weatherTypes:
            self.compareNewAstronomyPressuresByType(w.lower())


    def compareNewAstronomyPressuresAll(self):
        f = '/users/pmargani/webtest.txt'
        socPs = self.getSocorroPressures(f) 
        #print "SOC: ", socPs

        # get our equivalent:
        for g in self.grades:
            soc = socPs[g]
            gb = self.gradePs[g].allTypes()
            print "Grade: ", g
            print gb - soc

    def compareNewAstronomyPressuresByType(self, wtype):

        print "Type: ", wtype
        #f = '/users/pmargani/webtest.txt'
        #f = '/users/pmargani/webtest_excellent.txt'
        #f = '/users/pmargani/webtest_good.txt'
        #f = '/users/pmargani/webtest_poor.txt'
        f = '/users/pmargani/webtest_%s.txt' % wtype
        socPs = self.getSocorroPressures(f) 
        #print "SOC: ", socPs

        # get our equivalent:
        for g in self.grades:
            soc = socPs[g]
            #gb = self.gradePs[g].getType('Excellent')
            #gb = self.gradePs[g].getType('Good')
            #gb = self.gradePs[g].getType('Poor')
            gb = self.gradePs[g].getType(wtype)
            print "Grade: ", g
            print gb - soc

    def reportSocorroGrade(self, grade):
        "For comparing our pressures to the table under Soc's plots"

        # grade A Allocated, broken down by session
        print ""
        print "Grade %s Pressures by Session: " % grade
        gradeAtotal = self.newHrs()
        gradeAnum = 0 
        gradeAallocated = 0.0 
        pids = {}
        for k in sorted(self.pressuresBySession.keys()):
            bucket, sb, ps, total = self.pressuresBySession[k]
            #try:
            #if 'VLBA' not in k:
            if 1:
                id = self.sessionKey2Id(k)
                s = Session.objects.get(id = id)
                if bucket == ALLOCATED and s.grade.grade == grade:
                    pid = s.proposal.id
                    if not pids.has_key(pid):
                        pids[pid] = 1
                    else:
                        pids[pid] += 1
                    gradeAtotal += ps
                    gradeAnum += 1
                    if s.allotment.semester_time is not None and sb == 'semester':
                        gradeAallocated += s.allotment.semester_time
                    else:    
                        gradeAallocated += s.getTotalAllocatedTime()
                    lbl = "%s %s (%s, %s, %5.2f vs %5.2f vs %5.2f)" % (k, s.semester.semester, bucket, sb, total, s.getTotalAllocatedTime(), sum(ps))
                    print self.formatResults(lbl, ps, lblFrmt = "%35s")
                    
        print self.formatResults("Grade A Total: ", gradeAtotal, lblFrmt = "%35s")
        print "Grade A Total across LSTs: %5.2f" % sum(gradeAtotal)
        print "Grade A allocated: %5.2f" % gradeAallocated  
        # print table of proposal ID's
        t = 0
        ks = sorted(pids.keys())
        print "| Proposal ID | Count |" 
        for k in ks:
            print "| %12d | %7d |" % (k, pids[k]) 
            t += pids[k]
        print "Count total: %d" % t 

    def socorroFormat(self, session, ps):
        """
        Each row looks like this:
        (6529),3.00,3.00,3.00,3.00,3.00,3.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00
        where the first column is the session id, and they are ordered
        by id.
        """
        psStr = ",".join(["%4.2f" % ps[i] for i in range(len(ps))])
        return "(%d),%s" % (session.id, psStr)
       
    def reportSocorroFormat(self, semester):
        "A report for comparing pressures of each session w/ Socorro's"

        # we're going to assume that we've already called getPressures,
        # we'll now use the stored results to create this.

        ss = Session.objects.filter(semester__semester = semester).order_by('id')
        for s in ss:
           # extract the lst pressures from the stored results
           cat, sc, ps, total = self.pressuresBySession[s.__str__()]
           print self.socorroFormat(s, ps)

    def reportSocorroWeatherFormat(self, semester):
        "A report for comparing weather pressures of each session w/ Socorro's"

        # we're going to assume that we've already called getPressures,
        # we'll now use the stored results to create this.

        ss = Session.objects.filter(semester__semester = semester).order_by('id')

        # this is completely inefficient, but who cares:
        for w in ['Poor', 'Good', 'Excellent']:
            print w
            for s in ss:
                if self.weatherPressuresBySession.has_key(s.__str__()) and \
                   self.pressuresBySession.has_key(s.__str__()):

                    # we need to know if time was allocated
                    cat, sc, ps, total = self.pressuresBySession[s.__str__()]
                    # socorro only cares about the sessions that have been allocated time
                    if cat != ALLOCATED:
                        ps = [0.0]*24
                    else:    
                        # extract the lst pressures from the stored results
                        wps = self.weatherPressuresBySession[s.__str__()]
                        ps = wps.getType(w)
                else:
                    ps = [0.0]*24

                print self.socorroFormat(s, ps)


    def getPressureWeights(self, category):
        catMap = {'RFI'     : self.computeRfiWeights
                , 'Optical' : self.computeOpticalNightWeights
                , 'Thermal' : self.computeThermalNightWeights
                }
        weights = PressureWeight.GetWeights(self.nextSemester.semester, category)
        compute = False
        if not weights:
            compute    = True
            weights, _ = catMap[category](self.nextSemesterStart
                                , (self.nextSemesterEnd - self.nextSemesterStart).days)
            PressureWeight.LoadWeights(self.nextSemester.semester, category, weights)
        return weights, compute

    def getPressureWeights(self, category):
        catMap = {'RFI'     : self.computeRfiWeights
                , 'Optical' : self.computeOpticalNightWeights
                , 'Thermal' : self.computeThermalNightWeights
                }
        weights = PressureWeight.GetWeights(self.nextSemester.semester, category)
        compute = False
        if not weights:
            compute    = True
            weights, _ = catMap[category](self.nextSemesterStart
                                , (self.nextSemesterEnd - self.nextSemesterStart).days)
            PressureWeight.LoadWeights(self.nextSemester.semester, category, weights)
        return weights, compute
           
    def initFlagWeights(self):
        "These are what you get from 12B"

        self.rfiWeights           = numpy.array(self.getPressureWeights('RFI')[0])
        self.opticalNightWeights  = numpy.array(self.getPressureWeights('Optical')[0])
        self.thermalNightWeights  = numpy.array(self.getPressureWeights('Thermal')[0])

    def getSocorroPressures(self, filename):
        
        f = open(filename, 'r')
        ls = f.readlines()
        pressures = {}
        for l in ls:
            # yields: ['A ', '12.2 ', '2.3 ', ..'34.55\n']
            parts = l.split('\t')
            # don't include grade
            ps = parts[1:]
            # get rid of trailing \n
            ps[23] = ps[23][:-2]
            #print ps
            # convert to array of floats
            ps = [float(p.strip()) for p in ps]
            pressures[parts[0].strip()] = ps
        return pressures

    def getSocLstPressure(self, filename):
        # parse lines like:
        # GBT13A-210 	GBT13A-210 - 1 	7.0
        f = open(filename, 'r')
        ls = f.readlines()
        pressures = {}
        total = 0.0
        for l in ls:
            parts = l.split('\t')
            pcode = parts[0].strip()
            session = parts[1].strip()
            ps = float(parts[2][:-2].strip())
            print session, ps
            pressures[session] = ps
            total += ps
        print "total: ", total    
        return pressures    

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

    # we can pass in a few args.  Yeah, I know this ain't pretty.
    carryOverUseNextSemester = True
    adjustWeatherBins = True
    if len(sys.argv) > 1:
        try:
            for arg in sys.argv[1:]:
                key = arg.split('=')[0]
                value = arg.split('=')[1]
                if key == '-carryOverUseNextSemester':
                    if value == 'True':
                        v = True
                    elif value == 'False':
                        v = False
                    else:
                        raise 'True or False Only'
                    carryOverUseNextSemester = v
                elif key == '-adjustWeatherBins':
                    if value == 'True':
                        v = True
                    elif value == 'False':
                        v = False
                    else:
                        raise 'True or False Only'
                    adjustWeatherBins = v
                else:
                    raise 'Unrecognized option: %s' % arg 
        except:
            print "Usage: python LstPressures.py [-carryOverUseNextSemester=[True,False]] [-adjustWeatherBins=[True,False]]"
            sys.exit(1)
       
    lst = LstPressures(carryOverUseNextSemester = carryOverUseNextSemester
                     , adjustWeatherBins = adjustWeatherBins
    #                 , today = datetime(2012, 3, 1)
                      )
    #s = Session.objects.get(id = 9758)                  
    #ps = lst.getPressures(sessions = [s])
    #ss = Session.objects.all().exclude(semester__semester = '13A')
    #ss = Session.objects.filter(proposal__pcode = 'GBT12B-385')
    #s = Session.objects.get(name = 'BB303-01')
    #ss = [s]
    #ps = lst.getPressures(ss)
    ps = lst.getPressures()
    #lst.reportSocorroFormat('14A')
    #lst.reportSocorroWeatherFormat('12B')
    lst.report()
    #lst.reportSemesterSummary()
    #lst.compareNewAstronomyPressures()
    #lst.compareNewAstronomyPressuresAll()


    #exp = []
    #eps = 0.001
    #for i in range(len(ps)):
    #    keys = ps[i].ke#ys()
    #    for k in keys:
    #        if not (abs(exp[i][k] - ps[i][k]) < eps):
    #            print "Lst: %f, Key: %s" % (i, k)
    #            print exp[i][k]
    #            print ps[i][k]
    #        assert abs(exp[i][k] - ps[i][k]) < eps


