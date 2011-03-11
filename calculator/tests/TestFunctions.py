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
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 12.5, 8, 8, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 12.5, 1, 8, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

    def test_dec2Els(self):
        min_el, max_el = dec2Els(-20)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(31.57, max_el, 2)

        min_el, max_el = dec2Els(20)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(71.57, max_el, 2)

        min_el, max_el = dec2Els(38.43)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(90, max_el, 2)

        min_el, max_el = dec2Els(50)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(78.43, max_el, 2)

        min_el, max_el = dec2Els(60)
        self.assertAlmostEqual(8.43, min_el, 2)
        self.assertAlmostEqual(68.43, max_el, 2)

        min_el, max_el = dec2Els(85)
        self.assertAlmostEqual(33.43, min_el, 2)
        self.assertAlmostEqual(43.43, max_el, 2)

    def test_calculateEST0(self):
        for wv in WeatherValues.objects.all():
            r = calculateEST0(wv.frequency * 1000, 1)
            if wv.frequency < 85 and wv.frequency > 93:
                self.assertAlmostEqual(r, wv.est0, 1)

        for wv_must in WeatherValues.objects.exclude(t_rcvr_mustang = None):
            r = calculateEST0(wv_must.frequency * 1000, 1, 'Mustang')
            self.assertAlmostEqual(r, wv_must.est0_mustang, 1)

    def test_calculateAttenuation(self):
        attenuation = calculateAttenuation(2.11, 1420)
        self.assertAlmostEqual(attenuation, 0.961, 3)

    def test_calcTsky(self):
        t = calcTsky(0, 0, 1420, 'model')
        self.assertAlmostEqual(t, 0.6992, 4)
        t = calcTsky(60, 70, 1420, 'model')
        self.assertAlmostEqual(t, 0.8164, 4)
        
