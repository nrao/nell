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

import numpy

from utilities import SLATimeAgent as sla
from utilities import TimeAgent
from utilities import TimeAccounting

from pht.utilities    import *
from pht.models       import *
from scheduler.models import Observing_Type
from pht.tools.Sun    import Sun
from scheduler.models import Semester as DSSSemester

HRS = 24

class Pressures(object):

    def __init__(self, poor = None, good = None, excellent = None):
 
        # init to hours of zero
        self.poor = poor if poor is not None else numpy.zeros(HRS)
        self.good = good if good is not None else numpy.zeros(HRS)
        self.excellent = excellent if excellent is not None else numpy.zeros(HRS)

    def __str__(self):
        return "Poor: %s\nGood: %s\nEx: %s\n" % (self.poor
                                               , self.good
                                               , self.excellent)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.poor.tolist() == other.poor.tolist()) \
           and (self.good.tolist() == other.good.tolist()) \
           and (self.excellent.tolist() == other.excellent.tolist())

    def __add__(self, other):
        "Override addition to add all the fields"
        return Pressures( \
            poor = self.poor + other.poor
          , good = self.good + other.good
          , excellent = self.excellent + other.excellent
        )

    def __sub__(self, other):
        "Override subtraction to add all the fields"
        return Pressures( \
            poor = self.poor - other.poor
          , good = self.good - other.good
          , excellent = self.excellent - other.excellent
        )  

    def __mul__(self, other):
        "Override multiplication to multiply all the fields"
        return Pressures( \
            poor = self.poor * other.poor
          , good = self.good * other.good
          , excellent = self.excellent * other.excellent
        )

    def setType(self, type, value):
        self.__setattr__(type.lower(), value)

    def getType(self, type):
        return self.__getattribute__(type.lower())

    def allTypes(self):
        "Ignore the pressure distinctions by weather type"
        return self.poor + self.good + self.excellent

    def total(self, gc = False, type = None):
        "What are all these LST pressures, added up?"
        total = 0.0
        if type is None:
            types = ['poor', 'good', 'excellent']
        else:
            types = [type]
        for t in types:
            if not gc:
                total += sum(self.getType(t))
            else:
                # just sum up across the galactic center
                total += sum(self.getType(t)[15:21])
        return total        

class LstPressureWeather(object):

    """
    From Toney Minter:

    Calculating the Fraction of Time Going Against Different Weather Categories
---------------------------------------------------------------------------
The weather group is determined by receiver:
KFPA, MBA and W are in the excellent weather group.
X, Ku, Ka and Q are in the good weather group.
All others (342, 450, 600, 800, 1070, L, S, and C) are in the poor
weather group.

Let g be the fraction of windowed session that are observed away from their
default date.  (These are the sessions that get moved to poor weather days.)
The value of g is an input parameter for a whole semester.  The value of
g is between 0.0 and 1.0.  This value will need to be a parameter we 
input for a given semster.

Let f_poor, f_good and f_excellent be the fraction of time available for 
each weather group.  We get to set what these fractions are for a given
semester and the values are between 0.0 and 1.0.

An elective session will have m observations occur within n days.  The
fraction of observations occuring in the proper weather conditions is
given by h, were

h = (1 - m/n)


T_i is determined from the LST Pressure Calculation formula.

For weather monitoring sessions with widows less than or equal to 3 days:
T_poor_i = T_i * f_poor
T_good_i = T_i * f_good
T_excellent_i = T_i * f_excellent

For monitoring sessions with windows greater than 3 days:
T_poor_i = T_i * g  +  T_i * f_poor * (1 - g)
T_good_i = T_i * f_good * (1 - g)
T_excellent_i = T_i * f_excellent * (1 - g)


For poor weather elective sessions:
T_poor_i = T_i * h  +  T_i * f_poor * (1 - h)
T_good_i = T_i * f_good * (1 - h) 
T_excellent_i = T_i * f_excellent * (1 - h)

For good weather elective sessions:
T_good_i = T_i * h + T_i * f_good * (1 - h) / (f_good + f_excellent)
T_excellent_i = T_i * f_excellent * (1 - h) / (f_good + f_excellent)

For excellent weather elective sessions:
T_excellent_i = T_i

For open sessions the time should go only to the weather condition 
set for the session in the GB PHT.

For poor weather fixed sessions:
T_poor_i = T_i * f_poor
T_good_i = T_i * f_good
T_excellent_i = T_i * f_excellent

For good weather fixed sessions:
T_good_i = T_i * f_good / (f_good + f_excellent)
T_excellent_i = T_i * f_excellent / (f_good + f_excellent)

For excellent weather fixed sessions:
T_excellent_i = T_i

    """

    def __init__(self
               , semester = '12A'
               , avPoor = 0.50
               , avGood = 0.25
               , avExcellent = 0.25
               , windowFrac = 0.5
                ):

        self.semester = DSSSemester.objects.get(semester = semester)
        self.numDays = (self.semester.end() - self.semester.start()).days

        self.wPoor = WeatherType.objects.get(type = 'Poor')
        self.wGood = WeatherType.objects.get(type = 'Good')
        self.wExcellent = WeatherType.objects.get(type = 'Excellent')

        self.sFixed = SessionType.objects.get(type = 'Fixed')
        self.sWindowed = SessionType.objects.get(type = 'Windowed')
        self.sElective = SessionType.objects.get(type = 'Elective')

        # TBF: get rid of 4th weather type
        self.wTypes = ['Poor', 'Good','Excellent']
        self.grades = ['A', 'B', 'C']
        self.hrs = 24

        self.pressures = Pressures() 


        self.shares = dict(Poor = avPoor
                         , Good = avGood
                         , Excellent = avExcellent
                          )
        self.windowFrac = windowFrac                  
        self.initAvailability()

    def initAvailability(self):                          
        """
        Initial availability is the number of hours availabe split
        up by each weather types share
        """
        totalAvail = (self.numDays * 24.) / 24. 
        self.availabilityTotal = numpy.array([totalAvail]*self.hrs)
        self.availability = Pressures()
        for wt in self.wTypes:
            available = numpy.array([totalAvail*self.shares[wt]]*self.hrs)
            self.availability.setType(wt, available)

    def binSession(self, session, pressures):
 
        if session.session_type is None:
            return Pressures() 

        typeMap = {self.sFixed    : self.binFixedSession
                 , self.sWindowed : self.binWindowedSession
                   # TBF: for now, treat Electives like Fixed 
                 , self.sElective : self.binFixedSession
                 }
        return typeMap.get(session.session_type, self.binOpenSession)(session, numpy.array(pressures))

    def binOpenSession(self, session, pressure):
        wType = session.weather_type.type
        ps = Pressures()
        ps.setType(wType, pressure)
        return ps

    def binFixedSession(self, session, pressure):
        wType = session.weather_type
        ps = Pressures()
        if wType == self.wPoor:
            # get's distributed evenly
            for wt in self.wTypes:
                ps.setType(wt, pressure*self.shares[wt])

        elif wType == self.wGood:
            base = self.shares[self.wGood.type] \
                 + self.shares[self.wExcellent.type] 
            # good gets this share     
            f = self.shares[self.wGood.type] / base
            ps.good = pressure * f
            # excellent gets this share
            f = self.shares[self.wExcellent.type] / base
            ps.excellent = pressure * f
        elif wType == self.wExcellent:
            # excellent gets it all
            ps.setType(self.wExcellent.type, pressure)
        return ps    
            
    def binWindowedSession(self, session, pressure):
        # depends on window size (days)
        wsize = session.monitoring.window_size
        ps = Pressures()
        if wsize <= 3: 
            # get's distributed evenly - just like a fixed in poor wthr.
            for wt in self.wTypes:
                ps.setType(wt, pressure*self.shares[wt])
        else:
            # take into account the extra chance this window has 
            # of being scheduled like open
            wf = 1 - self.windowFrac
            ps.poor = (pressure*self.windowFrac) + \
               (pressure * wf * self.shares[self.wPoor.type])
            ps.good = pressure * wf * self.shares[self.wGood.type]   
            ps.excellent = pressure * wf * self.shares[self.wExcellent.type]   
        return ps

    def binElectiveSession(self, session, pressure):
        # TBF: where do we get these from, the periods?
        return Pressures() 

