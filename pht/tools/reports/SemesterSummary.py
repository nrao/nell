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

from datetime      import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units  import inch

from pht.models import *
from Report import Report

from pht.tools.SemesterTimeAccounting import SemesterTimeAccounting
 
class SemesterSummary(Report):

    """
    This class is responsible for producing a report on the overall
    summary of a given semester.
    """

    def __init__(self, filename, semester = None):
        super(SemesterSummary, self).__init__(filename)

        self.semester = semester

        # portrait or landscape?
        #w, h      = letter
        #self.orientation = 'portrait'
        #if self.orientation == 'portrait':
        #    pagesize = (w, h)
        #else:
        #    pagesize = (h, w)

        # set up the page    
        #self.doc  = SimpleDocTemplate(filename, pagesize=pagesize)
        #self.styleSheet = getSampleStyleSheet()['Normal']
        #self.styleSheet.fontSize = 7

        #self.tableStyle = TableStyle([
        #    ('TOPPADDING', (0, 0), (-1, -1), 0),
        #    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        #    ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
        #    ('BOX', (0, 0), (-1, -1), 1, colors.black),
        #])

        self.ta = SemesterTimeAccounting(semester = semester)

        self.title = 'Semester Summary'

    def report(self, semester = None):

        if semester is not None:
            self.semester = semester

        self.ta.calculateTimeAccounting()
        
        self.title = self.title if self.semester is None else \
                     self.title + " for Semester %s" % self.semester


        t0 = self.getIntroTable()
        t1 = self.getStartingHoursTable()
        t2 = self.getAvailableAllAstronomyTable()
        t3 = self.getAvailableNewAstronomyTableGradeA()
        t4 = self.getAvailableNewAstronomyTable()

        b = self.getBreak()

        tables = [t0, b, t1, b, t2, b]
        for g in ['A', 'B', 'C']:
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
              , [Paragraph('%s - %s' % (self.ta.timeRange), self.styleSheet)]
              , [Paragraph('As of %s' % self.ta.published, self.styleSheet)]
               ]

        t = Table(data, colWidths = [300])

        t.setStyle(self.tableStyle)
        
        return t

    def getStartingHoursTable(self):

        hrsInSemester = (self.ta.totalAvailableHrs.total.total 
                       , self.ta.totalAvailableHrs.gc.total)
        hrsMaint      = (self.ta.maintHrs.total.total
                       , self.ta.maintHrs.gc.total)  
        hrsShutdown   = (self.ta.shutdownHrs.total.total
                       , self.ta.shutdownHrs.gc.total)  
        hrsTests      = (self.ta.testHrs.total.total
                       , self.ta.testHrs.gc.total)  

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
                                    , self.ta.astronomyAvailableHrs)

    def getBacklogTableForGrade(self, grade):

        hrsFixed = (self.ta.carryOver[grade]['fixed'].total.total
                  , self.ta.carryOver[grade]['fixed'].gc.total)
        hrsTotal = (self.ta.carryOver[grade]['times'].total.total
                  , self.ta.carryOver[grade]['times'].gc.total)
        hrsTotal = (hrsTotal[0] + hrsFixed[0], hrsTotal[1] + hrsFixed[1])          
        hrsLowFreq = (self.ta.carryOver[grade]['times'].total.lowFreq
                    , self.ta.carryOver[grade]['times'].gc.lowFreq)
        hrsHiFreq1 = (self.ta.carryOver[grade]['times'].total.hiFreq1
                    , self.ta.carryOver[grade]['times'].gc.hiFreq1)
        hrsHiFreq2 = (self.ta.carryOver[grade]['times'].total.hiFreq2
                    , self.ta.carryOver[grade]['times'].gc.hiFreq2)
        
        data = [[self.pg('Group %s time' % grade)]
               , self.hrsPg('Hours Total', hrsTotal + hrsFixed)  
               , self.hrsPg('Fixed Hours', hrsFixed)
               , self.hrsPg('Hours for Low Freq', hrsLowFreq)
               , self.hrsPg('Hours for Hi Freq 1', hrsHiFreq1)
               , self.hrsPg('Hours for Hi Freq 2', hrsHiFreq2)               
               ]

        t = Table(data, colWidths = [100, 100, 100])
        t.setStyle(self.tableStyle)
        return t

    def getAvailableHrs(self, available):
        "Reorganize our data."

        hrsTotal = (available.total.total
                    , available.gc.total)
        hrsLowFreq = (available.total.lowFreq
                    , available.gc.lowFreq)
        hrsHiFreq1 = (available.total.hiFreq1
                    , available.gc.hiFreq1)
        hrsHiFreq2 = (available.total.hiFreq2
                    , available.gc.hiFreq2)

        return (hrsTotal, hrsLowFreq, hrsHiFreq1, hrsHiFreq2)            
        
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
                                    , self.ta.newAstroAvailGradeAHrs)


    def getAvailableNewAstronomyTable(self):
        txt = 'Available for NEW Astronomy during %s (All Grades Carry Over)' % self.semester
        return self.getAvailableTable(txt
                                    , self.ta.newAstroAvailAllGradeHrs)

    #def pg(self, text):
    #    "Shortcut to Paragraph"
    #    return Paragraph(text, self.styleSheet)

    def hrsPg(self, text, hrs):
        "This is common enough when reporting on hours"
        return [self.pg(text) # label
              , self.pg("%5.2f" % hrs[0]) # total hrs
              , self.pg("GC[%5.2f]" % hrs[1]) # hrs in Gal. Center
               ]

    #def genFooter(self, canvas, doc):
    #    pass
#
#    def makeHeaderFooter(self, canvas, doc):
#        canvas.saveState() 
#        canvas.setFont('Times-Roman', 20) 
#        w, h = letter
#
#        if self.orientation == 'portrait':
#            canvas.drawString(20, h-40, self.title)
#        else:
#            canvas.drawString(w, w-40, self.title)
#        self.genFooter(canvas, doc)

if __name__ == '__main__':

    f = file('SemesterSummary.pdf', 'w')
    ss = SemesterSummary(f, semester = '12B')
    ss.report()


