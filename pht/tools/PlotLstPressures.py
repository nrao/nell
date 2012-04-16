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

from pht.tools.LstPressures import LstPressures

from matplotlib.backends.backend_agg import FigureCanvasAgg 
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy

class PlotLstPressures(object):

    def __init__(self):
        self.lst = LstPressures()

        self.initPlots()

    def initPlots(self):


        self.figure = Figure(figsize=(6,6))
        self.axes = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
        self.canvas = None

    def plot(self, type):

        print "getting pressures"
        self.lst.getPressures()
        print "done w/ pressures"

        # what type of plot?
        # TBF: for now, just do the totals ...
        #self.plotTotals()
        self.plotPoor()

    def plotTotals(self):

    
        stacks = [
            {'data': self.lst.carryoverTotalPs
           , 'color': 'orange'}
           # grade A
          , {'data': self.lst.gradePs['A'].excellent
           , 'color': self.getColor('A', 'excellent')}
          , {'data': self.lst.gradePs['A'].good
           , 'color': self.getColor('A', 'good')}
          , {'data': self.lst.gradePs['A'].poor
           , 'color': self.getColor('A', 'poor')}
           # grade B
          , {'data': self.lst.gradePs['B'].excellent
           , 'color': self.getColor('B', 'excellent')}
          , {'data': self.lst.gradePs['B'].good
           , 'color': self.getColor('B', 'good')}
          , {'data': self.lst.gradePs['B'].poor
           , 'color': self.getColor('B', 'poor')}
           # grade C
          , {'data': self.lst.gradePs['C'].excellent
           , 'color': self.getColor('C', 'excellent')}
          , {'data': self.lst.gradePs['C'].good
           , 'color': self.getColor('C', 'good')}
          , {'data': self.lst.gradePs['C'].poor
           , 'color': self.getColor('C', 'poor')}
          , {'data': self.lst.requestedTotalPs
           , 'color': 'yellow'}
                ]
       
        self.plotPressureData(stacks, "Total Pressure")
    
    def plotPoor(self):

        stacks = [
            {'data': self.lst.carryoverPs.poor
           , 'color': 'orange'}
          , {'data': self.lst.gradePs['A'].poor
           , 'color': self.getColor('A', 'poor')}
          , {'data': self.lst.gradePs['B'].poor
           , 'color': self.getColor('B', 'poor')}
          , {'data': self.lst.gradePs['C'].poor
           , 'color': self.getColor('C', 'poor')}
          , {'data': self.lst.requestedPs.poor
           , 'color': 'yellow'}
                ]
       
        self.plotPressureData(stacks, "Poor")

    def plotPressureData(self, stacks, title):

        ind = numpy.arange(self.lst.hrs)
        total = numpy.zeros(self.lst.hrs)
        for stack in stacks:
            data = stack['data']
            print data
            self.axes.bar(ind, data, color=stack['color'], bottom=total)
            total += data

        self.figure.suptitle(title, fontsize=14)
        self.canvas = FigureCanvasAgg(self.figure)

    def getColor(self, grade, weatherType):

        grades = ['A', 'B', 'C']

        reds = ('#FF0000', '#FF8080', '#FFCCCC')
        blues = ('#0000FF', '#8080FF', '#CCCCFF')
        greens = ('#00FF00', '#99FF99', '#e5FFe5')

        colors = {'excellent' : blues
                , 'good' : greens
                , 'poor' : reds
                 }

        return colors[weatherType][grades.index(grade)]

    def printPlot(self, filename):
        self.canvas.print_png(filename)

if __name__ == '__main__':
    plot = PlotLstPressures()

