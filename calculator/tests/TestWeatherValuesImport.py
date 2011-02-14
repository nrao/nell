import unittest
from calculator.utilities  import WeatherValuesImport

class TestWeatherValuesImport(unittest.TestCase):

    def test_import(self):
        wvi = WeatherValuesImport('calculator/utilities/SensCalcWeatherValues.csv')
