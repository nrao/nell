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

from pht.models import *
 
class ProposalSummary(object):

    def __init__(self, filename):
        w, h      = letter
        self.doc  = SimpleDocTemplate(filename, pagesize=(h, w))
        self.styleSheet = getSampleStyleSheet()['Normal']
        self.styleSheet.fontSize = 7

    def report(self):
        data      = [self.genHeader()]
        proposals = [self.genRow(p) for p in Proposal.objects.all()]
        data.extend(proposals)
        t = Table(data, colWidths = [20, 350, 100, 50, 50, 50, 50, 50, 50])
        ts = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        for i in range(6, len(proposals), 5):
            ts.add('LINEABOVE', (0, i),(-1, i), 1, colors.black)
        t.setStyle(ts)

        # write the document to disk (or something)
        self.doc.build([t])

    def genHeader(self):
        return [Paragraph('<b># </b>', self.styleSheet)
              , Paragraph('<b>Title </b>', self.styleSheet)
              , Paragraph('<b>PI </b>', self.styleSheet)
              , Paragraph('<b>Req Time Hrs </b>', self.styleSheet)
              , Paragraph('<b>Thesis </b>', self.styleSheet)
              , Paragraph('<b>Bands </b>', self.styleSheet)
              , Paragraph('<b>Backends </b>', self.styleSheet)
              , Paragraph('<b>Obs Type </b>', self.styleSheet)
              , Paragraph('<b>Email </b>', self.styleSheet)
              ]

    def genRow(self, proposal):
        pi_name   = proposal.pi.getLastFirstName() if proposal.pi is not None else None
        obs_types = [ot.type[:1] for ot in proposal.observing_types.all()]
        thesis    = any([a.thesis_observing for a in proposal.author_set.all()])
        return [Paragraph('%s' % proposal.id, self.styleSheet)
              , Paragraph(proposal.title, self.styleSheet)
              , Paragraph(pi_name, self.styleSheet)
              , Paragraph(proposal.requestedTime(), self.styleSheet)
              , Paragraph(thesis, self.styleSheet)
              , Paragraph(proposal.bands(), self.styleSheet)
              , Paragraph(proposal.backends(), self.styleSheet)
              , Paragraph(''.join(obs_types), self.styleSheet)
              , Paragraph('<b>Email </b>', self.styleSheet)
              ]

if __name__ == '__main__':
    ps = ProposalSummary('proposalSummary.pdf')
    ps.report()
