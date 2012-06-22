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
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units  import inch

from pht.models import *
from pht.utilities import *
from pht.tools.SourceConflicts import SourceConflicts
from Report import Report
 
class SourceConflictsReport(Report):

    def __init__(self, filename):
        super(SourceConflictsReport, self).__init__(filename
                                           , orientation = 'landscape') 
        self.title = 'Source Conflicts'
        self.headerStyleSheet = getSampleStyleSheet()['Normal']
        self.headerStyleSheet.fontSize = 15

    def report(self, semester = None):
        self.semester = semester
        self.sc       = SourceConflicts(semester = semester)

        # TBF: Remove this later.  Limiting search space for testing.
        self.sc.findConflicts(
           proposals = Proposal.objects.filter(semester__semester = '12B').order_by('pcode')
           #proposals = Proposal.objects.filter(semester__semester = '12B').order_by('pcode')[:5]
         #, allProposals = Proposal.objects.filter(semester__semester = '12A'))
         , allProposals = Proposal.objects.all())

        self.conflictedProposals = sorted([k for k in self.sc.conflicts.keys() if len(self.sc.conflicts[k]['conflicts']) > 0])

        self.title = self.title if self.semester is None else \
                     self.title + " for Semester %s" % self.semester

        data = []
        for pcode in self.conflictedProposals:
            data.extend(self.genRecordHeader(pcode))
            data.append(self.genTable(pcode))
            data.append(PageBreak())

        # write the document to disk (or something)
        self.doc.build(data, onFirstPage = self.makeHeaderFooter, onLaterPages = self.makeHeaderFooter)

    def genRecordHeader(self, pcode):
        propConflict = self.sc.conflicts[pcode]
        data = [Paragraph(propConflict['proposal'].title, self.styleSheet)
              , Paragraph(propConflict['proposal'].pi.getLastFirstName(), self.styleSheet)
              , Paragraph("Search Radius('): %.3f" % rad2arcMin(propConflict['searchRadius']), self.styleSheet)
              , Paragraph("Lowest Rx: %s" % propConflict['lowestRx'], self.styleSheet)
              ]
        table = Table([data], colWidths = [300, 100, 100, 100])
        return [Paragraph('Sources Found in other Proposals for %s' % pcode, self.headerStyleSheet)
              , self.getBreak()
              , table
              ]

    def genTable(self, pcode):
        propConflict = self.sc.conflicts[pcode]

        data = [self.genHeader()]
        data.extend(map(self.genRow, propConflict['conflicts']))
        t = Table(data, colWidths = self.colWidths())
        t.setStyle(self.tableStyle)
        return t

    def genHeader(self):
        return [Paragraph('<b>Source</b>', self.styleSheet)
              , Paragraph('<b>Chk. Source </b>', self.styleSheet)
              , Paragraph('<b>Ra </b>', self.styleSheet)
              , Paragraph('<b>Dec</b>', self.styleSheet)
              , Paragraph('<b>Proposal </b>', self.styleSheet)
              , Paragraph("<b>Distance (')</b>", self.styleSheet)
              , Paragraph("<b>DeltaRa (') </b>", self.styleSheet)
              , Paragraph("<b>DeltaDec (') </b>", self.styleSheet)
              , Paragraph("<b>Level</b>", self.styleSheet)
              ]

    def genRow(self, conflict):
        return [Paragraph(conflict['targetSrc'].target_name, self.styleSheet)
              , Paragraph(conflict['searchedSrc'].target_name, self.styleSheet)
              , Paragraph('%.4f' % conflict['searchedSrc'].ra, self.styleSheet)
              , Paragraph('%.4f' % conflict['searchedSrc'].dec, self.styleSheet)
              , Paragraph(conflict['searchedProp'].pcode, self.styleSheet)
              , Paragraph('%.4f' % rad2arcMin(conflict['distance']), self.styleSheet)
              , Paragraph('%.4f' % rad2arcMin(abs(conflict['targetSrc'].ra - conflict['searchedSrc'].ra)), self.styleSheet)
              , Paragraph('%.4f' % rad2arcMin(abs(conflict['targetSrc'].dec - conflict['searchedSrc'].dec)), self.styleSheet)
              , Paragraph('%s' % conflict['level'], self.styleSheet)
              ]

    def colWidths(self):
        return [150, 150, 40, 60, 60, 60, 60, 60, 60]

    def makeHeaderFooter(self, canvas, doc):
        canvas.saveState() 
        canvas.setFont('Times-Roman', 20) 
        w, h = letter

        canvas.drawString(43, w-40, self.title)
        self.genFooter(canvas, doc)

    def genFooter(self, canvas, doc):
        dateStr = self.getDateStr()
        data = [
         [Paragraph('%s - %d' % (dateStr, doc.page), self.styleSheet)],
        ]
        t = Table(data, colWidths = [600])
        ts = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        t.setStyle(ts)
        t.wrapOn(canvas, 3*72, 2*72)
        t.drawOn(canvas, 10, 10)

    def getDateStr(self):
        dt = datetime.now()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return '%s, %s' % (days[dt.weekday()],  dt.strftime('%B %d, %Y'))

if __name__ == '__main__':
    scr = SourceConflictsReport('sourceConflictsReport.pdf')
    scr.report()
