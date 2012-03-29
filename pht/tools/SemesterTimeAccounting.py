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

from datetime import datetime, date, timedelta

from pht.models       import *
from pht.utilities    import *

from scheduler.models import Project
from scheduler.models import Observing_Type 
from scheduler.models import Period as DSSPeriod
from scheduler.models import Semester as DSSSemester

from utilities import AnalogSet
from utilities import TimeAgent
from utilities import SLATimeAgent as sla

from pht.tools.Sun import Sun

class SemesterTimes(object):

    """
    This class makes it easier for us to deal with the fact that
    for every time quantity we want to calculate, we will
    also want to calculate this quantity for the Galactic Center time.
    """
 
    def __init__(self, total = None, gc = None):

        total = total if total is not None else  Times(type = 'Total')
        gc = gc if gc is not None else  Times(type = 'GC')

        self.total = total 
        # Galactic Center time
        self.gc = gc

    def __str__(self):
        return "%s; %s" % (self.total, self.gc)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        "Override addition to add all the fields"
        return SemesterTimes( \
            total = self.total + other.total
          , gc = self.gc + other.gc
        )

    def __sub__(self, other):
        "Override addition to add all the fields"
        return SemesterTimes( \
            total = self.total - other.total
          , gc = self.gc - other.gc
        )

    def __eq__(self, other):
        "Override equality to compare all the fields"
        return self.total == other.total \
            and self.gc == other.gc

    def check(self):
        self.total.check()
        self.gc.check()

class Times(object):

    """
    This class simply makes the management of the different
    quantities we'll be calculating a lot easier.
    """
    
    def __init__(self
        , type = None
        , total = 0.0
        , lowFreq = 0.0
        , hiFreq1 = 0.0
        , hiFreq2 = 0.0
        ):

        self.type = type
        self.total = total
        self.lowFreq = lowFreq 
        self.hiFreq1 = hiFreq1
        self.hiFreq2 = hiFreq2

    def __str__(self):

        return "Type: %8s, Total: %8.2f, LF: %8.2f, HF1: %8.2f, HF2: %8.2f" % \
            (self.type, self.total, self.lowFreq, self.hiFreq1, self.hiFreq2)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        "Override addition to add all the fields"
        return Times( \
            type = self.type
          , total = self.total + other.total
          , lowFreq = self.lowFreq + other.lowFreq
          , hiFreq1 = self.hiFreq1 + other.hiFreq1
          , hiFreq2 = self.hiFreq2 + other.hiFreq2
        )

    def __sub__(self, other):
        "Override subtraction to subtract all the fields"
        return Times( \
            type = self.type
          , total = self.total - other.total
          , lowFreq = self.lowFreq - other.lowFreq
          , hiFreq1 = self.hiFreq1 - other.hiFreq1
          , hiFreq2 = self.hiFreq2 - other.hiFreq2
        )

    def __eq__(self, other):
        "Override equality to compare all the fields"
        return self.eq(self.total, other.total) \
            and self.eq(self.lowFreq, other.lowFreq) \
            and self.eq(self.hiFreq1, other.hiFreq1) \
            and self.eq(self.hiFreq2, other.hiFreq2)

    def factor(self, f):
        "Create new object with all fields multiplied by factor."
        return Times( \
            total = self.total * f
          , lowFreq = self.lowFreq * f
          , hiFreq1 = self.hiFreq1 * f
          , hiFreq2 = self.hiFreq2 * f
        )

    def eq(self, v1, v2):
        "Are these floats almost equal?"
        eps = 1e-2
        return abs(v1 - v2) < eps

    def check(self):
        assert self.total == (self.lowFreq + self.hiFreq1 + self.hiFreq2)

class SemesterTimeAccounting(object):

    """
    This class is responsible for determining many complicated
    time accounting quantities.
    For each quantity, there are two types: total, and those covered
    by the Galactic Center.
    """

    def __init__(self, semester):


        self.sun = Sun()

        self.semester = DSSSemester.objects.get(semester = semester)

        self.timeRange = (self.semester.start()
                        , self.semester.end())
        self.published = None

        # Galactic Center goes from 15 to 20 hours [,)
        self.gcHrs = (15, 21) 

        # initialize all the buckets we'll be calculating
        self.totalAvailableHrs = SemesterTimes() 
        self.maintHrs = SemesterTimes()
        self.shutdownHrs = SemesterTimes()
        self.testHrs = SemesterTimes()
        self.astronomyAvailableHrs = SemesterTimes()
        self.carryOver = {}
        self.newAstronomyGradeAHrs = SemesterTimes()
        self.newAstronomyAllGradeHrs = SemesterTimes()

        self.lowFreqPercent = 0.50
        self.hiFreq1Percent = 0.25
        self.hiFreq2Percent = 0.25

        # how to map from session freq type to time category?
        self.freq2key = {'LF' : 'lowFreq'
                       , 'HF1' : 'hiFreq1'
                       , 'HF2' : 'hiFreq2'
                        }

        self.grades = ['A', 'B', 'C']                

    def checkTimes(self):
        "Basic check that everything adds up"

        self.totalAvailableHrs.check() 
        self.maintHrs.check() 
        self.shutdownHrs.check() 
        self.testHrs.check() 
        self.astronomyAvailableHrs.check() 
        
        preAssigned = self.maintHrs + self.shutdownHrs + self.testHrs
        avail = preAssigned  + self.astronomyAvailableHrs
        assert avail.total == self.totalAvailableHrs.total

    def calcTotalAvailableHours(self):

        # how many hours in this semester?
        days = self.getSemesterDays(self.semester)
        totalHrs = days * 24
        totalGCHrs = self.getGCHrs(totalHrs)
        total = Times(type = 'Total'
                    , total = totalHrs
                    , lowFreq = totalHrs*self.lowFreqPercent
                    , hiFreq1 = totalHrs*self.hiFreq1Percent
                    , hiFreq2 = totalHrs*self.hiFreq2Percent
                     )
        gc = Times(type = 'GC'
                 , total = self.getGCHrs(totalHrs)
                 , lowFreq = self.getGCHrs(total.lowFreq)
                 , hiFreq1 = self.getGCHrs(total.hiFreq1)
                 , hiFreq2 = self.getGCHrs(total.hiFreq2)
                     )         
        return  SemesterTimes(total = total, gc = gc)  

    def calculateTimeAccounting(self):

        self.published = datetime.now()

        self.totalAvailableHrs =  self.calcTotalAvailableHours()  

        # how much has been pre-assigned for this semester?
        # first, find the periods
        self.maintPeriods = self.getMaintenancePeriods()
        self.shutdownPeriods = self.getShutdownPeriods()
        self.testSessions = self.getTestSessions()

        # now calculate their hours
        self.maintHrs = self.getHours(self.maintPeriods)
        self.shutdownHrs = self.getHours(self.shutdownPeriods)
        self.testHrs = self.getSessionsHours(self.testSessions)

        # so, how much does that leave left for real astronomy?
        self.astronomyAvailableHrs = None
        # add up maintHrs, shutdownHrs, testHrs, total and GC, 
        # then subtract those from the totalAvailableHrs
        preAssigned = self.maintHrs + self.shutdownHrs + self.testHrs
        self.astronomyAvailableHrs = self.totalAvailableHrs - preAssigned             
        # now, what's the carry over?
        self.carryOverSessions = self.getCarryOverSessions()
        self.carryOver = self.getCarryOver(self.carryOverSessions)

        # and how does THAT affect time available?
        self.newAstroAvailGradeAHrs = \
            self.getNewAstroAvailableTime(self.carryOver
                                         , self.astronomyAvailableHrs
                                         , ['A']
                                          )

        self.newAstroAvailAllGradeHrs = \
            self.getNewAstroAvailableTime(self.carryOver
                                         , self.astronomyAvailableHrs
                                         , self.grades
                                          )

    def getNewAstroAvailableTime(self, carryover, available, grades):

        carryOverTotals = SemesterTimes()
        for g in grades:
            times = carryover[g]['times']
            fixed = carryover[g]['fixed']
            carryOverTotals += times + fixed
        return available - carryOverTotals

    def report(self):
        "Prints out simple version of the results."

        print "Summary of Semester %s" % self.semester.semester
        print "As of %s" % datetime.now()
        print ""
        print "Time Analysis for Semester %s" % self.semester.semester
        print "%s to %s" % (self.semester.start(), self.semester.end())
        print ""

        print "Hours available in the Semester: "
        print "%s" % self.totalAvailableHrs.total
        print "%s" % self.totalAvailableHrs.gc

        print ""
        print "Maint: %s" % self.maintHrs.total
        print "       %s" % self.maintHrs.gc
        print "Shutd: %s" % self.shutdownHrs.total
        print "       %s" % self.shutdownHrs.gc
        print "Tests: %s" % self.testHrs.total
        print "       %s" % self.testHrs.gc
        print ""

        print "Available for Astronomy = %5.2f, GC[%5.2f]" % \
            (self.astronomyAvailableHrs.total.total
           , self.astronomyAvailableHrs.gc.total)

        print ""
        print "Available for ALL Astronomy during %s" % \
            self.semester.semester    
        print "%s" % self.astronomyAvailableHrs.total
        print "%s" % self.astronomyAvailableHrs.gc

        print ""
        print "Backlog committments for %s" % self.semester.semester
        for g in self.grades:
            tt = self.carryOver[g]['fixed'].total.total + \
                 self.carryOver[g]['times'].total.total
            gt = self.carryOver[g]['fixed'].gc.total + \
                 self.carryOver[g]['times'].gc.total
            print "Group %s Time:" % g
            print "    Fixed: %s" % self.carryOver[g]['fixed'].total
            print "           %s" % self.carryOver[g]['fixed'].gc
            print "    Rest:  %s" % self.carryOver[g]['times'].total
            print "           %s" % self.carryOver[g]['times'].gc
            print "Group %s total Hours = %5.2f GC[%5.2f]" % (g, tt, gt)
            print ""
            
        print "Available for NEW Astronomy during %s" % self.semester.semester
        print "Includes only Group A carry over time:"
        print "    %s" % self.newAstroAvailGradeAHrs.total
        print "    %s" % self.newAstroAvailGradeAHrs.gc
        print ""
        print "Includes Groups A, B and C carry over time:"
        print "    %s" % self.newAstroAvailAllGradeHrs.total
        print "    %s" % self.newAstroAvailAllGradeHrs.gc
        print ""

        #self.debugReport()

    def debugReport(self):
        "For debugging"

        print "DETAILS: "
        print "Maint. Periods: "
        total = 0
        for p in self.maintPeriods:
            print p 
            total += p.duration
        print "Total maint periods: ", total    

        print "Shutdown Periods: "
        total = 0
        for p in self.shutdownPeriods:
            print p 
            total += p.duration
        print "Total shutdown periods: ", total    

        print "Test Sessions: "
        for s in self.testSessions:
            print s

        print "Carryover Sessions:"
        total = 0
        totals = {'A' : 0.0, 'B' : 0.0, 'C' : 0.0, 'None' : 0.0}
        for s in self.carryOverSessions:
            print s, s.session_type, s.grade, s.next_semester.time 
            if s.grade is not None:
                totals[s.grade.grade] += s.next_semester.time
            else:
                totals['None'] += s.next_semester.time
            total = s.next_semester.time
        print "Total Carryover Time: ", total, totals    

    def getSemesterDays(self, semester = None):    
        "How many days in the given semester?"
        if semester is None:
            s = self.semester
        else:    
            s = DSSSemester.objects.get(semester = semester)
        return (s.end() - s.start()).days

    def getGCHrs(self, hrs):
        """
        Given a uniformly distributed number of hours, how many would
        fall within the Galactic Center range?
        """
        gcHrs = (self.gcHrs[1] - self.gcHrs[0]) 
        return hrs * (gcHrs/24.)

    def getMaintenancePeriods(self):
        "What maintenance periods have been scheduled for this semester?"
        return self.getProjectPeriods('Maintenance')

    def getShutdownPeriods(self):
        "What shutdown periods have been scheduled for this semester?"
        return self.getProjectPeriods('Shutdown')

    def getProjectPeriods(self, pcode):    
        ps = DSSPeriod.objects.filter( \
            session__project__pcode = pcode
          , start__gt = self.semester.start()
          , start__lt = self.semester.end()).exclude( \
              state__name = 'Deleted').order_by('start')    
        return ps 

    def getTestSessions(self):
        "What are the testing sessions for this semester?"
        sem = self.semester.semester
        testing = Observing_Type.objects.get(type='testing')
        commissioning = Observing_Type.objects.get(type='commissioning')
        calibration = Observing_Type.objects.get(type = 'calibration')
        return Session.objects.filter(Q(semester__semester = sem) 
                                    , Q(observing_type = testing) \
                                    | Q(observing_type = commissioning)\
                                    | Q(observing_type = calibration))


    def getHours(self, periods):

        allHrs = SemesterTimes()            
        for p in periods:
            hrs = self.getPeriodHours(p)
            # update the totals
            allHrs += hrs

        return allHrs        
            
    def getPeriodHours(self, period):
        """
        Determines how much of ther various types of time these periods 
        add up.  These types include:
           * how much lies in the galactic center?
           * how much gets billed to each frequency bin?
        Uses their duration, since we'll be looking at mostly pending
        periods, who won't have any time billed yet.
        """

        dur = period.duration
        start = period.start
        end = period.end()

        # Turns out that we FOR NOW, we don't care about day/night
        #dayHrs, nightHrs = self.getHrsInDayTime(start, end)
        gcHrs, nonGCHrs  = self.getHrsInGC(start, end)
        gcFrac = gcHrs / dur

        lowFreqHrs = self.lowFreqPercent * dur
        hiFreq1Hrs = self.hiFreq1Percent * dur
        hiFreq2Hrs = self.hiFreq2Percent * dur

        total= Times(type = 'total'
                  , total = dur
                  , lowFreq= lowFreqHrs
                  , hiFreq1= hiFreq1Hrs
                  , hiFreq2= hiFreq2Hrs
                  )       

        gc = total.factor(gcFrac)
        gc.type = 'gc'
        
        return SemesterTimes(total = total, gc = gc)

    def getHrsInDayTime(self, start, end):
        "Split up given time range by PTCS day and night time hours."
        dur = TimeAgent.dtDiffHrs(start, end)
        startDate = date(start.year, start.month, start.day)
        #rise, set = self.sun.getRiseSet(date1)
        # cast a wide net: compute the rise and set times for any days
        # that might be covered by the given time range
        days = (end - start).days + 2
        dayTimes = []
        for day in range(days):
            dt = startDate + timedelta(days = day)
            dayTimes.append(self.sun.getPTCSRiseSet(dt))
        # where does our given time range intersect with day time?    
        ints = AnalogSet.intersects([dayTimes, [(start, end)]])
        if len(ints) > 0:
            # some day time
            day = 0.0
            for intersection in ints:
                td = intersection[1] - intersection[0]
                day += TimeAgent.timedelta2frachours(td)
            # the rest must be night time    
            night = abs(dur - day) 
        else:
            # our range is all night time.
            day = 0.0
            night = dur 
        return (day, night)

    def fltEqual(self, flt1, flt2):
        eps = 1e-3
        return abs(flt1 - flt2) < eps

    def getHrsInGC(self, start, end):
        "Split up given time range by Galactic Center overlap."
        dur = TimeAgent.dtDiffHrs(start, end)
        # convert local time range to LST range
        lstStart = sla.Absolute2RelativeLST(start)
        lstEnd = sla.Absolute2RelativeLST(end)
        # be simplistic about the overalp
        if lstEnd < lstStart:
            lstEnd += 24.0
        
        gcHrs, nonGcHrs = self.findOverlap((lstStart, lstEnd), self.gcHrs, dur)
        return (gcHrs, nonGcHrs)

    def findOverlap(self, a, b, dur):
        """Utility for returning the fraction of given duration that
        is spent in the overlap of the two given tuples.
        """
        a1, a2 = a
        b1, b2 = b
        # what's the overlap between them (like the Galactice Center)?
        if AnalogSet.overlaps(a, b):
            ints = AnalogSet.intersect(a, b)
            # if our range is entirely in overlap, avoid calculations
            if self.fltEqual(ints[0], a1) \
                and self.fltEqual(ints[1], a2):
                overlap = dur
                nonOverlap = 0
            else:    
               # otherwise we need to convert back to duration - 
               # one way to do this is via fractions
               frac = (ints[1] - ints[0]) / (a2 - a1)
               overlap = dur * frac
               nonOverlap = (1.0 - frac) * dur
        else:
            overlap = 0
            nonOverlap = dur
            
        return (overlap, nonOverlap)

    def getSessionsHours(self, ss):

        all = SemesterTimes()
        for s in ss:
            t = self.getSessionHours(s)
            all += t
        return all

    def getSessionHours(self, s):
        "PHT Sessions simply bill to the freq they are at."

        t = Times()          
        timeType = self.freq2key[s.determineFreqCategory()]

        # add alloted time to this time type 
        t.__setattr__(timeType, s.allotment.allocated_time)

        # add to other categories
        t.total  = s.allotment.allocated_time
        gcHrs, nonGCHrs = self.getGCHoursFromSession(s)
        gcFrac   = gcHrs / (gcHrs + nonGCHrs) 
        gc       = t.factor(gcFrac)

        return SemesterTimes(total = t, gc = gc)

            
            
    def getGCHoursFromSession(self, session):
        # use max/min LST as compared to the Galctic Center
        s = (rad2hr(session.target.min_lst)
           , rad2hr(session.target.max_lst))
        dur = session.allotment.allocated_time
        gcHrs, nonGCHrs = self.findOverlap(s, self.gcHrs, dur)
        return gcHrs, nonGCHrs                                 

    def getCarryOverSessions(self):
        """
        Returns any sessions that have a corresponding
        DSS Session and won't be complete next semester.
        In other words, they contribute to carry over.
        """

        # TBF: how to do the not None query?
        ss = Session.objects.filter(next_semester__complete = False).order_by('name')
        return [s for s in ss if s.dss_session is not None]
            
    def getCarryOver(self, sessions):
        """
        How much do these sessions contribute to the 
        carryover, divided by Grade and Frequency,
        among other things.
        """

        carryOver = {}
        for g in ['A', 'B', 'C']:
            grade = SessionGrade.objects.get(grade = g)
            ss = [s for s in sessions if s.grade == grade]
            carryOver[g] = self.getCarryOverForGrade(ss)
        return carryOver    

    def getCarryOverForGrade(self, sessions):
        "Carry over is divided between fixed and everything else"

        fixed = SessionType.objects.get(type = 'Fixed')
        fixedSess = [s for s in sessions if s.session_type == fixed]
        otherSess = [s for s in sessions if s.session_type != fixed]

        fixed = self.getCarryOverTimes(fixedSess) 
        st = self.getCarryOverTimes(otherSess)

        return dict(fixed = fixed
                  , times = st)

    def getCarryOverTimes(self, ss):

       sts = SemesterTimes()
       for s in ss:
          st = self.getCarryOverForSession(s)
          sts += st 
       return sts    

    def getCarryOverForSession(self, s):
        """
        How much will the given session contribute to this
        semester's carryover?
        """

        # what freq to bill this against?
        timeType = self.freq2key[s.determineFreqCategory()]

        # add next semester's time to this time type 
        t = Times(type = 'Total')          
        time = s.next_semester.time
        t.__setattr__(timeType, time)
        t.total = time

        # how much of this time is Galactic Center time?
        gcHrs, nonGcHrs = self.getGCHoursFromSession(s)
        if (gcHrs + nonGcHrs) > 0.0:
            gcFrac = gcHrs / (gcHrs + nonGcHrs)
        else:
            gcFrac = 0.0
        gc = t.factor(gcFrac)
        gc.type = 'GC'

        return SemesterTimes(total = t, gc = gc) 
        
if __name__ == '__main__':
    ta = SemesterTimeAccounting(semester = '12B') 
    ta.calculateTimeAccounting()
    ta.report()
       
       


    
        
