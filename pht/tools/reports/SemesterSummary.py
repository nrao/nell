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

from datetime      import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units  import inch

from pht.models import *
from scheduler.models import Semester as DSSSemester
from Report import Report

from pht.tools.LstPressures import LstPressures
 
class SemesterSummary(Report):

    """
    This class is responsible for producing a report on the overall
    summary of a given semester.
    """

    def __init__(self, filename, semester = None):
        super(SemesterSummary, self).__init__(filename)

        self.semester = semester

        # In order to calculate the pressures for the right semester
        # we need to tell this class that we are a few days before
        # this semester starts:
        s = DSSSemester.objects.get(semester = semester)
        today = (s.start() - timedelta(days = 10))
        self.lst = LstPressures(today = today)

        self.title = 'Semester Summary'

    def report(self, semester = None):

        if semester is not None:
            self.semester = semester

        # crunch the numbers we need for this report
        self.lst.getPressures()
        
        self.title = self.title if self.semester is None else \
                     self.title + " for Semester %s" % self.semester


        t0 = self.getIntroTable()
        t1 = self.getStartingHoursTable()
        t2 = self.getAvailableAllAstronomyTable()
        t3 = self.getAvailableNewAstronomyTableGradeA()
        t4 = self.getAvailableNewAstronomyTable()

        b = self.getBreak()

        tables = [t0, b, t1, b, t2, b]
        for g in self.lst.grades: 
            tables.append(self.getBacklogTableForGrade(g))
            tables.append(b)
        tables.extend([t3, b, t4, b])    

        # write the document to disk (or something)
        self.doc.build(tables
                    , onFirstPage = self.makeHeaderFooter
                    , onLaterPages = self.makeHeaderFooter)

    def getIntroTable(self):

        data = [[Paragraph('Time Analysis for Semester %s' % self.semester, self.styleSheet)
                ]
              , [Paragraph('%s - %s' % (self.lst.timeRange), self.styleSheet)]
              , [Paragraph('As of %s' % self.lst.published, self.styleSheet)]
               ]

        t = Table(data, colWidths = [300])

        t.setStyle(self.tableStyle)
        
        return t

    def getStartingHoursTable(self):

        hrsInSemester = (self.lst.weather.availability.total()
                       , self.lst.weather.availability.total(gc = True))
        hrsMaint      = (self.lst.maintenancePs.total()
                       , self.lst.maintenancePs.total(gc = True))
        hrsShutdown   = (self.lst.shutdownPs.total()
                       , self.lst.shutdownPs.total(gc = True))
        hrsTests      = (self.lst.testingPs.total()
                       , self.lst.testingPs.total(gc = True))

        data = [self.hrsPg('Hours in Semester', hrsInSemester)
              , self.hrsPg('Maintenance Hours', hrsMaint)
              , self.hrsPg('Test, Comm, Calib Hours', hrsTests)
              , self.hrsPg('Shutdown Hours', hrsShutdown)
                ]

        t = Table(data, colWidths = [100, 100, 100])
        t.setStyle(self.tableStyle)
        return t

    def getAvailableAllAstronomyTable(self):
        txt = 'Available for ALL Astronomy during %s' % self.semester
        return self.getAvailableTable(txt
                                    #, self.ta.astronomyAvailableHrs)
                                    , self.lst.postMaintAvailabilityPs)

    def getBacklogTableForGrade(self, grade):

        g = grade
        t = True
        hrsFixed = (self.lst.carryoverGradePs['fixed'][g].total()
                  , self.lst.carryoverGradePs['fixed'][g].total(gc = t))
        hrsTotal = (self.lst.carryoverGradePs['total'][g].total()
                  , self.lst.carryoverGradePs['total'][g].total(gc = t))

        data = [[self.pg('Group %s time' % grade)]
               , self.hrsPg('Hours Total', hrsTotal)  
               , self.hrsPg('Fixed Hours', hrsFixed)
               ]

        r = 'rest'
        for w in self.lst.weatherTypes:
            w = w.lower()
            hrs = (self.lst.carryoverGradePs[r][g].total(type = w)
                 , self.lst.carryoverGradePs[r][g].total(type = w
                                                       , gc = t))
            label = 'Hours for %s' % self.lst.weatherMap[w]        
            data.append(self.hrsPg(label, hrs))

        t = Table(data, colWidths = [100, 100, 100])
        t.setStyle(self.tableStyle)
        return t

    def getAvailableHrs(self, available):
        "Reorganize our data."

        hrsTotal = (available.total(), available.total(gc = True))
        hrs = []
        for w in self.lst.weatherTypes:
            w = w.lower()
            hrs.append((available.total(type = w)
                      , available.total(type = w, gc = True)))

        return (hrsTotal, hrs[0], hrs[1], hrs[2])            
        
    def getAvailableTable(self, text, available):
        "Worker function for creating a table of available hours."
        hrsTotal, hrsLowFreq, hrsHiFreq1, hrsHiFreq2 = \
            self.getAvailableHrs(available)

        data = [[self.pg(text)
                ]
              , self.hrsPg('Hours Total', hrsTotal)  
              , self.hrsPg('Hours for Low Freq', hrsLowFreq)
              , self.hrsPg('Hours for Hi Freq 1', hrsHiFreq1)
              , self.hrsPg('Hours for Hi Freq 2', hrsHiFreq2)
               ]

        t = Table(data, colWidths = [100, 100, 100])
        t.setStyle(self.tableStyle)
        return t

    def getAvailableNewAstronomyTableGradeA(self):
        txt = 'Available for NEW Astronomy during %s (Grade A Carry Over Only)' % self.semester
        return self.getAvailableTable(txt
            , self.lst.remainingFromGradeACarryoverPs)


    def getAvailableNewAstronomyTable(self):
        txt = 'Available for NEW Astronomy during %s (All Grades Carry Over)' % self.semester
        return self.getAvailableTable(txt
                                    , self.lst.remainingPs)

    def hrsPg(self, text, hrs):
        "This is common enough when reporting on hours"
        return [self.pg(text) # label
              , self.pg("%5.2f" % hrs[0]) # total hrs
              , self.pg("GC[%5.2f]" % hrs[1]) # hrs in Gal. Center
               ]


if __name__ == '__main__':

    f = file('SemesterSummary.pdf', 'w')
    ss = SemesterSummary(f, semester = '13A')
    ss.report()


