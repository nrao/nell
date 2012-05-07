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

import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units  import inch

from pht.tools.LstPressures import LstPressures
from pht.models import *
from Report import Report

class LstPressureReport(Report):

    """
    This class is responsible for producing a report on the LST
    pressures for all the given sessions.  It is basically a tabular
    representation of what the plots show.
    """

    def __init__(self, filename):
        super(LstPressureReport, self).__init__(filename
                                              , orientation = 'landscape' 
                                              , topMargin = 50
                                               )

        # make first style sheet font a little smaller
        self.styleSheet.fontSize = 6

        # a second style sheet for headers
        self.styleSheet2 = getSampleStyleSheet()['Normal']
        self.styleSheet2.fontSize = 8

        # redefine table style to include an inner grid
        self.tableStyle = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])

        self.lst = LstPressures()

        self.title = 'LST Pressures'
        self.titleOffset = 0

        self.fltFrmt = "%5.2f"

    def report(self, sessions = None, debug = False):

        if sessions is not None:
            self.title += " for %s" % ",".join([s.name for s in sessions])
            self.titleOffset = 100 + len(self.title) 

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

        b = self.getBreak() #Paragraph('<br/>', self.styleSheet)

        elements = [h1, t1 
                  , h2, t2 #, b
                  , h3, t3 #, b
                  , h4, t4 #, b
                  , h5, t5 #, b
                  , h6, t6
                   ]

        if debug:
            debugElements = self.createDebugElements()
            elements.extend(debugElements)

        # write the document to disk (or something)
        self.doc.build(elements
                    , onFirstPage = self.makeHeaderFooter
                    , onLaterPages = self.makeHeaderFooter)

    def createTotalsTable(self):
        "Simply one header row, and the row of total data"
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
        "Common pattern: display total, then break it down by weather type."
        rows = [self.createLstRow()]
        dataRows = [self.createRow('Total'
                                 , totals 
                                 , self.fltFrmt)]
        for w in self.lst.weatherTypes:
            row = self.createRow(self.cropWeatherLabel(w)
                               , types.getType(w) 
                               , self.fltFrmt)
            dataRows.append(row)
        rows.extend(dataRows)

        t = Table(rows, colWidths = [30]*self.lst.hrs)
        t.setStyle(self.tableStyle)
        return t 

    def createLstRow(self):
        "Every table begins with the LSTs 0-23"
        return self.createRow('LST', range(self.lst.hrs), '%d')
    
    def createAvailableTable(self):
        return self.createPressureTable(self.lst.weather.availabilityTotal
                                      , self.lst.weather.availability)

                
    def createRemainingTable(self):
        return self.createPressureTable(self.lst.remainingTotalPs
                                      , self.lst.remainingPs)

    def cropWeatherLabel(self, w):
        if w == 'Excellent':
            return 'Ex'
        else:
            return w

    def createRow(self, label, data, frmt):
        rows = [self.pg(label, bold = True)]
        dataRows = [self.pg(frmt % d) for d in data]
        rows.extend(dataRows)
        return rows

    def tableHeader(self, text):
        return Paragraph("<b>%s</b>" % text, self.styleSheet2)       

    def getDataRow(self, title, data):
        row = [self.pg(title)]
        rowData = [self.pg("%5.2f" % d) for d in data]
        row.extend(rowData)
        return row

    def createDebugElements(self):

        els = [self.pg("Debug Info:", bold = True)]

        # warnings ?
        valid, msgs = self.lst.checkPressures()
        if not valid:
            els.append(self.getBreak())
            els.append(self.pg("Accounting ERRORS:", bold = True))
            for msg in msgs:
                els.append(self.pg(msg))

        # non traditional sessions
        if len(self.lst.badSessions) > 0:
            ss = self.createSessionElements("Session's without pressures (bad):"
                                         , self.lst.badSessions)
            els.extend(ss)
        if len(self.lst.futureSessions) > 0:
            ss = self.createSessionElements("Session's for future semesters:"
                                         , self.lst.futureSessions)
            els.extend(ss)
        if len(self.lst.semesterSessions) > 0:
            ss = self.createSessionElements("Session's using semester time:"
                                         , self.lst.semesterSessions)
            els.extend(ss)
        if len(self.lst.noGrades) > 0:
            ss = self.createSessionElements("Session's without grades:"
                                         , self.lst.noGrades)
            els.extend(ss)
        if len(self.lst.failingSessions) > 0:
            ss = self.createSessionElements("Session's with failing grades:"
                                         , self.lst.failingSessions)
            els.extend(ss)

        # session details
        els.append(self.getBreak())
        els.append(self.pg("Session Details:", bold = True))
        data = [self.createLstRow()]
        for name in sorted(self.lst.pressuresBySession.keys()):
            bucket, ps, total = self.lst.pressuresBySession[name]
            label = "%s: (%s, %5.2f)" % (name, bucket, total)
            data.append(self.getDataRow(label, ps))
        widths = [120]
        widths.extend([25]*(self.lst.hrs-1))
        t = Table(data, colWidths = widths)
        t.setStyle(self.tableStyle)
        els.append(t)

        return els        


    def createSessionElements(self, header, sessions):
        "Print out a list of sessions"
        els = [self.getBreak()]
        els.append(self.pg(header, bold = True))
        for s in sessions:
            els.append(self.pg(s.__str__()))
        return els

if __name__ == '__main__':

    sessions = None
    debug = False

    for arg in sys.argv:
        key = arg.split('=')[0]
        if key == '-session':
            session = arg.split('=')[1]
            sessions = Session.objects.filter(name = session)
        elif key == '-debug':
            debug = True

    f = file('LstPressures.pdf', 'w')
    lst = LstPressureReport(f)
    lst.report(sessions = sessions
             , debug = debug)         
