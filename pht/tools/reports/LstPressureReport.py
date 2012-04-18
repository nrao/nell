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

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units  import inch

from pht.tools.LstPressures import LstPressures

class LstPressureReport(object):

    """
    This class is responsible for producing a report on the LST
    pressures for all the given sessions.  It is basically a tabular
    representation of what the plots show.
    """

    def __init__(self, filename, semester = None):

        self.semester = semester

        # portrait or landscape?
        w, h      = letter
        self.orientation = 'landscape'
        if self.orientation == 'portrait':
            pagesize = (w, h)
        else:
            pagesize = (h, w)

        # set up the page    
        self.doc  = SimpleDocTemplate(filename
                                    , pagesize=pagesize
                                    , topMargin=50)
        self.styleSheet = getSampleStyleSheet()['Normal']
        self.styleSheet.fontSize = 6
        self.styleSheet2 = getSampleStyleSheet()['Normal']
        self.styleSheet2.fontSize = 8

        self.tableStyle = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])

        self.lst = LstPressures()

        self.title = 'LST Pressures'

        self.fltFrmt = "%5.2f"

    def report(self, sessions = None):

        # crunch the numbers
        self.lst.getPressures(sessions) 

        # now mak'm pretty
        h1 = self.tableHeader('Totals:')
        t1 = self.createTotalsTable()
 
        h2 = self.tableHeader('Availability:')
        t2 = self.createAvailableTable()

        h3 = self.tableHeader('Carryover:')
        t3 = self.createCarryoverTable()

        h4 = self.tableHeader('Remaining:')
        t4 = self.createRemainingTable()

        h5 = self.tableHeader('Requested:')
        t5 = self.createRequestedTable()

        h6 = self.tableHeader('Allocated:')
        t6 = self.createAllocatedTable()

        b = Paragraph('<br/>', self.styleSheet)

        elements = [h1, t1 
                  , h2, t2 #, b
                  , h3, t3 #, b
                  , h4, t4 #, b
                  , h5, t5 #, b
                  , h6, t6
                   ]

        # write the document to disk (or something)
        self.doc.build(elements
                    , onFirstPage = self.makeHeaderFooter
                    , onLaterPages = self.makeHeaderFooter)

    def createTotalsTable(self):
        rows = [self.createLstRow()
              , self.createRow('Total', self.lst.totalPs, self.fltFrmt)]
        t = Table(rows, colWidths = [30]*self.lst.hrs)
        t.setStyle(self.tableStyle)
        return t
                
    def createRequestedTable(self):
        return self.createPressureTable(self.lst.requestedTotalPs
                                      , self.lst.requestedPs)

    def createCarryoverTable(self):
        return self.createPressureTable(self.lst.carryoverTotalPs
                                      , self.lst.carryoverPs)
    def createRemainingTable(self):
        return self.createPressureTable(self.lst.remainingTotalPs
                                      , self.lst.remainingPs)

    def createAllocatedTable(self):

        # different from the other tables
        rows = [self.createLstRow()
              , self.createRow('Total'
                             , self.lst.newAstronomyTotalPs
                             , self.fltFrmt)]
        for w in self.lst.weatherTypes:
            for g in self.lst.grades:
                # make sure our row lable fits
                if w == 'Excellent':
                    label = 'Ex_%s' % g
                else:
                    label = '%s_%s' % (w, g)
                rows.append(self.createRow(label
                                         , self.lst.gradePs[g].getType(w)
                                         , self.fltFrmt))
                                         
        t = Table(rows, colWidths = [30]*self.lst.hrs)
        t.setStyle(self.tableStyle)
        return t

    def createPressureTable(self, totals, types):
        rows = [self.createLstRow()]
        dataRows = [self.createRow('Total'
                                 , totals 
                                 , self.fltFrmt)]
        for w in self.lst.weatherTypes:
            row = self.createRow(w
                               , types.getType(w) 
                               , self.fltFrmt)
            dataRows.append(row)
        rows.extend(dataRows)

        t = Table(rows, colWidths = [30]*self.lst.hrs)
        t.setStyle(self.tableStyle)
        return 

    def createLstRow(self):
        return self.createRow('LST', range(self.lst.hrs), '%d')
    
    def createRow(self, label, data, frmt):
        rows = [self.pg(label)]
        dataRows = [self.pg(frmt % d) for d in data]
        rows.extend(dataRows)

    def createAvailableTable(self):
        return self.createPressureTable(self.lst.weather.availabilityTotal
                                      , self.lst.weather.availability)

        rows = [self.createLstRow()]
        dataRows = [self.createRow('Total'
                                 , self.lst.weather.availabilityTotal
                                 , self.fltFrmt)]
        for w in self.lst.weatherTypes:
            row = self.createRow(w
                               , self.lst.weather.availability.getType(w)
                               , self.fltFrmt)
            dataRows.append(row)
        rows.extend(dataRows)

        t = Table(rows, colWidths = [30]*self.lst.hrs)
        t.setStyle(self.tableStyle)
        return t
                
    def createRemainingTable(self):
        return self.createPressureTable(self.lst.remainingTotalPs
                                      , self.lst.remainingPs)

    def createPressureTable(self, totals, types):
        rows = [self.createLstRow()]
        dataRows = [self.createRow('Total'
                                 , totals 
                                 , self.fltFrmt)]
        for w in self.lst.weatherTypes:
            row = self.createRow(w
                               , types.getType(w) 
                               , self.fltFrmt)
            dataRows.append(row)
        rows.extend(dataRows)

        t = Table(rows, colWidths = [30]*self.lst.hrs)
        t.setStyle(self.tableStyle)
        return t

    def createLstRow(self):
        return self.createRow('LST', range(self.lst.hrs), '%d')
    
    def createRow(self, label, data, frmt):
        rows = [self.pg(label)]
        dataRows = [self.pg(frmt % d) for d in data]
        rows.extend(dataRows)
        return rows

    def pg(self, text):
        "Shortcut to Paragraph"
        return Paragraph(text, self.styleSheet)       

    def tableHeader(self, text):
        return Paragraph(text, self.styleSheet2)       

    def getDataRow(self, title, data):
        row = [self.pg(title)]
        rowData = [self.pg("%5.2f" % d) for d in data]
        row.extend(rowData)
        return row

    def genFooter(self, canvas, doc):
        pass

    def makeHeaderFooter(self, canvas, doc):
        canvas.saveState() 
        canvas.setFont('Times-Roman', 20) 
        w, h = letter

        if self.orientation == 'portrait':
            canvas.drawString(20, h-40, self.title)
        else:
            canvas.drawString(w, w-40, self.title)
        self.genFooter(canvas, doc)

if __name__ == '__main__':

    f = file('LstPressures.pdf', 'w')
    lst = LstPressureReport(f)
    lst.report()         
