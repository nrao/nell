from django.test import TestCase

from calculator.utilities.functions import *

class TestCalcTsky(TestCase):
    fixtures = ['tsky_data.json']

    def test_calcTsky(self):
        t = calcTsky(0, 0, 1420, 'model')
        self.assertAlmostEqual(t, 0.6992, 4)
        t = calcTsky(60, 70, 1420, 'model')
        self.assertAlmostEqual(t, 0.8164, 4)
        
