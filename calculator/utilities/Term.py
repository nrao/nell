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

import math

from Document             import Document
from EquationParser       import EquationParser
from functions            import *
from utilities.TimeAgent  import *

class Term(Document):

    """
    This class embodies an equation and all it's attributes, as you 
    might find in the equations.cfg file.  For example, the term
    'max_elevation' has the following entries in this file:
        keyword : max_elevation 
        equation : getMaxElevation(declination)
        units : d # degrees
        labels : "Maximum Elevation"
        display : .1f, 50 # floating point, ?
    In addition, the dependencies listed in it's equation are kept
    track of, and other terms can be evaluated based off these
    dependencies.
    Terms are dependent on other Terms and will only be evaluated when 
    all their dependencies are met.
    """    
        

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
        """
        Uses the display and units attribute to return formatted 
        representation of the term's value.
        """
        if self.display is not None and self.display != '':
            return self.display.replace('[value]', str(self.value)).replace('[units]', str(self.units))
        else:
            return self.value
        
    def renderLabel(self):
        return self.label if self.label is not None and self.label != '' else self.keyword

    def get(self):
        return self.value, self.units, self.equation, self.renderLabel(), self.display

    def set(self, value):
        "Sets the value of our Term"
        if value is None and self.isJustValue():
            self.set(eval(self.equation))
        elif value is None and not self.isJustValue():
            self.value = None
        else:
            self.value = value

    def evaluate(self, term):
        """
        Part of the steps needed to find the final value for this
        term's equation; the given term should be a dependent of
        this term.
        """
        # is the given term one of our dependencies?
        if term.keyword in self.variables.keys():
            if term.value is None or self.variables[term.keyword] != term.value:
                self.value = None # need to recalculate
            # set this term's internal value    
            self.variables[term.keyword] = term.value
        else:
            return # if not, nothing to do

        # if we now have values for *all* our dependencies, and this
        # term doesn't have a value, then calculate our value
        if self.value is None and self.variables and \
           None not in self.variables.values():
            # calculate our value
            self.set(eval(self.equation, globals(), self.variables))
            # broadcast what we did
            self.notify(self.keyword, self.value)

    def isJustValue(self):
        "Is the equation just a constant, like 3.14?"
        return self.equation and not self.hasDependencies()

    def hasDependencies(self):
        return self.variables.keys() != []

    def isDependentOn(self, key):
        return key in self.variables.keys()
