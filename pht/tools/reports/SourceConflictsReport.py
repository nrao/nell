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

from scheduler.models import Semester as DssSemester
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

    def report(self, conflicts, semester = None, pcode = None, level = 0):
        self.conflicts = conflicts
        self.conflictedProposals = sorted([k for k in self.conflicts.keys() if len(self.conflicts[k]['conflicts']) > 0])
        self.title = self.title if semester is None else \
                     self.title + " for Semester %s" % semester
        self.title = self.title if pcode is None else \
                     self.title + " for %s" % pcode


        rows = []
        for pcode in self.conflictedProposals:
            rows.extend(self.genRecordHeader(pcode))
            rows.append(self.genTable(pcode))
            rows.append(self.getBreak())
            rows.append(Paragraph('Conflicted Proposal Information', self.styleSheet))
            rows.append(self.genProposalsTable(pcode))
            rows.append(PageBreak())
        data = rows or [Paragraph("No conflicts", self.styleSheet)]

        # write the document to disk (or something)
        self.doc.build(data, onFirstPage = self.makeHeaderFooter, onLaterPages = self.makeHeaderFooter)

    def genRecordHeader(self, pcode):
        propConflict = self.conflicts[pcode]
        data = [Paragraph(propConflict['proposal'].title, self.styleSheet)
              , Paragraph(propConflict['proposal'].pi.getLastFirstName(), self.styleSheet)
              , Paragraph("Search Radius('): %.3f" % rad2arcMin(propConflict['searchRadius']), self.styleSheet)
              , Paragraph("Lowest Rx: %s" % propConflict['lowestRx'], self.styleSheet)
              , Paragraph(propConflict['proposal'].spectral_line or '', self.styleSheet)
              ]
        table = Table([data], colWidths = [250, 100, 100, 100, 150])
        return [Paragraph('Sources Found in other Proposals for %s' % pcode, self.headerStyleSheet)
              , self.getBreak()
              , table
              ]

    def genTable(self, pcode):
        propConflict = self.conflicts[pcode]

        data = [self.genHeader()]
        data.extend(map(self.genRow, propConflict['conflicts']))
        t = Table(data, colWidths = self.colWidths())
        t.setStyle(self.tableStyle)
        return t

    def genProposalsTable(self, pcode):
        def genProposalInfo(conflictedPcode):
            conflict     = [c for c in self.conflicts[pcode]['conflicts'] if c['searchedProp'].pcode == conflictedPcode][0]
            searched     = conflict['searchedProp']
            complete     = ''
            thisSemester = 'V' if DssSemester.getCurrentSemester().semester == searched.semester.semester else 'S'
            if searched.dss_project is not None and searched.dss_project.complete:
                complete = 'C' 

            lastObsDate = conflict['lastObsDate'].strftime('%m/%d/%Y') if conflict['lastObsDate']is not None else ''
            grades = ', '.join(set([s.grade.grade if s.grade is not None else '?' for s in searched.session_set.all()]))
            return [Paragraph(searched.pcode, self.styleSheet)
                  , Paragraph(lastObsDate, self.styleSheet)
                  , Paragraph(grades, self.styleSheet)
                  , Paragraph(searched.title, self.styleSheet)
                  , Paragraph(searched.pi.getLastFirstName(), self.styleSheet)
                  , Paragraph(thisSemester, self.styleSheet)
                  , Paragraph(complete, self.styleSheet)
                  , Paragraph(searched.spectral_line or '', self.styleSheet)
                    ]
            
        data = [[Paragraph('<b>Pcode</b>', self.styleSheet)
               , Paragraph('<b>Last Obs</b>', self.styleSheet)
               , Paragraph('<b>Grades</b>', self.styleSheet)
               , Paragraph('<b>Title</b>', self.styleSheet)
               , Paragraph('<b>PI</b>', self.styleSheet)
               , Paragraph('', self.styleSheet)
               , Paragraph('<b>Complete</b>', self.styleSheet)
               , Paragraph('<b>Spec Line</b>', self.styleSheet)
                 ]]
        conflictedPcodes = set([c['searchedProp'].pcode for c in self.conflicts[pcode]['conflicts']])
        #data.extend(map(genProposalInfo, self.conflicts[pcode]['conflicts']))
        data.extend(map(genProposalInfo, conflictedPcodes))
        t = Table(data, colWidths = [60, 50, 50, 280, 100, 20, 50, 150])
        t.setStyle(self.tableStyle)
        return t

    def genHeader(self):
        return [Paragraph('<b>Source</b>', self.styleSheet)
              , Paragraph('<b>Proposal </b>', self.styleSheet)
              , Paragraph('<b>Chk. Source </b>', self.styleSheet)
              , Paragraph('<b>Sp. Line </b>', self.styleSheet)
              , Paragraph('<b>Ra </b>', self.styleSheet)
              , Paragraph('<b>Dec</b>', self.styleSheet)
              , Paragraph("<b>Distance (')</b>", self.styleSheet)
              , Paragraph("<b>DeltaRa (') </b>", self.styleSheet)
              , Paragraph("<b>DeltaDec (') </b>", self.styleSheet)
              ]

    def genRow(self, conflict):
        spLine = conflict['searchedProp'].spectral_line
        searchedProp = conflict['searchedProp'].pcode
        if conflict['lastObsDate'] is not None:
            searchedProp += ' (%s)' % conflict['lastObsDate'].strftime('%m/%d/%Y')
        return [Paragraph(conflict['targetSrc'].target_name, self.styleSheet)
              , Paragraph(searchedProp, self.styleSheet)
              , Paragraph(conflict['searchedSrc'].target_name, self.styleSheet)
              , Paragraph(spLine[:100] if spLine is not None else '', self.styleSheet)
              , Paragraph(rad2sexHrs(conflict['searchedSrc'].ra), self.styleSheet)
              , Paragraph(rad2sexDeg(conflict['searchedSrc'].dec), self.styleSheet)
              , Paragraph('%.4f' % rad2arcMin(conflict['distance']), self.styleSheet)
              , Paragraph('%.4f' % rad2arcMin(abs(conflict['targetSrc'].ra - conflict['searchedSrc'].ra)), self.styleSheet)
              , Paragraph('%.4f' % rad2arcMin(abs(conflict['targetSrc'].dec - conflict['searchedSrc'].dec)), self.styleSheet)
              ]

    def colWidths(self):
        return [150, 100, 150, 100, 40, 60, 50, 50, 60]

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
    import argparse
    parser = argparse.ArgumentParser(description='Command line tool for running GB PHT Source Conflict Reports.  Specify at least a semester or pcode.')
    parser.add_argument('-s','--semester', dest="semester", help='Semester of the proposals you wish to check for source conflicts.')
    parser.add_argument('-p','--pcode', dest="pcode", help='Run source conflicts for a given pcode (Ex. GBT12B-100)')
    parser.add_argument('-l','--level', dest="level", type = int, default = -1, help='Level of conflicts to check.  Options are "0", "1", "2" (defaults to all).')

    args = parser.parse_args()

    sc = SourceConflicts(semester = args.semester)
    if args.pcode is not None:
        sc.findConflicts(proposals = Proposal.objects.filter(pcode = args.pcode))
        filename = args.pcode
    else:
        sc.findConflicts(
            #  Uncomment for testing.
            #proposals = Proposal.objects.filter(semester__semester = args.semester)[:5]
            )
        filename = args.semester

    levelMap = ['all', 'sameReceiver', 'sameReceiver-proprietaryPeriod']
    if args.level == -1:
        sc.filterConflicts(0)
        scr = SourceConflictsReport('sourceConflictsReport-%s-all.pdf' % filename)
        scr.report(sc.filteredConflicts, semester = args.semester, pcode = args.pcode, level = 0)
        sc.filterConflicts(1)
        scr = SourceConflictsReport('sourceConflictsReport-%s-sameReceiver.pdf' % filename)
        scr.report(sc.filteredConflicts, semester = args.semester, pcode = args.pcode, level = 1)
        sc.filterConflicts(2)
        scr = SourceConflictsReport('sourceConflictsReport-%s-sameReceiver-proprietaryPeriod.pdf' % filename)
        scr.report(sc.filteredConflicts, semester = args.semester, pcode = args.pcode, level = 2)
    else:
        sc.filterConflicts(args.level)
        scr = SourceConflictsReport('sourceConflictsReport-%s-%s.pdf' % (filename, levelMap[args.level]))
        scr.report(sc.filteredConflicts, semester = args.semester, pcode = args.pcode, level = args.level)
