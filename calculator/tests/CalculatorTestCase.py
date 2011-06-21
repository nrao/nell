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

from TestViewsBase import TestViewsBase
import settings
import os

equations = """
[equations]
time = size * sensitivity
airmass = sensitivity + size + time
sensitivity = 3 * size
size = 5
foo  = size + time + bar
bar =
#nop = 0 # lame comment
[units]
time = sec
size = meters
[labels]
[displays]
"""

class CalculatorTestCase(TestViewsBase):

    def setUp(self):
        super(CalculatorTestCase, self).setUp()
        self.old_sc_equation_defs = settings.SC_EQUATION_DEFS
        settings.SC_EQUATION_DEFS = 'test.cfg'

        f = open(settings.SC_EQUATION_DEFS, 'w')
        f.write(equations)
        f.close()

    def tearDown(self):
        super(CalculatorTestCase, self).tearDown()
        os.remove(settings.SC_EQUATION_DEFS)
        settings.SC_EQUATION_DEFS = self.old_sc_equation_defs

    def addTerm(self, equation, units = None):
        f   = open(settings.SC_EQUATION_DEFS)
        eqs = "".join(f.readlines())
        f.close()
        fst, snd = eqs.split("[units]")
        fst += equation + "\n"
        units_section, end = snd.split("[labels]")
        if units is not None:
            units_section += units + "\n"
        new_equations = fst + "[units]" + units_section + "[labels]" + end
        f = open(settings.SC_EQUATION_DEFS, 'w')
        f.write(new_equations)
        f.close()
        
    def resetTerms(self):
        f = open(settings.SC_EQUATION_DEFS, 'w')
        f.write(equations)
        f.close()

