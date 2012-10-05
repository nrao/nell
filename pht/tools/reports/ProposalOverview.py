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
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units  import inch

from Report             import Report
from pht.models         import Proposal
from pht.tools.database import PstInterface

class ProposalOverview(Report):

    def __init__(self, filename):
        super(ProposalOverview, self).__init__(filename, orientation = 'portrait')

    def setRankProposals(self, proposals):
        self.rankedProposals = sorted(proposals, key = lambda p: p.normalizedSRPScore)
        
    def report(self, proposal):
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
        mainData = [[proposalHeader], [proposalTable]]
        main = Table(mainData, colWidths = [500])
        main.setStyle(self.tableStyle)
        
        # write the document to disk (or something)
        docData = [main]
        docData.extend(self.genComments(proposal))
        self.doc.build(docData
                     , onFirstPage = self.makeFooter
                     , onLaterPages = self.makeFooter)


    def genComments(self, proposal):
        # Need to fetch some comments from the PST DB
        pst      = PstInterface()
        reviews  = pst.getProposalTechnicalReviews(proposal.pcode)
        ps       = ParagraphStyle(name = 'Heading1', fontSize = 10, leading = 16)
        contents = [Paragraph('<b>Scientific Ratings</b>', ps)
                  , self.pg(proposal.comments.srp_to_pi.replace('\n\n', '<br/><br/>'))
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
        contents.extend([Paragraph('<b>NRAO Comments</b>', ps)
                       , Paragraph(proposal.comments.nrao_comment, reviewStyle)
                         ])
        return contents
                
    def makeFooter(self, canvas, doc):
        pass

        
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'Usage: ProposalOverview.py <pcode>'
        sys.exit()
    pcode    = sys.argv[1]
    proposal = Proposal.objects.get(pcode = pcode)
    ps = ProposalOverview('proposalOverview_%s.pdf' % pcode)
    ps.setRankProposals(Proposal.objects.filter(semester__semester = proposal.semester.semester))
    ps.report(proposal)
