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
 
class Report(object):

    def __init__(self, filename):
        w, h      = letter
        self.doc  = SimpleDocTemplate(filename, pagesize=(h, w))
        self.styleSheet = getSampleStyleSheet()['Normal']
        self.styleSheet.fontSize = 7
        self.title = ''
        self.proposals = []

    def report(self, semester = None):
        self.semester = semester
        self.title = self.title if self.semester is None else \
                     self.title + " for Semester %s" % self.semester

        data = [self.genHeader()]
        self.getProposals(semester)
        data.extend(map(self.genRow, self.proposals))
        t = Table(data, colWidths = self.colWidths())
        self.tableStyle = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        for i in range(6, len(self.proposals), 5):
            self.tableStyle.add('LINEABOVE', (0, i),(-1, i), 1, colors.black)
        t.setStyle(self.tableStyle)

        # write the document to disk (or something)
        self.doc.build([t], onFirstPage = self.makeHeaderFooter, onLaterPages = self.makeHeaderFooter)

    def getProposals(self, semester):
        self.proposals = self.order(
         [p for p in Proposal.objects.all() if 'TGBT' not in p.pcode] if semester is None else
         [p for p in Proposal.objects.filter(semester__semester = semester) if 'TGBT' not in p.pcode])
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
