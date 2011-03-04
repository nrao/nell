from calculator.utilities.Term import Term
import unittest

class TestTerm(unittest.TestCase):
    def setUp(self):
        self.term = Term('test', units = 'ohms')

    def testInit(self):
        self.assertTrue('test' in self.term.__str__())
        self.assertEquals((None, 'ohms', '', 'test', None), self.term.get())

        term = Term('stuff', 3)
        self.assertTrue('stuff' in term.__str__())
        self.assertEquals((3, None, '', 'stuff', None), term.get())

    def testAddObserver(self):
        self.assertEquals([], self.term.observers)
        self.term.addObserver('1')
        self.assertEquals(['1'], self.term.observers)

    def testGet(self):
        self.assertEquals((None, 'ohms', '', 'test', None), self.term.get())

        self.term.value = 'abc'
        self.assertEquals(('abc', 'ohms', '', 'test', None), self.term.get())

    def testSet(self):
        self.assertEquals((None, 'ohms', '', 'test', None), self.term.get())

        self.term.set('abc')
        self.assertEquals(('abc', 'ohms', '', 'test', None), self.term.get())

        self.term.set(None)
        self.assertEquals((None, 'ohms', '', 'test', None), self.term.get())

    def testEvaluate(self):
        term1 = Term('a', 1)
        term2 = Term('b', 2)

        term = Term('test', equation = 'a + b', units = 'parsecs')
        self.assertEquals('a + b', term.equation)
        term.evaluate(term1)
        term.evaluate(term2)
        self.assertEquals((3, 'parsecs', 'a + b', 'test', None), term.get())

        term = Term('test', equation = 'a * b', units = 'parsecs')
        self.assertEquals('a * b', term.equation)
        term.evaluate(term1)
        term.evaluate(term2)
        self.assertEquals((2, 'parsecs', 'a * b', 'test', None), term.get())

        term = Term('test', equation = 'a - b', units = 'parsecs')
        self.assertEquals('a - b', term.equation)
        term.evaluate(term1)
        term.evaluate(term2)
        self.assertEquals((-1, 'parsecs', 'a - b', 'test', None), term.get())

        term = Term('test', equation = 'a / b', units = 'parsecs')
        self.assertEquals('a / b', term.equation)
        term.evaluate(term1)
        term.evaluate(term2)
        self.assertEquals((1/2, 'parsecs', 'a / b', 'test', None), term.get())

    def testReEvaluate(self):
        term1 = Term('a', 1)
        term2 = Term('b', 2)

        term = Term('test', equation = 'a + b', units = 'parsecs')
        self.assertEquals('a + b', term.equation)
        term.evaluate(term1)
        term.evaluate(term2)
        self.assertEquals((3, 'parsecs', 'a + b', 'test', None), term.get())

        #  Now change a term and see if the dependent gets reevaluated
        term1.set(2)
        term.evaluate(term1)
        self.assertEquals((4, 'parsecs', 'a + b', 'test', None), term.get())

if __name__== "__main__":
    unittest.main()
