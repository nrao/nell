from calculator.utilities.Result import Result

import unittest

class TestResultCalculations(unittest.TestCase):

    def setUp(self):
        super(TestResultCalculations, self).setUp()
        self.results = Result('equations')
        self.results.set('frame', 'topocentric frame')
        self.results.set('topocentric_freq', 1420)

    def tearDown(self):
        super(TestResultCalculations, self).tearDown()
        self.results.__del__()

    def test_fwhm(self):
        value, _, _, _, _ = self.results.get('fwhm')
        self.assertAlmostEqual(4.341, value, 3)

    def test_source_diameter(self):
        self.results.set('source_diameter_slider', 2)
        value, _, _, _, _ = self.results.get('source_diameter')
        self.assertAlmostEqual(0.868, value, 3)
        
    def test_topocentric_wavelength(self):
        value, _, _, _, _ = self.results.get('topocentric_wavelength')
        self.assertAlmostEqual(21.127, value, 3)

    def test_aperture_eff(self):
        value, _, _, _, _ = self.results.get('aperture_eff')
        self.assertAlmostEqual(0.6997, value, 4)

    def test_extended_source_eff(self):
        self.results.set('source_diameter_slider', 2)
        value, _, _, _, _ = self.results.get('extended_source_eff')
        self.assertAlmostEqual(0.690, value, 3)

    def test_confusion_limit(self):
        self.results.set('source_diameter_slider', 2)
        self.results.set('units', 'flux')
        value, _, _, _, _ = self.results.get('confusion_limit')
        self.assertAlmostEqual(0.015, value, 3)

        self.results.set('units', 'tr')
        value, _, _, _, _ = self.results.get('confusion_limit')
        self.assertAlmostEqual(2.9692268088858926e+18, value, 0)

        self.results.set('units', 'ta')
        value, _, _, _, _ = self.results.get('confusion_limit')
        self.assertAlmostEqual(1.2168111723765818e+25, value, 3)
