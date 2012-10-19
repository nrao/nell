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

def defaultFilter(proposal):
    return 'TGBT' not in proposal.pcode

class ProposalWorksheet(Report):

    def __init__(self, filename):
        self.filename = filename
        super(ProposalWorksheet, self).__init__(filename, orientation = 'portrait')

    def genHeader(self, proposal):
        pi_name  = proposal.pi.getLastFirstName() if proposal.pi is not None else ''
        content = [[self.pg('<b>%s</b>' % proposal.pcode)
                  , self.pg(pi_name)
                  , self.pg('%s - %s' % (proposal.requestedTime(), proposal.bands()))
                  , self.pg(proposal.title)
                    ],
                   [self.pg('')
                  , self.pg('')
                  , self.pg('')
                  , self.pg('')
                  , self.pg(''.join([o.code for o in proposal.observing_types.all()]))
                    ]]
        proposalHeader = Table(content, colWidths = [50, 75, 50, 300, 50])
        proposalHeader.setStyle(self.tableStyle)

        data = [proposalHeader]
        data.extend([self.getBreak()] * 10)
        return data

    def reports(self, semester, filter = None):
        filter = filter or defaultFilter
        proposals = [p for p in Proposal.objects.filter(semester__semester = semester).order_by('pcode') if filter(p)]
        contents = []
        for header in map(self.genHeader, proposals):
            contents.extend(header)
        self.doc.build(contents
                     , onFirstPage = self.makeFooter
                     , onLaterPages = self.makeFooter)
        
    def report(self, proposal):
        contents = self.genHeader(proposal)
        self.doc.build(contents
                     , onFirstPage = self.makeFooter
                     , onLaterPages = self.makeFooter)

    def makeFooter(self, canvas, doc):
        pass

        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Command line tool for creating Proposal Worksheets. Specify least a semester or pcode.')
    parser.add_argument('-s','--semester', dest="semester", help='Semester of the proposals.')
    parser.add_argument('-p','--pcode', dest="pcode", help='Run report for a given pcode (Ex. GBT12B-100)')

    args = parser.parse_args()

    if args.pcode is not None:
        proposal = Proposal.objects.get(pcode = args.pcode)
        ps = ProposalWorksheet('proposalWorksheet_%s.pdf' % args.pcode)
        ps.report(proposal)
    elif args.semester is not None:
        ps = ProposalWorksheet('proposalWorksheet_%s.pdf' % args.semester)
        ps.reports(args.semester)
