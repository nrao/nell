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

from pht.models         import *
from ProposalReport     import ProposalReport
 
class ProposalSummary(ProposalReport):

    def __init__(self, filename):
        super(ProposalSummary, self).__init__(filename)
        self.title = 'Proposal Summary'

    def setTitle(self, title):
        self.title = title

    def genHeader(self):
        return [Paragraph('<b># </b>', self.styleSheet)
              , Paragraph('<b>Title </b>', self.styleSheet)
              , Paragraph('<b>PI </b>', self.styleSheet)
              , Paragraph('<b>Rq Time Hrs</b>', self.styleSheet)
              , Paragraph('<b>Thesis </b>', self.styleSheet)
              , Paragraph('<b>Bands </b>', self.styleSheet)
              , Paragraph('<b>Backends </b>', self.styleSheet)
              , Paragraph('<b>Obs Type </b>', self.styleSheet)
              , Paragraph('<b>Email </b>', self.styleSheet)
              ]

    def genRow(self, proposal):
        pi_name   = proposal.pi.getLastFirstName() if proposal.pi is not None else ''
        email     = proposal.pi.email if proposal.pi is not None else ''
        obs_types = [ot.code for ot in proposal.observing_types.all()]
        students  = len(proposal.author_set.filter(thesis_observing = True))
        thesis    = str(students)
        code      = proposal.pcode.split('-')
        pcode     = code[1] if len(code) > 1 and 'GBT' in proposal.pcode else proposal.pcode
        return [Paragraph('%s' % pcode, self.styleSheet)
              , Paragraph(proposal.title, self.styleSheet)
              , Paragraph(pi_name, self.styleSheet)
              , Paragraph(str(proposal.requestedTime()), self.styleSheet)
              , Paragraph(thesis, self.styleSheet)
              , Paragraph(proposal.bands(), self.styleSheet)
              , Paragraph(proposal.backends(), self.styleSheet)
              , Paragraph(''.join(obs_types), self.styleSheet)
              , Paragraph(email, self.styleSheet)
              ]

    def colWidths(self):
        return [50, 300, 80, 40, 30, 50, 50, 50, 120]

    def genFooter(self, canvas, doc):
        dateStr = self.getDateStr()
        data = [
          [Paragraph('<b>Bands(GHz):</b>', self.styleSheet)
         , Paragraph(self.genBands(), self.styleSheet)],
          [Paragraph('<b>BackEnds:</b>', self.styleSheet)
         , Paragraph(self.genBackends(), self.styleSheet)],
          [Paragraph('<b>Obs Type:</b>', self.styleSheet)
         , Paragraph(self.genObsTypes(), self.styleSheet)
         , Paragraph('%s - %d' % (dateStr, doc.page), self.styleSheet)],
        ]
        t = Table(data, colWidths = [50, 600])
        ts = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        t.setStyle(ts)
        t.wrapOn(canvas, 3*72, 2*72)
        t.drawOn(canvas, 10, 10)

if __name__ == '__main__':
    ps = ProposalSummary('proposalSummary.pdf')
    ps.report()
