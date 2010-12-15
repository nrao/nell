from calculator.utilities  import EquationParser

import unittest

class TestEquationParser(unittest.TestCase):

    def test_call(self):
        eq      = "y = m * x + b"
        deplist = EquationParser()(eq)
        self.assertEqual(['m', 'x', 'b'], deplist)

if __name__ == "__main__":
    unittest.main()
