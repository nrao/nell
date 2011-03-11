import unittest
from calculator.utilities  import TSkyImport

class TestTSkyImport(unittest.TestCase):

    def test_import(self):
        tsky = TSkyImport('calculator/data/tsky.dat')
