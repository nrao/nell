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
 
class ProposalRanking(Report):

    def __init__(self, filename):
        super(ProposalRanking, self).__init__(filename)
        self.title = 'GBT Proposal unWeighted Panel Ranking List'

    def colWidths(self):
        return [20, 20, 80, 310, 20, 50, 20, 20, 20, 20, 20, 20, 30, 20, 40]

    def genHeader(self):
        return [Paragraph('<b>Pro</b>', self.styleSheet)
              , Paragraph('<b>Ptm/Oh </b>', self.styleSheet)
              , Paragraph('<b>PI </b>', self.styleSheet)
              , Paragraph('<b>Title</b>', self.styleSheet)
              , Paragraph('', self.styleSheet)
              , Paragraph('<b>Band</b>', self.styleSheet)
              , Paragraph('<b>#S</b>', self.styleSheet)
              , Paragraph('<b>SRP</b>', self.styleSheet)
              , Paragraph('<b>Refs</b>', self.styleSheet)
              , Paragraph('<b>Rk</b>', self.styleSheet)
              , Paragraph('<b>Norm. SRP</b>', self.styleSheet)
              , Paragraph('<b>Rk</b>', self.styleSheet)
              , Paragraph('<b>Obs Type</b>', self.styleSheet)
              , Paragraph('<b>Req Hrs</b>', self.styleSheet)
              , Paragraph('<b>Total Ref Hrs</b>', self.styleSheet)
              ]

    def genRow(self, proposal):
        pi_name   = proposal.pi.getLastFirstName() if proposal.pi is not None else None
        obs_types = [ot.code for ot in proposal.observing_types.all()]
        draftRank = str(self.proposalsDraft.index(proposal) + 1)
        rank      = str(self.proposals.index(proposal) + 1)
        draftScore = str(proposal.draft_normalizedSRPScore) \
                       if proposal.draft_normalizedSRPScore is not None else ''
        score      = str(proposal.normalizedSRPScore) \
                       if proposal.normalizedSRPScore is not None else ''
        students  = len(proposal.author_set.filter(thesis_observing = True))
        thesis    = str(students)
        return [Paragraph(proposal.pcode.split('-')[1], self.styleSheet)
              , ''
              , Paragraph(pi_name, self.styleSheet)
              , Paragraph(proposal.title, self.styleSheet)
              , Paragraph(thesis, self.styleSheet)
              , Paragraph(proposal.bands(), self.styleSheet)
              , Paragraph(str(len(proposal.source_set.all())), self.styleSheet)
              , Paragraph(draftScore, self.styleSheet)
              , Paragraph(str(proposal.num_refs), self.styleSheet)
              , Paragraph(draftRank, self.styleSheet)
              , Paragraph(score, self.styleSheet)
              , Paragraph(rank, self.styleSheet)
              , Paragraph(''.join(obs_types), self.styleSheet)
              , Paragraph(str(proposal.requestedTime()), self.styleSheet)
              , ''
              ]

    def genFooter(self, canvas, doc):
        dateStr = self.getDateStr()
        data = [
          [Paragraph('<b>Bands(GHz):</b>', self.styleSheet)
         , Paragraph(self.genBands(), self.styleSheet)],
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

    def order(self, proposals):
        self.proposalsDraft = sorted(proposals, key = lambda p: p.draft_normalizedSRPScore)
        return sorted(proposals, key = lambda p: p.normalizedSRPScore)

