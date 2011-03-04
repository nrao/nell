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
