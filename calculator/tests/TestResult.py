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

from CalculatorTestCase          import CalculatorTestCase
from calculator.utilities.Result import Result

class TestResult(CalculatorTestCase):

    def setUp(self):
        super(TestResult, self).setUp()
        self.results = Result('equations')

    def tearDown(self):
        self.results.__del__()
        super(TestResult, self).tearDown()

    def testGet(self):
        self.assertEquals(5, self.results.get('size')[0])
        self.assertEquals('meters', self.results.get('size')[1])
        self.assertEquals(15, self.results.get('sensitivity')[0])
        self.assertEquals(75, self.results.get('time')[0])
        self.assertEquals('sec', self.results.get('time')[1])
        self.assertEquals(95, self.results.get('airmass')[0])

        self.results.set('size', None)
        self.assertEquals(5, self.results.get('size')[0])
        self.assertEquals(None, self.results.get('sensitivity')[0])
        self.assertEquals(None, self.results.get('time')[0])
        self.assertEquals(None, self.results.get('airmass')[0])

        self.results.set('size', 1)
        self.assertEquals(1, self.results.get('size')[0])
        self.assertEquals(3, self.results.get('sensitivity')[0])
        self.assertEquals(3, self.results.get('time')[0])
        self.assertEquals(7, self.results.get('airmass')[0])

    def test_two_dependent_variables(self):
        self.addTerm("x = ")
        self.addTerm("y = 3 * x + 1", "y = Newtons")

        r        = Result('equations')
        results  = r.get()
        self.assertEqual(results['x'], (None, None, '', 'x', None))
        self.assertEqual(results['y'], (None, 'Newtons', '3 * x + 1', 'y', None))
        self.assertEqual(results['foo'], (None, None, "size + time + bar", 'foo', None))

        r.set('bar', 2)
        r.set('x', 5)
        results  = r.get()
        self.assertEqual(results['foo'], (82, None, "size + time + bar", 'foo', None))
        self.assertEqual(results['x'], (5, None, '', 'x', None))
        self.assertEqual(results['y'], (16, 'Newtons', '3 * x + 1', 'y', None))

        r.__del__()


if __name__== "__main__":
    import unittest
    unittest.main()
