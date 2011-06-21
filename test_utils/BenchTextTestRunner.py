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

import unittest
import time

class _BenchTextTestResult(unittest._TextTestResult):

    def __init__(self, a, b, c):
        unittest._TextTestResult.__init__(self, a, b, c)
        self.elapsedTime = []

    def stopTest(self, test):
        "saves the elapsed time for the test that just stopped"
        unittest._TextTestResult.stopTest(self, test)
        self.elapsedTime.append((test, test.getElapsedTime()))
        
    def printTimes(self):
        "like printErrors, prints out the elapsed time for each test"
        self.stream.writeln(self.separator1)
        for test, timeElapsed in self.elapsedTime:
            self.stream.writeln("%s: %f" %(self.getDescription(test),timeElapsed))
    
        
class BenchTextTestRunner(unittest.TextTestRunner):

    def _makeResult(self):
        return _BenchTextTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = float(stopTime - startTime)
        result.printErrors()
        # only added line: print the times for each test as well
        result.printTimes()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()
        if not result.wasSuccessful():
            self.stream.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.stream.write("failures=%d" % failed)
            if errored:
                if failed: self.stream.write(", ")
                self.stream.write("errors=%d" % errored)
            self.stream.writeln(")")
        else:
            self.stream.writeln("OK")
        return result
        
