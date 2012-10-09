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
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units  import inch

from Report             import Report
from pht.models         import Proposal
from pht.tools.database import PstInterface

class ProposalOverview(Report):

    def __init__(self, filename):
        self.filename = filename
        super(ProposalOverview, self).__init__(filename, orientation = 'portrait')

    def setRankProposals(self, proposals):
        self.rankedProposals = sorted(proposals, key = lambda p: p.normalizedSRPScore)

    def semesterReport(self, proposals):
        contents = []
        for overview in map(self.genOverview, proposals):
            contents.extend(overview)
            contents.append(PageBreak())
            
        self.doc.build(contents
                     , onFirstPage = self.makeFooter
                     , onLaterPages = self.makeFooter)
                       
    def report(self, proposal):
        overview = self.genOverview(proposal)

        self.doc.build(overview
                     , onFirstPage = self.makeFooter
                     , onLaterPages = self.makeFooter)
                     
    def genOverview(self,proposal):
        data = [[self.pg('<b>%s</b>' % proposal.pcode)
              , self.pg(proposal.title)
                ]]

        proposalHeader = Table(data, colWidths = [100, 300])
        joint    = 'Joint' if proposal.joint_proposal else 'Not Joint'
        pi_name  = proposal.pi.getLastFirstName() if proposal.pi is not None else ''
        rank     = self.rankedProposals.index(proposal) + 1
        percentile = round(100 * (len(self.rankedProposals) - rank) / float(len(self.rankedProposals)))

        proposalData = [[self.pg(proposal.proposal_type.type)
                       , self.pg(joint)
                       , self.pg(pi_name)
                       , self.pg('Bands: %s' % proposal.bands())
                       , self.pg('Back ends: %s' % proposal.backends())
                         ],
                        [self.pg('Req Time (hrs): %s' % proposal.requestedTime())
                       , self.pg('Type of Obs: %s' % ', '.join([o.code for o in proposal.observing_types.all()]))
                         ],
                        [self.pg('<b>SRP Grade:</b> %s' % proposal.normalizedSRPScore)
                       , self.pg('<b>Rank:</b> %s' % str(rank))
                       , self.pg('<b>#Refs:</b> %s' % proposal.num_refs)
                       , self.pg('<b>Percentile:</b> %i%%' % percentile)
                         ],
                          ]
        proposalTable = Table(proposalData, colWidths = [100, 100, 100, 100, 100])
        psumContent = [[proposalHeader], [proposalTable]]
        summary = Table(psumContent, colWidths = [500])
        summary.setStyle(self.tableStyle)
        overview = [summary]
        overview.extend(self.genComments(proposal))
        return overview

    def genComments(self, proposal):
        # Need to fetch some comments from the PST DB
        pst      = PstInterface()
        reviews  = pst.getProposalTechnicalReviews(proposal.pcode)
        ps       = ParagraphStyle(name = 'Heading1', fontSize = 10, leading = 16)
        sciComment = proposal.comments.srp_to_pi if proposal.comments is not None else ''
        sciComment = sciComment.replace('\n\n', '<br/><br/>') if sciComment is not None else ''
        contents = [Paragraph('<b>Scientific Ratings</b>', ps)
                  , self.pg(sciComment)
                  , Paragraph('<b>Technical Ratings</b>', ps)
                    ]
        reviewStyle  = ParagraphStyle(name = 'Review', fontSize = 8, leftIndent = 20)
        reviewStyle2 = ParagraphStyle(name = 'Review', fontSize = 8, leftIndent = 40)
        for tech4Auth, tech4Tac, refF, refL in reviews:
            rf, rl = '', ''
            if refF is not None and refL is not None:
                rf, rl = refF[0], refL[0]
            contents.extend(
                [Paragraph('<b>Ref</b> %s%s' % (rf, rl), reviewStyle)
               , Paragraph(tech4Auth.replace('\n', '<br/>'), reviewStyle2)
               , Paragraph('<b>To Selection Committee</b>', reviewStyle)
               , Paragraph(tech4Tac.replace('\n', '<br/>'), reviewStyle2)
                        ])
        nraoComment = (proposal.comments.nrao_comment if proposal.comments is not None else '') or ''
        contents.extend([Paragraph('<b>NRAO Comments</b>', ps)
                       , Paragraph(nraoComment, reviewStyle)
                         ])
        return contents
                
    def makeFooter(self, canvas, doc):
        pass

        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Command line tool for running GB PHT Proposal Overview reports.  Specify at least a semester or pcode.')
    parser.add_argument('-s','--semester', dest="semester", help='Semester of the proposals.')
    parser.add_argument('-p','--pcode', dest="pcode", help='Run report for a given pcode (Ex. GBT12B-100)')
    parser.add_argument('-t','--test', dest="test", type = bool, default = False, help='Include testing and commissioning proposals.')

    args = parser.parse_args()

    if args.pcode is not None:
        proposal = Proposal.objects.get(pcode = args.pcode)
        ps = ProposalOverview('proposalOverview_%s.pdf' % args.pcode)
        ps.setRankProposals(Proposal.objects.filter(semester__semester = proposal.semester.semester))
        ps.report(proposal)
    elif args.semester is not None:
        proposals = Proposal.objects.filter(semester__semester = args.semester).order_by('pcode')
        if not args.test:
            proposals = [p for p in proposals if 'TGBT' not in p.pcode]
        ps = ProposalOverview('proposalOverview_%s.pdf' % args.semester)
        ps.setRankProposals(proposals)
        ps.semesterReport(proposals)
        
