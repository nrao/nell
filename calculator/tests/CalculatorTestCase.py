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

