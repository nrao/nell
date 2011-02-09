from Document  import Document
from Term      import Term
from utilities.FormatExceptionInfo import formatExceptionInfo

from threading import Condition, Thread, Lock
from exceptions import RuntimeError

import ConfigParser, time
import settings

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
                equations[term][3] = display

        return [(t, e, u, l, d) for t, (e, u, l, d) in equations.items()]

    def __init__(self, section):
        Thread.__init__(self)

        self.lock  = Lock()
        self.queue = []
        self.queue_empty = Condition()
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
        try:
            self.join()
        except RuntimeError:
            pass

    def get(self, key = None):
        self.queue_empty.acquire()
        if self.queue:
            self.queue_empty.wait() # make sure all calcuations are complete

        if key and self.terms.has_key(key):
            term   = self.terms[key]
            result = term.get()
        else: # all of it
            result = {}
            for key, term in self.terms.items():
                result[key] = term.get()
        self.queue_empty.release()

        return result

    def set(self, key, value):
        self.lock.acquire()

        try:
            if self.terms.has_key(key):
                self.terms[key].set(value)
                for _, term in self.terms.items():
                    if value is None and term.hasDependencies() and not term.isJustValue():
                        term.set(None) # clear the board
                        for t in term.variables.keys():
                            if self.terms[t].isJustValue():
                                self.terms[t].set(None)
                            else:
                                term.variables[t] = None
                    else:
                        term.evaluate(self.terms[key]) # move the ball forward
                
        except:
            print "Caught %s with value %s" % (key, value)
            print formatExceptionInfo()
        finally:
            self.lock.release()

    def onNotify(self, key, value):
        self.queue_empty.acquire()
        self.queue.append((key, value)) # add to calcuation list, don't block
        self.queue_empty.release()

    def run(self):
        while self.loop:
            self.queue_empty.acquire()

            if self.queue:
                key, value = self.queue.pop(0)
                self.set(key, value)
            else:
                self.queue_empty.notify()

            self.queue_empty.release()
            time.sleep(.01)  #  Slow this puppy down a bit.
