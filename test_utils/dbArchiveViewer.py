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

import matplotlib
matplotlib.use('Agg')

from pylab import *
from dbArchiveReader import dbArchiveReader
from datetime        import datetime
import time

class dbArchiveViewer:
    """
    This class is responsible for reading benchmark tests from the database,
    creating plots of these results, and saving them as .png files.
    """

    def __init__(self):
        
        self.colorNames = ['red', \
            'green', \
            'blue', \
            'purple', \
            'maroon', \
            'aqua', \
            'lime', \
            'fuchsia', \
            'olive', \
            'navy', \
            'teal', \
            'yellow', \
            'silver', \
            'gray', \
            'black' ]

        # set default value for directory to write images to
        self.exportDir = '.'

        # by default, images will always be overwritten, and unique
        # filenames for the images will NOT be used
        self.backupImages = 0

    def setExportDirectory(self, dir):
        "Sets the location where images are written to"
        self.exportDir = dir

    def setBackupImagesOn(self):
        "Unique image files will be saved off every time viewer is run."
        self.backupImages = 1

    def setBackupImagesOff(self):
        "Unique image files will not be saved off every time viewer is run."
        self.backupImages = 0

    def run(self):
        "Reads database, creates plots, and exports them.  Must be called from DEAP."

        
        # time that we are running this - for use with backup images
        #timestamp = DateTime.now().Format("%Y_%m_%d_%H_%M_%S")
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        # create a plot for every table in database
        reader = dbArchiveReader()
        testTables = reader.getTestTables()
        for testTable in testTables:
            color = 0
            # clear plot
            clf()
            
            # set title and labels
            date = time.asctime()
            title("%s tests" % testTable)
            ylabel("elapsed time (seconds)")
            xlabel("start time")
            maxX = []
            for test in testTables[testTable]:
                # x = start time
                # y = elapsed time
                sy, sx = \
                  zip(*reader.getTestElapsedAndStartTimes(testTable, test))
                x = [datetime.strptime(s, "%Y-%m-%d %H:%M:%S") for s in sx]
                y = [float(s) for s in sy]
                if len(x) > 1 and len(y) > 1:
                    # plot the data
                    testColor = self.colorNames[color]
                    #print "Test: %s, Color: %s" % (test, testColor)
                    plot_date(x,y,color=testColor,linestyle='-',marker='None',label=test)
                        
                    color += 1
                    if len(x) > len(maxX): maxX = x 
                    # fix the tick problem for large plots
                    if len(maxX) > 20:
                        ticks = []
                        lenX = len(maxX)
                        stepSize = int(lenX/5)
                        step = 0
                        for i in range(5):
                            if step < lenX:
                                ticks.append(maxX[step])
                            step +=stepSize
                            ticks.append(maxX[-1])    
                        xticks(ticks)

            leg = legend(loc=2)
            for t in leg.get_texts():
                t.set_fontsize(6)

            # export the plot
            filename = self.exportDir + '/' + testTable + '.png'
            savefig(filename)
            # save off this instance of the image using a unique filename
            if self.backupImages:
                name = testTable + '_' + timestamp
                filename = self.exportDir + '/' + name + '.png'
                savefig(filename)
                    
if __name__ == "__main__":
    dbv = dbArchiveViewer()
    dbv.run()
