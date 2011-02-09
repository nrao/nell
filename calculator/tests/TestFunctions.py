import unittest

from calculator.utilities.functions import *

class TestFunctions(unittest.TestCase):

    def test_sourceSizeCorrection(self):
        correction = sourceSizeCorrection(6, 8)
        self.assertAlmostEqual(correction, 0.828, 3)

    def test_getKs(self):
        k1, k2 = getKs('Spectral Processor', 1, 1, 1, 1)  #  bandwidth, bw, windows, and beams not used
        self.assertEqual(k1, 1.3)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 200, 1, 1, 1)  #  bw, windows, and beams not used
        self.assertEqual(k1, 1.235)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 800, 1, 1, 1)  #  bw, windows, and beams not used
        self.assertEqual(k1, 1.235)
        self.assertEqual(k2, 1.21)

        
        k1, k2 = getKs('GBT Spectrometer', 50, 8, 8, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 50, 1, 8, 1)
        self.assertEqual(k1, 1.235)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 12.5, 8, 8, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 12.5, 1, 8, 1)
        self.assertEqual(k1, 1.235)
        self.assertEqual(k2, 1.21)

