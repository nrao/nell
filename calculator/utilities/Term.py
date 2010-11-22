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
        if value is None:
            self.value = None
            for k in self.variables.keys():
                self.variables[k] = None
        else:
            self.value = value

    def evaluate(self, term):
        if term.keyword in self.variables.keys():
            self.variables[term.keyword] = term.value
            if term.value is None:
                self.value = None # need to recalculate

        if self.value is None and \
           self.variables and \
           None not in self.variables.values():
            self.set(eval(self.equation, globals(), self.variables))
            self.notify(self.keyword, self.value)

    def isJustValue(self):
        return self.equation and not self.hasDependencies()

    def hasDependencies(self):
        return self.variables.keys() != []
