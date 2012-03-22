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

HRS = 24

class Pressures(object):

    def __init__(self
        , poor = numpy.array([0.]*HRS)
        , good = numpy.array([0.]*HRS)
        , excellent = numpy.array([0.]*HRS)):

        self.poor = poor
        self.good = good
        self.excellent = excellent

    def __str__(self):
        return "Poor: %s\nGood: %s\nEx: %s\n" % (self.poor
                                               , self.good
                                               , self.excellent)
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
  
    def __mul__(self, other):
        "Override multiplication to multiply all the fields"
        return Pressures( \
            poor = self.poor * other.poor
          , good = self.good * other.good
          , excellent = self.excellent * other.excellent
        )

    def setType(self, type, value):
        self.__setattr__(type.lower(), value)

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


For all sessions:
If the time in poor weather for sessions given a Group A ranking exceeds
the time available in a semester for the poor weather then the amount of
time exceeding the poor weather semester time will count against good
and excellent weather in the ratio of f_good and f_excellent.  For example
if T_poor_i = 1000 and T_poor_available_i = 600 then the extra 400 hours 
is split amongst T_good_availabe_i and T_excellent_available_i.  The fraction
going to the good weather is determined by

(T_poor_i - T_poor_available_i ) * f_good / (f_good + f_excellent)

and the fraction going to excellent weather is determined by

(T_poor_i - T_poor_available_i ) * f_excellent / (f_good + f_excellent)

The faction of poor weather time is then capped at

T_poor_i = T_poor_available_i

Again, note that this is only for time assigned to Group A.
    """

    def __init__(self
               , avPoor = 0.50
               , avGood = 0.25
               , avExcellent = 0.25
                ):

        self.wPoor = WeatherType.objects.get(type = 'Poor')
        self.wGood = WeatherType.objects.get(type = 'Good')
        self.wExcellent = WeatherType.objects.get(type = 'Excellent')

        # TBF: get rid of 4th weather type
        self.wTypes = ['Poor', 'Good','Excellent']
        self.grades = ['A', 'B', 'C']
        self.hrs = 24
        self.pressures = Pressures() 
       
        self.shares = dict(Poor = avPoor
                         , Good = avGood
                         , Excellent = avExcellent
                             )

    def binSessionPressureWeather(self, session, pressures):

        # in case pressures is a list
        pressures = numpy.array(pressures)

        type = session.session_type.type
        if type == 'open':
            ps = self.binOpenSession(session, pressure)
        elif type == 'fixed':
            ps = self.binFixedSession(session, pressure)
        
        # accumulate the results
        self.pressures += ps

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
            good = pressure * f
            ps.setType(self.wGood.type, good)
            # excellent gets this share
            f = self.shares[self.wExcellent.type] / base
            ex = pressure * f
            ps.setType(self.wExcellent.type, ex)
        elif wType == self.wExcellent:
            # excellent gets it all
            ps.setType(self.wExcellent.type, pressure)
        return ps    
            
