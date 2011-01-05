from Archiver     import Archiver
from dbArchiver   import dbArchiver
from NellTestCase import NellTestCase
import settings
import unittest
import time

def timeIt(f):
    def new_f(self, *args):
        latency = self.timeFunc(f.__name__, f, *args)
        # actually prints the latency if not being archived
        self.archiver.printLatency(latency)
    return new_f

class BenchTestCase(NellTestCase):

    """
    This class extends the unittest.TestCase class in order to include
    measurments of perfomance time of desired test.
    """

    def __init__(self, methodName = 'runTest', archiver = Archiver()):
        super(BenchTestCase, self).__init__(methodName)

        self.archiver    = Archiver() if settings.BENCHMARK_DB_NAME is None else dbArchiver(self.__class__.__name__)
        self.elapsedTime = 0.0
        self.startTime   = 0.0
        self.stopTime    = 0.0

    def startTimer(self):
        """
        Records start time, and calls stub method for marking start
        of test. Used in conjunction with the following function to
        time portions of a test.
        """
     
        #self.getTestStartInfo()
        self.onStartTest()
        self.archiver.onStartTest()
        
        self.startTime = time.time()

        # save for posterity.
        self.saveValue("start_time", self.startTime)

        return self.startTime

    def stopTimer(self):
        """
        Records stop time and elapsed time, and calls stub method
        for marking end of test.
        """
        
        self.stopTime    = time.time() 
        self.elapsedTime = self.stopTime - self.startTime

        self.onEndTest()
        self.archiver.onEndTest()
        
        # save for posterity.
        self.saveValue("stop_time",    self.stopTime)
        self.saveValue("elapsed_time", self.elapsedTime)
        self.archiver.write()

        return self.stopTime

    def timeFunc(self, name, func, *args):
        """
        Calls a given function, and calculates its elapsed time.
        Used in conjunction with decorator timeIt to time an
        entire test.
        """
        
        # Save for posterity.
        self.saveValue("test_name", name)

        startTime = self.startTimer()
        func(self, *args)
        stopTime  = self.stopTimer()

        return stopTime - startTime
        
    def onStartTest(self):
        pass

    def onEndTest(self):
        pass 
        
    def assertTimeInRange(self, min, max):
        self.assertTimeLessThen(max)
        self.assertTimeGreaterThen(min)

    def assertTimeGreaterThen(self, minTime):
        if self.elapsedTime < minTime:
            raise self.failureException, \
                  ('time passed: %f less then min time: %f' % \
                   (self.elapsedTime, minTime))

    def assertTimeLessThen(self, maxTime):
        if self.elapsedTime > maxTime:
            raise self.failureException, \
                  ('time passed: %f greater then max time: %f' % \
                   (self.elapsedTime, maxTime))

    def assertTimeNotAboveAvg(self, avgRange):
        if self.getAvgElapsedTime() > avgRange:
            raise self.failureException, \
                  ('time passed: %f above average of %f by too much.' % \
                   (self.elapsedTime, 0.0))

    def getElapsedTime(self):
        return self.elapsedTime

    def getAvgElapsedTime(self):
        return self.archiver.getAvgElapsedTime()

    def getTestStartInfo(self):
        os.system("top b n 1 > startTop.txt")
        f = open("startTop.txt",'r')
        self.startTopLines = f.readlines()
        f.close()

    def getTestStopInfo(self):
        os.system("top b n 1 > stopTop.txt")
        f = open("stopTop.txt",'r')
        self.stopTopLines = f.readlines()
        f.close()

    def saveValue(self, name, value):
        self.archiver.setValue(name, value)

