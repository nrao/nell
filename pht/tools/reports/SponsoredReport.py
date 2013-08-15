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

from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib      import colors

from pht.models import *
from Report     import Report

REQUESTED = 'Requested'
ALLOCATED = 'Allocated'
LOST = 'Lost'
BILLED = 'Billed'
SCHEDULED = 'Scheduled'
REMAINING = 'Remaining'

class SponsoredReport(Report):

    """
    This class is responsible for producing a simple report on how the
    sponsored projects are coming along time accounting wise.
    """

    def __init__(self, filename, debug = False):
        super(SponsoredReport, self).__init__(filename
                                            , orientation = 'landscape')

        self.debug = debug

        self.title = 'Sponsor Report'

        self.headings = ['Pcode'
                  , 'Semester'
                  , 'Sponsor'
                  , REQUESTED 
                  , ALLOCATED 
                  , LOST 
                  , BILLED 
                  , SCHEDULED 
                  , REMAINING 
                    ]

        # redefine table style to include an inner grid
        self.tableStyle = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])

    def report(self):

        self.calculate()

        if self.debug:
            self.debugOutput()

        # header
        data = [self.genHeader()]

        # proposals - one per row
        pcodes = sorted(self.info.keys())
        data.extend([self.genRow(self.info[p]) for p in pcodes])
        t = Table(data, colWidths = [80]*len(self.headings))

        # now the last row of totals
        b = self.getBreak()
        data2 = [self.genTotalRow()]
        t2 = Table(data2, colWidths = [80]*len(self.headings))

        tables = [t, b, t2]

        # write the document to disk (or something)
        self.doc.build(tables
                    , onFirstPage = self.makeHeaderFooter
                    , onLaterPages = self.makeHeaderFooter)

    def genHeader(self):
        return [Paragraph('<b>%s</b>' % h, self.styleSheet) for h in self.headings]

    def genRow(self, info):
        "For each proposal"
        frmt = '%5.2f'
        row = ['%s' % info[0].pcode
             , '%s' % info[1] # semester
             , '%s' % info[2] # sponsor
              ]
        row.extend([frmt % f for f in info[3:]])
        return [Paragraph(r, self.styleSheet) for r in row]
    
    def genTotalRow(self):
        "The last row that sums up each column"
        frmt = '%5.2f'
        row = ['TOTAL', '', '']
        row.extend([frmt % self.totals[h] for h in self.headings[3:]])
        return [Paragraph(r, self.styleSheet) for r in row]

    def calculate(self):
        """
        Gather stats on the sponsored proposals.
        If this was more complicated, we'd put it in it's own class.
        """

        self.sponsoredPs = Proposal.objects.exclude(sponsor = None).order_by('pcode')

        self.info = {}
        self.totals= {}
        for k in self.headings[3:]:
            self.totals[k] = 0.0
                     
        for p in self.sponsoredPs:
            req = p.requestedTime()
            if p.dss_project is not None:
                dssAll = p.dssAllocatedTime()
                billed = p.billedTime()
                lost = p.lostTime()
                schd = p.scheduledTime()
                rem = p.remainingTime()
            else:
                dssAll = lost = billed = schd = rem = 0.0
            self.totals[REQUESTED] += req            
            self.totals[ALLOCATED] += dssAll
            self.totals[LOST] += lost
            self.totals[BILLED] += billed
            self.totals[SCHEDULED] += schd
            self.totals[REMAINING] += rem
            i = (p
               , p.semester.semester
               , p.sponsor.abbreviation
               , req
               , dssAll
               , lost
               , billed
               , schd
               , rem
                )
            self.info[p.pcode] = i   

    def debugOutput(self):
        "Print to stdout what you'd see in the PDF"

        tFrmt = "%-9.2f"
        frmt = "%-12s %-3s %-8s " + ("%-9s "*6)
        #PCODE        Sem Sponsor  Req       DssAll    Lost Billed Schd      Rem
        header = frmt % ("PCODE", "Sem", "Sponsor", "Req", "DssAll", "Lost", "Billed", "Schd", "Rem")
        print header
        for pcode in sorted(self.info.keys()):
            info = self.info[pcode]
            p, semester, sponsor = info[:3]
            times = info[3:]
            timesStr = ((" "+tFrmt) * len(times)) % times
            print "%-12s %-3s %-8s%s" % (p.pcode, semester, sponsor, timesStr)
        t = self.totals
        frmt = "%-12s %-3s %-8s"+((" "+tFrmt) * 6) 
        print frmt % ("TOTAL", "", "", t[REQUESTED], t[ALLOCATED], t[LOST], t[BILLED], t[SCHEDULED], t[REMAINING])

            
if __name__ == '__main__':
    # make a bunch of random proposals sponsored
    #from pht.models import Proposal
    #from scheduler.models import Sponsor
    #ps = Proposal.objects.filter(semester__semester = '13B').order_by('pcode')
    #wvu = Sponsor.objects.get(abbreviation = 'WVU')
    #for i in range(5,11):
    #    p = ps[i]
    #    p.sponsor = wvu
    #    p.save()
    sr = SponsoredReport('SponsorReport.pdf')
    sr.report()


