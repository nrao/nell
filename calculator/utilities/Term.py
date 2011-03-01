import math

from Document             import Document
from EquationParser       import EquationParser
from functions            import *
from utilities.TimeAgent  import *

class Term(Document):
    def __init__(
        self, keyword, value = None, equation = '', units = None, label = None, display = None):
        Document.__init__(self)

        self.keyword      = keyword
        self.value        = value
        self.equation     = equation
        self.units        = units
        self.label        = label
        self.display      = display

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

    def renderDisplay(self):
        if self.display is not None and self.display != '':
            return self.display.replace('[value]', str(self.value)).replace('[units]', str(self.units))
        else:
            return self.value
        
    def renderLabel(self):
        return self.label if self.label is not None and self.label != '' else self.keyword

    def get(self):
        return self.value, self.units, self.equation, self.renderLabel(), self.display

    def set(self, value):
        if value is None and self.isJustValue():
            self.set(eval(self.equation))
        elif value is None and not self.isJustValue():
            self.value = None
        else:
            self.value = value

    def evaluate(self, term):
        if term.keyword in self.variables.keys():
            if term.value is None or self.variables[term.keyword] != term.value:
                self.value = None # need to recalculate
            self.variables[term.keyword] = term.value
        else:
            return

        if self.value is None and self.variables and \
           None not in self.variables.values():
            self.set(eval(self.equation, globals(), self.variables))
            self.notify(self.keyword, self.value)

    def isJustValue(self):
        return self.equation and not self.hasDependencies()

    def hasDependencies(self):
        return self.variables.keys() != []

    def isDependentOn(self, key):
        return key in self.variables.keys()
