######################################################################
#
#  Report.py: defines a simple report class which can take lines or
#  embedded reports.  Useful for making tables in reports.
#
#  Copyright (C) 2009 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
#  $Id:$
#
######################################################################

from pprint import pprint

class Line:

    def __init__(self, line = None):
        if line == None:
            self.clear()
        else:
            self.columns = line.columns[:]
            self.widths = line.widths[:]

    def add(self, col, datatype = None):
        if datatype == None:
            datatype = type(col)

        if datatype == type(1.0):
            width = len(str("%5.2f" % col))
            col = float(col)
        else:
            width = len(str(col))

        self.columns.append(col)
        self.widths.append(width + 2)

    def get_widths(self):
        return self.widths

    def set_widths(self, w):
        self.widths = w

    def clear(self):
        self.columns = []
        self.widths = []

    def my_type(self):
        return "Line"

    def normalize(self):
        pass

    def _ljust(self, value, width, datatype = None):
        if datatype == None:
            datatype = type(value)

        # watch out for floats
        if datatype == type(3.14):
            return str("%5.2f" % value)[:width].ljust(width)
        else:
            return str(value)[:width].ljust(width)


    def output(self, widths = None, indent = 0):

        if widths == None:
            w = self.widths
        else:
            w = widths

        os = ''

        for i in range(0, len(self.columns)):
            os += self._ljust(self.columns[i], w[i])

        print indent * " " + os


class Report:

    def __init__(self, report = None):

        if report == None:
            self.clear()
        else:
            self.elements = report.elements[:]
            self.headers = Line(report.headers)
            self.widths = report.widths[:]
            self.indent = report.indent

    def add_headers(self, headers):
        self.headers = Line(headers);
        self._set_widths(headers.get_widths())

    def add_line(self, line):
        l = Line(line)
        self.elements.append(l)
        self._set_widths(line.get_widths())

    def add_report(self, report):
        r = Report(report)
        report.indent = self.indent + 4
        self.elements.append(report)

    def lines(self):
        return len(self.elements)

    def my_type(self):
        return "Report"

    def output(self, widths = None, indent = None):

##         if self.indent > 0:
##             print

        underscore = " " * self.indent + "-" * sum(self.widths)

        if self.headers:
            self.headers.output(self.widths, self.indent)
            print underscore

        for i in self.elements:
            i.output(self.widths, self.indent)

##         if self.indent > 0:
##             print

    def clear(self):
        self.elements = []
        self.headers = None
        self.widths = []
        self.indent = 0


    def normalize(self):
        wm = {}

        for i in self.elements:
            w = i.get_widths()
            l = len(w)

            if not wm.has_key(l):
                wm[l] = []

                for i in range(0, l):
                    wm[l].append([])

            for i in range(0, l):
                wm[l][i].append(w[i])

        max_w = {}

        for i in wm.keys():
            max_w[i] = [max(x) for x in wm[i]]

        for i in self.elements:
            l = len(i.get_widths())
            i.set_widths(max_w[l])
            i.normalize()

    def get_widths(self):
        return self.widths

    def set_widths(self, w):
        self.widths = w

    def _set_widths(self, widths):

        w = []

        if len(self.widths) > len(widths):
            w1 = self.widths
            w2 = widths
        else:
            w1 = widths
            w2 = self.widths

        for i in range(0, len(w2)):
            w.append(max(w1[i], w2[i]))

        for i in range(len(w2), len(w1)):
            w.append(w1[i])

        self.widths = w
