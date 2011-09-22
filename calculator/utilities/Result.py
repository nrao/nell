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

from Document  import Document
from Term        import Term
from utilities.FormatExceptionInfo import formatExceptionInfo

from threading import Thread, Lock
from Queue     import Queue
from exceptions import RuntimeError

import ConfigParser, time
import settings
import sys

class Result(Thread):

    """
    This class is responsible for loading the equation definitions
    from a configuration file, and evaluating those equations
    using collections of Term objects, all thread safe.
    """

    @staticmethod
    def getEquations(section):
        """
        Loads the equation configuration file, and returns the 
        equation information as a list of tuples, where each tuple
        carries information such as the euqation's units, it's label, etc
        """
       
        # parse the file
        config = ConfigParser.RawConfigParser()
        config.read(settings.SC_EQUATION_DEFS)

        if section is None:
            section = 'equations'

        # create a map of term to term attributes
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

        # convert our map into a list of tuples
        return [(t, e, u, l, d) for t, (e, u, l, d) in equations.items()]

    def __init__(self, section):
        Thread.__init__(self)

        self.lock  = Lock()
        self.queue = Queue()
        self.loop = True

        # for every term listed in the config file, create a Term obj.
        self.terms = {}
        for t, equation, units, label, display in Result.getEquations(section):
            self.terms[t] = Term(t, None, equation, units, label, display)
            # this class will have it's onNotify method called when
            # a term calls it's notify method.
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
        """
        Once the queue is empty, returns the named term's value, or
        all term values, if no specific term is named.
        """

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
                    #print formatExceptionInfo()
                    pass
                finally:
                    self.lock.release()
                    return result
            else:
                self.lock.release()

    def set(self, key, value):
        """
        Sets the value of the term specified by the given key,
        and then evaluates all terms that are dependent on this key.
        """

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
            #print "Caught %s with value %s" % (key, value)
            #print formatExceptionInfo()
            pass
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
