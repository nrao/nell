import settings
import os, unittest

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

class CalculatorTestCase(unittest.TestCase):

    def setUp(self):
        self.old_sc_equation_defs = settings.SC_EQUATION_DEFS
        settings.SC_EQUATION_DEFS = 'test.cfg'

        f = open(settings.SC_EQUATION_DEFS, 'w')
        f.write(equations)
        f.close()

    def tearDown(self):
        os.remove(settings.SC_EQUATION_DEFS)
        settings.SC_EQUATION_DEFS = self.old_sc_equation_defs

    def addTerm(self, equation, units = None):
        eqs = "".join(open(settings.SC_EQUATION_DEFS).readlines())
        fst, snd = eqs.split("[units]")
        fst += equation + "\n"
        if units is not None:
            snd += units + "\n"
        new_equations = fst + "[units]" + snd
        f = open(settings.SC_EQUATION_DEFS, 'w')
        f.write(new_equations)
        f.close()
        
    def resetTerms(self):
        f = open(settings.SC_EQUATION_DEFS, 'w')
        f.write(equations)
        f.close()

