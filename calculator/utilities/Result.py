from Document  import Document
from Term        import Term
from OrderedDict import OrderedDict
from utilities.FormatExceptionInfo import formatExceptionInfo

from threading import Thread, Lock
from Queue     import Queue
from exceptions import RuntimeError

import ConfigParser, time
import settings
import sys

class Result(Thread):

    @staticmethod
    def getEquations(section):
        config = ConfigParser.RawConfigParser()
        config.read(settings.SC_EQUATION_DEFS)

        if section is None:
            section = 'equations'

        equations = {}
        for term, equation in config.items(section):
            equations[term] = [equation, None, None, None]

        for term, unit in config.items('units'):
            if equations.has_key(term):
                equations[term][1] = unit

        for term, label in config.items('labels'):
            if equations.has_key(term):
                equations[term][2] = label

        for term, display in config.items('displays'):
            if equations.has_key(term):
                digits, order = map(lambda s: s.strip(), display.split(','))
                equations[term][3] = digits, int(order)

        return [(t, e, u, l, d) for t, (e, u, l, d) in equations.items()]

    def __init__(self, section):
        Thread.__init__(self)

        self.lock  = Lock()
        self.queue = Queue()
        self.loop = True

        self.terms = {}
        for t, equation, units, label, display in Result.getEquations(section):
            self.terms[t] = Term(t, None, equation, units, label, display)
            self.terms[t].addObserver(self)

        self.start() # Start queue thread

        # Trigger the first round of calculations.
        for key, term in self.terms.items():
            value = term.get()[0]
            if value is not None:
                self.set(key, value)

    def __del__(self):
        self.loop = False

    def get(self, key = None):
        while True:
            self.queue.join()
            self.lock.acquire()
            if self.queue.empty():
                try:

                    if key and self.terms.has_key(key):
                        term   = self.terms[key]
                        result = term.get()
                    else: # all of it
                        result = {}
                        for key, term in self.terms.items():
                            result[key] = term.get()
                except:
                    print formatExceptionInfo()
                finally:
                    self.lock.release()
                    return result
            else:
                self.lock.release()

    def set(self, key, value):
        self.lock.acquire()
        try:
            if self.terms.has_key(key):
                self.terms[key].set(value)
                for _, term in self.terms.items():
                
                    if value is None and term.isDependentOn(key):
                        term.set(None) # clear the board
                    else:
                        term.evaluate(self.terms[key]) # move the ball forward
        except:
            print "Caught %s with value %s" % (key, value)
            print formatExceptionInfo()
        finally:
            self.lock.release()

    def onNotify(self, key, value):
        self.queue.put((key, value))

    def run(self):
        while self.loop:
            try:
                key, value = self.queue.get(True, 1)
                self.set(key, value)
                self.queue.task_done()
            except:
                pass
