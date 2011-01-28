import math

from Document       import Document
from EquationParser import EquationParser
from functions      import *

class Term(Document):
    def __init__(self, keyword, value = None, equation = '', units = None):
        Document.__init__(self)

        self.keyword      = keyword
        self.value        = value
        self.equation     = equation
        self.units        = units
        self.changed      = False

        self.variables = {}
        for keyword in EquationParser()(self.equation):
            self.variables[keyword] = None

        if self.isJustValue():
            self.set(eval(self.equation))

    def __eq__(self, x):
        return x == self.value

    def __str__(self):
        return self.keyword

    def __repr__(self):
        return self.keyword

    def get(self):
        return self.value, self.units, self.equation

    def set(self, value):
        if self.value is not None and self.value != value:
            self.changed = True

        if value is None and self.isJustValue():
            self.set(eval(self.equation))
        elif value is None and not self.isJustValue():
            self.value = None
        else:
            self.value = value

    def evaluate(self, term):
        if term.keyword in self.variables.keys():
            self.variables[term.keyword] = term.value
            if term.value is None or term.changed:
                self.value = None # need to recalculate
        else:
            return

        if (self.value is None or term.changed) and \
           self.variables and \
           None not in self.variables.values():
            self.set(eval(self.equation, globals(), self.variables))
            term.changed = False
            self.notify(self.keyword, self.value)

    def isJustValue(self):
        return self.equation and not self.hasDependencies()

    def hasDependencies(self):
        return self.variables.keys() != []
