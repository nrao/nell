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

#from django.core.management import setup_environ
#import settings
#setup_environ(settings)

from datetime import date, datetime, timedelta
from utilities import SLATimeAgent as sla
from utilities import TimeAgent

from pht.utilities    import *
from pht.models       import *
from scheduler.models import Observing_Type
from pht.tools.Sun    import Sun


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
        

    def __init__(self):

        self.hrs = 24
        self.bins = [0.0]*self.hrs

        self.pressures = [{'LST':float(i), 'Total':0.0} for i in range(24)]

        # for reporting
        self.badSess = []

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
        

        # for computing day light hours
        self.sun = Sun()
        
        # what example year do we compute flags for?
        self.year = 2012

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

    def getPressuresForSession(self, session):
        """
        Take into account different attributes of given session
        to return it's LST Pressure at each LST (0..23)
        """

        # first, is this session setup so we can do this?
        if session.target is None or session.allotment is None \
            or session.allotment.allocated_time is None \
            or session.target.min_lst is None \
            or session.target.max_lst is None:
            return []

        # TBF: is this right?
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
        ps = [(totalTime * ws[i] * fs[i]) / weightSum \
            for i in range(self.hrs)]

        return ps    

    def product(self, xs, ys):
        "multiply two vectors"
        # TBF: I know we shouldn't be writing our own one of these ...
        assert len(xs) == len(ys)
        zz = []
        for i in range(len(xs)):
            zz.append(xs[i] * ys[i])
        return zz    



    def getPressures(self):
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

        # how much time is available in a semester (6 months)?
        for p in self.pressures:
            p['Available'] = (180*24) / 24 

        # carry over
        ss = [s for s in Session.objects.all() \
            if s.dss_session is not None]
        self.getPressuresByType(ss, "Carryover")

        # TBF: maintenance and test time

        # new stuff, by all grade and weather type
        for weather in ['Poor', 'Good', 'Excellent']:
            for grade in ['A', 'B', 'C']:
                ss = Session.objects.filter(weather_type__type = weather
                                          , grade__grade = grade
                                          , dss_session = None
                                            )
                type = "%s_%s" % (weather, grade)
                self.getPressuresByType(ss, type)
       
        return self.pressures

    def getPressuresByType(self, sessions, type):
        "Get the pressures for the given sessions"

        # initilize this type's dictionary
        if not self.pressures[0].has_key(type):
            for p in self.pressures:
                p[type] = 0.0

        for s in sessions:
            
            ps = self.getPressuresForSession(s)
            if len(ps) > 0:
                for hr in range(self.hrs):
                    self.pressures[hr]['Total'] += ps[hr]
                    self.pressures[hr][type] += ps[hr]
            else:
                self.badSess.append(s)

            




