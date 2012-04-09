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
        self.badSess = []
        self.pressures = [] 

        # for computing day light hours
        self.sun = Sun()
        
        # what example year do we compute flags for?
        self.year = 2012

        self.nextSemester = DSSSemester.getFutureSemesters()[0]

        # TBF: get from DB?
        self.grades = ['A', 'B', 'C']
        self.weatherTypes = ['Poor', 'Good', 'Excellent']

        self.initPressures()
        self.initFlagWeights()


    def initPressures(self):
        # init our buckets
        self.totalPs  = numpy.array([0.0]*self.hrs)
        self.carryoverTotalPs = numpy.array([0.0]*self.hrs)
        self.carryoverPs = Pressures() 
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
        ws = [0.0] * self.hrs
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
            fs = self.product(fs, self.thermalNightWeights)
        elif session.flags.optical_night:
            fs = self.product(fs, self.opticalNightWeights)
        elif session.flags.rfi_night:
            fs = self.product(fs, self.rfiWeights)
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
        total = [0.0]*self.hrs
        for period in periods:
            ps = self.getPressuresFromPeriod(period)
            total = self.add(total, ps)
        return total

    def getSessionNextSemesterPeriods(self, session): 

        # TBF: for elective sessions, get one period
        # per elective group!
        return DSSPeriod.objects.filter( \
            session = session.dss_session
          , start__gt = self.nextSemester.start()
          , start__lt = self.nextSemester.end()).exclude( \
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
            or session.allotment.allocated_time is None \
            or session.target.min_lst is None \
            or session.target.max_lst is None:
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
        else:    
            totalTime = session.allotment.allocated_time

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
        weightSum = sum([(ws[i] * fs[i]) for i in range(self.hrs)])
        if weightSum != 0:
            ps = [(totalTime * ws[i] * fs[i]) / weightSum \
                for i in range(self.hrs)]
        else:
            ps = [0.0]*self.hrs

        return ps    

    def product(self, xs, ys):
        "multiply two vectors"
        # TBF: I know we shouldn't be writing our own one of these ...
        assert len(xs) == len(ys)
        zz = []
        for i in range(len(xs)):
            zz.append(xs[i] * ys[i])
        return zz    

    def add(self, xs, ys):
        "I know, I know, I should just use numpy"
        assert len(xs) == len(ys)
        zz = []
        for i in range(len(xs)):
            zz.append(xs[i] + ys[i])
        return zz    

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
            sessions = Session.objects.all()

        # fill the buckets
        for s in sessions:
            carryover = s.dss_session is not None
            if self.useCarryOverPeriods(s):
                ps = self.getPressuresFromSessionsPeriods(s)
            else:
                ps = self.getPressuresForSession(s, carryover)
            ps = numpy.array(ps)
            # accum pressure in total 
            self.totalPs += ps
            # We really keep carryover separate
            # Also track carryover by weather type
            if carryover:
                self.carryoverTotalPs += ps
                self.carryoverPs += self.weather.binSession(s, ps)
            else:
                wps = self.weather.binSession(s, ps)
                if s.grade is not None:
                    grade = s.grade.grade
                    self.gradePs[grade] += wps

        # now figure out the availability        
        changes = self.weather.getAvailabilityChanges(self.gradePs['A'])
        self.gradePs['A'] += changes

        # now convert the buckets to expected output
        return self.jsonDict()

    def jsonDict(self):
        """
        Convert our numpy arrays to the format expected by the client:
        A list of dictionaries, where LST is a key.
        """
       
        output = []
        for i in range(self.hrs):
            lstDict = dict(LST = i
                         , Total = self.totalPs[i] 
                         , Available = self.weather.availabilityTotal[i]
                         , Carryover = self.carryoverTotalPs[i] 
                          )
            for weather in self.weatherTypes: 
                availType = "Available_%s" % weather
                lstDict[availType] = self.weather.availability.getType(weather)[i]
                carryoverType = "Carryover_%s" % weather
                lstDict[carryoverType] = self.carryoverPs.getType(weather)[i]
                for grade in self.grades: 
                    type = "%s_%s" % (weather, grade)
                    lstDict[type] = self.gradePs[grade].getType(weather)[i]
            output.append(lstDict)
           
        self.pressures = output   
        return output        

    def report(self):
        "Report on pressure results - mostly for debugging."
        
        print self.formatResults('Total', self.totalPs)

        print ""                           
        print "Availablilty: "
        print self.formatResults('    Total'
            , self.weather.availabilityTotal)
        for w in self.weatherTypes:
            print self.formatResults('    %s' % w
                                   , self.weather.availability.getType(w))

        
        print ""
        print "Carryover: "
        print self.formatResults('    Total'
            , self.carryoverTotalPs)
        for w in self.weatherTypes:
            print self.formatResults('    %s' % w
                                   , self.carryoverPs.getType(w))
        
        print ""
        print "Next Semester Astromony: "
        for w in self.weatherTypes:
            print "    %s" % w
            for g in self.grades:
                print self.formatResults("      %s_%s" % (w, g)
                                       , self.gradePs[g].getType(w))
    def formatResults(self, label, results):
        label = "%18s" % label
        rs = ["%7.2f" % results[i] for i in range(len(results))]
        return label + ": " + ' '.join(rs)
            

    def initFlagWeights(self):

        # TBF: These get computed by methods in this class,
        # but no need to do it at start up every time.
        self.thermalNightWeights = [0.61643835616438358
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
                          ]
        self.opticalNightWeights = [0.50958904109589043
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
                            ]
        self.rfiWeights     = [0.54246575342465753
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
                             ] 
            


if __name__ == '__main__':
    lst = LstPressures()
    ps = lst.getPressures()
    lst.report()

    exp = [{'Available': 181.0, 'Carryover_Good': 10.408394268910172, 'Carryover': 36.364497468345398, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 0, 'Good_C': 0.0, 'Carryover_Poor': 0.5310742521060543, 'Excellent_A': 0.0, 'Carryover_Excellent': 9.5512514117673142, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 36.963962708987111, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 11.542857142857143, 'Carryover': 35.328571428571436, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 1, 'Good_C': 0.0, 'Carryover_Poor': 1.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 9.7857142857142865, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 35.928036669213149, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 12.037814666064842, 'Carryover': 36.251354091238156, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 2, 'Good_C': 0.0, 'Carryover_Poor': 1.989915046415397, 'Excellent_A': 0.0, 'Carryover_Excellent': 10.280671808921985, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 36.650819331879866, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 14.060054892191472, 'Carryover': 38.542898651699467, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 3, 'Good_C': 0.0, 'Carryover_Poor': 6.0343954986686548, 'Excellent_A': 0.0, 'Carryover_Excellent': 12.302912035048614, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 38.942363892341177, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 15.861502859244046, 'Carryover': 40.245781881855784, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 4, 'Good_C': 0.0, 'Carryover_Poor': 9.6372914327737984, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.104360002101187, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 40.645247122497494, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 16.042857142857144, 'Carryover': 41.100694322570469, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 5, 'Good_C': 0.0, 'Carryover_Poor': 10.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.285714285714286, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 41.500159563212179, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 16.042857142857144, 'Carryover': 48.139667475274983, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 6, 'Good_C': 0.0, 'Carryover_Poor': 10.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.285714285714286, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 48.539132715916693, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 16.042857142857144, 'Carryover': 56.874582206757943, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 7, 'Good_C': 0.0, 'Carryover_Poor': 10.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.285714285714286, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 57.156400388576124, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 16.042857142857144, 'Carryover': 65.609496938155829, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 8, 'Good_C': 0.0, 'Carryover_Poor': 10.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.285714285714286, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 65.89131511997401, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 16.042857142857144, 'Carryover': 73.742370627442142, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 9, 'Good_C': 0.0, 'Carryover_Poor': 10.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.285714285714286, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 74.024188809260323, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 15.152712290918069, 'Carryover': 74.930509997070018, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 10, 'Good_C': 0.0, 'Carryover_Poor': 9.9339960104075615, 'Excellent_A': 0.0, 'Carryover_Excellent': 14.252712290918067, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 75.2123281788882, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 4.75, 'Carryover': 60.551935262869563, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 11, 'Good_C': 0.0, 'Carryover_Poor': 9.5, 'Excellent_A': 0.0, 'Carryover_Excellent': 4.75, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 61.137649548583852, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 4.7179685338665873, 'Carryover': 67.271845167773591, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 12, 'Good_C': 0.0, 'Carryover_Poor': 9.4359370677331746, 'Excellent_A': 0.0, 'Carryover_Excellent': 4.7179685338665873, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 68.143273739202172, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 3.1294648609924351, 'Carryover': 73.297459341586062, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 13, 'Good_C': 0.0, 'Carryover_Poor': 6.2589297219848703, 'Excellent_A': 0.0, 'Carryover_Excellent': 3.1294648609924351, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 74.168887913014643, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.96023589156207612, 'Carryover': 73.40381971703269, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 14, 'Good_C': 0.0, 'Carryover_Poor': 1.9204717831241522, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.96023589156207612, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 74.592895347284809, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.0, 'Carryover': 71.478010945211139, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 15, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.0, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 72.667086575463259, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.0, 'Carryover': 69.680423175254418, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 16, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.0, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 71.069498805506541, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.0, 'Carryover': 61.56824350563312, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 17, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.0, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 62.957319135885228, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.0, 'Carryover': 56.011357933675626, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 18, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.0, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 57.11471927821345, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.0, 'Carryover': 53.106970202722692, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 19, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.0, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 53.924617261546231, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 0.8571428571428571, 'Carryover': 47.338222834044494, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 20, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 0.0, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 48.055869892868031, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 10.142857142857144, 'Carryover': 57.991446255859309, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 21, 'Good_C': 0.0, 'Carryover_Poor': 0.0, 'Excellent_A': 0.0, 'Carryover_Excellent': 9.2857142857142865, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 58.509093314682843, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 10.241716044750428, 'Carryover': 48.797937081600416, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 22, 'Good_C': 0.0, 'Carryover_Poor': 0.197717803786567, 'Excellent_A': 0.0, 'Carryover_Excellent': 9.38457318760757, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 49.315584140423951, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}
    , {'Available': 181.0, 'Carryover_Good': 10.392857142857144, 'Carryover': 42.782723697409359, 'Available_Poor': 90.5, 'Excellent_C': 0.0, 'Excellent_B': 0.0, 'Available_Excellent': 45.25, 'LST': 23, 'Good_C': 0.0, 'Carryover_Poor': 0.5, 'Excellent_A': 0.0, 'Carryover_Excellent': 9.5357142857142865, 'Good_A': 0.0, 'Good_B': 0.0, 'Total': 43.300370756232894, 'Poor_C': 0.0, 'Poor_B': 0.0, 'Poor_A': 0.0, 'Available_Good': 45.25}]

    assert exp == ps

