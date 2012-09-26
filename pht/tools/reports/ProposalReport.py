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
from Report import Report
 
def defaultFilter(proposal):
    return 'TGBT' not in proposal.pcode # and 'GBT' in proposal.pcode

class ProposalReport(Report):

    """
    This is an abstract class for the Proposal reports, like
    Proposal Ranking, etc.
    """

    def __init__(self, filename):
        super(ProposalReport, self).__init__(filename
                                           , orientation = 'landscape') 
        self.title = ''
        self.proposals = []

    def report(self, semester = None, filter = None):
        self.semester = semester
        self.title = self.title if self.semester is None else \
                     self.title + " for Semester %s" % self.semester

        data = [self.genHeader()]
        self.getProposals(semester, filter = filter)
        data.extend(map(self.genRow, self.proposals))
        data.append([])
        proposalTable = Table(data, colWidths = self.colWidths())
        for i in range(6, len(self.proposals), 5):
            self.tableStyle.add('LINEABOVE', (0, i),(-1, i), 1, colors.black)
        proposalTable.setStyle(self.tableStyle)

        bandStatsTable = self.genBandStatsTable()

        # write the document to disk (or something)
        self.doc.build([proposalTable, self.genStats(), PageBreak(), bandStatsTable]
                     , onFirstPage = self.makeHeaderFooter
                     , onLaterPages = self.makeHeaderFooter)

    def genBandStatsTable(self):
        data = [[Paragraph('<b>Band</b>', self.styleSheet)
               , Paragraph('<b>#Proposals</b>', self.styleSheet)
               , Paragraph('<b>Req Hrs</b>', self.styleSheet)
               ]]
        bandStats = {}
        for rcvr in Receiver.objects.all():
            bandStats[rcvr.code] = (0, 0)

        for p in self.proposals:
            bands = p.bands()
            backends = p.backends()
            if 'Z' in backends:
                bands += 'Z'
            for band in bands:
                num, time = bandStats.get(band, (0,0))
                bandStats[band] = (num + 1, time + (p.requestedTime() / float(len(bands))))
    
        sortedBandStats = sorted(bandStats.iteritems(), key = lambda stat: stat[0])
        for band, stats in sortedBandStats:
            data.append([Paragraph(band, self.styleSheet)
                       , Paragraph('%s' % stats[0], self.styleSheet)
                       , Paragraph('%s' % round(stats[1], 2), self.styleSheet)
                       ])
        bandStatsTable = Table(data, colWidths = [50, 50, 50])
        bandStatsTable.setStyle(self.tableStyle)

        return bandStatsTable

    def genStats(self):
        
        numProp  = len(self.proposals)
        reqhours = sum([p.requestedTime() for p in self.proposals])
        typeStats = {}
        for p in self.proposals:
            num, hrs = typeStats.get(p.proposal_type.type, (0, 0))
            typeStats[p.proposal_type.type] = num + 1, hrs + p.requestedTime()
            
        reqdays  = reqhours / 24.

        stats = '<br/>'.join(['<b>%s: %s for %s hours (%.2f days)</b>' % (t, n, h, h / 24.)
                              for t, (n, h) in typeStats.iteritems()])
        stats += '<br/><b>Number of proposals %s for %s hours (%.2f days)</b>' % (numProp, reqhours, reqdays)
        return Paragraph(stats, self.styleSheet)

    def getProposals(self, semester, filter = None):
        if filter is None:
            filter = defaultFilter
        self.proposals = self.order(
         [p for p in Proposal.objects.all() if filter(p)] if semester is None else
         [p for p in Proposal.objects.filter(semester__semester = semester) if filter(p)])
        return self.proposals

    def makeHeaderFooter(self, canvas, doc):
        canvas.saveState() 
        canvas.setFont('Times-Roman', 20) 
        w, h = letter

        canvas.drawString(43, w-40, self.title)
        self.genFooter(canvas, doc)

    def order(self, proposals):
        "Default implementation doesn't sort, override for custom sorting."
        return proposals

    def genBands(self):
        return ', '.join(['%s(%s-%s)' % (r.code, r.freq_low, r.freq_hi)
          for r in Receiver.objects.all()])

    def genBackends(self):
        return ', '.join(['%s-%s' % (b.code, b.abbreviation) for b in Backend.objects.all()])

    def genObsTypes(self):
        return ', '.join(['%s-%s' % (ot.code, ot.type) for ot in ObservingType.objects.all()])

    def getDateStr(self):
        dt = datetime.now()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return '%s, %s' % (days[dt.weekday()],  dt.strftime('%B %d, %Y'))
