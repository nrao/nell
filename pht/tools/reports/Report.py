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

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units  import inch


class Report(object):

    """
    This is an abstract class that utilizies reportlab to create
    a PDF report.
    """

    def __init__(self
               , filename
               , orientation = 'portrait'
               , topMargin = None
                ):

        # portrait or landscape?
        w, h      = letter
        self.orientation = orientation 
        if self.orientation == 'portrait':
            self.pagesize = (w, h)
        else:
            self.pagesize = (h, w)

        # set up the page    
        if topMargin is None:
            self.doc  = SimpleDocTemplate(filename, pagesize = self.pagesize)
        else:    
            self.doc  = SimpleDocTemplate(filename
                                        , pagesize = self.pagesize
                                        , topMargin = topMargin)

        self.styleSheet = getSampleStyleSheet()['Normal']
        self.styleSheet.fontSize = 7

        self.tableStyle = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])

        self.titleOffset = 0

    def truncateStr(self, string, length):
        return string if len(string) <= length else string[:length]
    

    def pg(self, text, bold = False):
        "Shortcut to Paragraph"
        if bold:
            text = "<b>%s</b>" % text
        return Paragraph(text, self.styleSheet) 

    def getBreak(self):
        return Paragraph('<br/>', self.styleSheet)

    def genFooter(self, canvas, doc):
        pass

    def makeHeaderFooter(self, canvas, doc):
        canvas.saveState() 
        canvas.setFont('Times-Roman', 20) 
        w, h = letter

        if self.orientation == 'portrait':
            canvas.drawString(20, h-40, self.title)
        else:
            canvas.drawString(w-self.titleOffset, w-40, self.title)
        self.genFooter(canvas, doc)

