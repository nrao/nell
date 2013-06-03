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

from calculator.utilities.Result import Result
from calculator.utilities.functions import dec2Els
from django.test import TestCase
import unittest

class TestGalacticModel(TestCase):
    fixtures = ['tsky_data.json']

    def test_galactic_model(self):
        self.results = Result('equations')
        self.results.set('frame', 'topocentric frame')
        self.results.set('topocentric_freq', 1420)
        self.results.set('declination', 38.43)
        self.results.set('right_ascension', 10.25)
        self.results.set('galactic', 'model')

        value, _, _, _, _ = self.results.get('t_galactic_model')
        self.assertTrue(value is not None)
        self.assertAlmostEqual(value, 0.5586, 4)

        self.results.__del__()

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
        self.assertAlmostEqual(8.677, value, 3)

    def test_source_diameter(self):
        self.results.set('source_diameter_slider', 2)
        value, _, _, _, _ = self.results.get('source_diameter')
        self.assertAlmostEqual(1.735, value, 3)
        
    def test_topocentric_wavelength(self):
        value, _, _, _, _ = self.results.get('topocentric_wavelength')
        self.assertAlmostEqual(21.112, value, 3)

    def test_aperture_eff(self):
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        value, _, _, _, _ = self.results.get('aperture_eff')
        self.assertAlmostEqual(0.6999, value, 3)

    def test_extended_source_eff(self):
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        self.results.set('source_diameter_slider', 2)
        self.results.set('units', 'flux')
        value, _, _, _, _ = self.results.get('extended_source_eff')
        self.assertAlmostEqual(0.690, value, 3)

    def test_confusion_limit(self):
        self.results.set('backend', 'GBT Spectrometer')
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        self.results.set('source_diameter_slider', 2)
        self.results.set('units', 'flux')
        value, _, _, _, _ = self.results.get('confusion_limit')
        self.assertAlmostEqual(60.819, value, 3)

        self.results.set('units', 'tr')
        value, _, _, _, _ = self.results.get('confusion_limit')
        self.assertAlmostEqual(173.663, value, 3)

        self.results.set('units', 'ta')
        value, _, _, _, _ = self.results.get('confusion_limit')
        self.assertAlmostEqual(119.792, value, 3)

    def test_airmass(self):
        def getResults(dec):
            self.results.set('declination', dec)
            self.results.set('min_elevation', dec2Els(dec)[0])
            min_el   = float(self.results.get('min_elevation')[0])
            max_el   = float(self.results.get('max_elevation')[0])
            air_mass = float(self.results.get('air_mass')[0])
            return min_el, max_el, air_mass

        min_el, max_el, air_mass = getResults(-20)
        self.assertAlmostEqual(min_el, 5, 2)
        self.assertAlmostEqual(max_el, 31.57, 2)
        self.assertAlmostEqual(air_mass, 4.03, 2)

        min_el, max_el, air_mass = getResults(20)
        self.assertAlmostEqual(min_el, 5, 2)
        self.assertAlmostEqual(max_el, 71.57, 2)
        self.assertAlmostEqual(air_mass, 2.41, 2)

        min_el, max_el, air_mass = getResults(38.43)
        self.assertAlmostEqual(min_el, 5, 2)
        self.assertAlmostEqual(max_el, 90, 2)
        self.assertAlmostEqual(air_mass, 2.11, 2)

        min_el, max_el, air_mass = getResults(50)
        self.assertAlmostEqual(min_el, 5, 2)
        self.assertAlmostEqual(max_el, 78.43, 2)
        self.assertAlmostEqual(air_mass, 2.28, 2)

        min_el, max_el, air_mass = getResults(60)
        self.assertAlmostEqual(min_el, 8.43, 2)
        self.assertAlmostEqual(max_el, 68.43, 2)
        self.assertAlmostEqual(air_mass, 2.12, 2)

        min_el, max_el, air_mass = getResults(85)
        self.assertAlmostEqual(min_el, 33.43, 2)
        self.assertAlmostEqual(max_el, 43.43, 2)
        self.assertAlmostEqual(air_mass, 1.62, 2)

    def test_est0(self):
        self.results.set('backend', 'GBT Spectrometer')
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        value = self.results.get('est0')[0]
        self.assertTrue(value is not None)

        est0 = float(value)
        self.assertAlmostEqual(est0, 16.634, 3)

    def test_attenuation(self):
        self.results.set('backend', 'GBT Spectrometer')
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        value = self.results.get('attenuation')[0]
        self.assertTrue(value is not None)

        attenuation = float(value)
        self.assertAlmostEqual(attenuation, 1.015, 3)

    def test_estTS(self):
        self.results.set('backend', 'GBT Spectrometer')
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        self.results.set('right_ascension', 0.0)
        self.results.set('galactic', 'no_correction')
        self.results.set('estimated_continuum', 3)
        value = self.results.get('est_ts')[0]
        self.assertTrue(value is not None)

        est_ts = float(value)
        self.assertAlmostEqual(est_ts, 19.852, 3)

    def test_t_sys(self):
        self.results.set('backend', 'GBT Spectrometer')
        self.results.set('declination', 38.43)
        self.results.set('min_elevation', 5)
        self.results.set('right_ascension', 0.0)
        self.results.set('galactic', 'no_correction')
        self.results.set('estimated_continuum', 3)
        value = self.results.get('t_sys')[0]
        self.assertTrue(value is not None)

        t_sys = float(value)
        self.assertAlmostEqual(t_sys, 19.558, 3)

