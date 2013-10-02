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

from pht.models     import *
from ProposalReport import ProposalReport
 
class ProposalRanking(ProposalReport):

    def __init__(self, filename):
        super(ProposalRanking, self).__init__(filename)
        self.title = 'GBT Proposal Linear Ranking List'

    def colWidths(self):
        return [20, 20, 80, 310, 20, 50, 20, 20, 20, 20, 20, 20, 30, 20, 40]

    def genHeaderStr(self):
        return 'Pro\tPI\tTitle\t\tBand\t#S\tSRP\tRefs\tRk\tNorm. SRP\tRk\tObs Type\tReq Hrs\tTotalRef Hrs'

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

    def getProposalCode(self, proposal):
        """
        GBT12A-001 -> G001
        VLBA12B-023 -> V023
        GLST12345 -> GLST12345
        """
        code      = proposal.pcode.split('-')
        if len(code) > 1:
            return code[0][0] + code[1]    
        else:
            return proposal.pcode
        
    def genRowData(self, proposal):
        students  = len(proposal.author_set.filter(thesis_observing = True))
        obs_types = [ot.code for ot in proposal.observing_types.all()]
        data = {'pi_name'    : proposal.pi.getLastFirstName() if proposal.pi is not None else ''
              , 'title'      : proposal.title
              , 'bands'      : proposal.bands()
              , 'num_srcs'   : str(len(proposal.source_set.all()))
              , 'num_refs'   : str(proposal.num_refs)
              , 'draftRank'  : str(self.proposalsDraft.index(proposal) + 1)
              , 'rank'       : str(self.proposals.index(proposal) + 1)
              , 'draftScore' : str(proposal.draft_normalizedSRPScore) \
                               if proposal.draft_normalizedSRPScore is not None else ''
              , 'score'      : str(proposal.normalizedSRPScore) \
                               if proposal.normalizedSRPScore is not None else ''
              , 'thesis'     : str(students) if students > 0 else ''
              , 'code'       : self.getProposalCode(proposal) 
              , 'obs_types'  : ''.join(obs_types)
              , 'rq_time'    : str(proposal.requestedTime())
              }
        return data

    def genRowDataOrdered(self, proposal):
        data = self.genRowData(proposal)
        return '\t'.join([data['code']
              , data['pi_name']
              , data['title']
              , data['thesis']
              , data['bands']
              , data['num_srcs']
              , data['draftScore']
              , data['num_refs']
              , data['draftRank']
              , data['score']
              , data['rank']
              , data['obs_types']
              , data['rq_time']
              ])

    def genRow(self, proposal):
        data = self.genRowData(proposal)
        return [Paragraph(data['code'], self.styleSheet)
              , ''
              , Paragraph(data['pi_name'], self.styleSheet)
              , Paragraph(data['title'], self.styleSheet)
              , Paragraph(data['thesis'], self.styleSheet)
              , Paragraph(data['bands'], self.styleSheet)
              , Paragraph(data['num_srcs'], self.styleSheet)
              , Paragraph(data['draftScore'], self.styleSheet)
              , Paragraph(data['num_refs'], self.styleSheet)
              , Paragraph(data['draftRank'], self.styleSheet)
              , Paragraph(data['score'], self.styleSheet)
              , Paragraph(data['rank'], self.styleSheet)
              , Paragraph(data['obs_types'], self.styleSheet)
              , Paragraph(data['rq_time'], self.styleSheet)
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

    def proposalIsNotSponsored(self, proposal):
        "For filtering out sponsored proposals."
        return not proposal.isSponsored()

    def reportWithoutSponsors(self, semester = None):
        filter = self.proposalIsNotSponsored
        self.report(semester = semester, filter = filter)

if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Command line tool for running GB PHT Linear Ranking reports.  Specify at least a semester.')
    parser.add_argument('-s','--semester', dest="semester", help='Semester of the proposals.')
    parser.add_argument('-x', '--exclude_sponsors', help='Exclude sponsored proposals from this report', action='store_true')

    args = parser.parse_args()

    if args.semester is None:
        print "Semester is a required option :)"
        sys.exit(0)
    else:
        semester = args.semester

    fn = 'proposalRanking.pdf'
    pr = ProposalRanking(filename = fn)
    filter = pr.proposalIsNotSponsored if args.exclude_sponsors else None
    pr.report(semester = semester, filter = filter)


