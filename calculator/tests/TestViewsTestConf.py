from django.test.client  import Client
from CalculatorTestCase  import CalculatorTestCase, equations
import settings

class TestViewsTestConf(CalculatorTestCase):

    def test_modify_terms(self):
        """
        Just testing added functionality to modify terms in the config file.
        """
        self.addTerm("x = 1")
        self.addTerm("y = x + 1", "y = Newtons")

        #  Make sure the new terms are loaded.
        c = Client()
        response = c.get('/calculator/initiate_hardware')
        response = c.post('/calculator/set_terms/', {})
        response = c.get('/calculator/get_result/')
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertTrue('x' in results.keys() and 'y' in results.keys())
        self.assertEqual(results['x'], [1, None, '1'])
        self.assertEqual(results['y'], [2, 'Newtons', 'x + 1'])
        self.failUnlessEqual(response.status_code, 200)

        self.resetTerms()

        #  Make sure the add terms are really gone.
        response = c.post('/calculator/set_terms/', {})
        response = c.get('/calculator/get_result/')
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertTrue('x' not in results.keys() and 'y' not in results.keys())
        self.failUnlessEqual(response.status_code, 200)

    def test_one_dependent_variable(self):
        c = Client()
        response = c.get('/calculator/initiate_hardware')
        response = c.post('/calculator/set_terms/', {})
        response = c.get('/calculator/get_result/')
        results  = eval(response.content.replace("null", "None"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(results['foo'], [None, None, "size + time + bar"])

        response = c.post('/calculator/set_terms/', {'bar' : 2})
        response = c.get('/calculator/get_result/')
        results  = eval(response.content.replace("null", "None"))
        self.assertEqual(results['foo'], [82, None, "size + time + bar"])

    def test_two_dependent_variables(self):
        self.addTerm("x = ")
        self.addTerm("y = 3 * x + 1", "y = Newtons")

        c = Client()
        response = c.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = c.post('/calculator/set_terms/', {})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))
        self.assertEqual(results['x'], [None, None, ''])
        self.assertEqual(results['y'], [None, 'Newtons', '3 * x + 1'])
        self.assertEqual(results['foo'], [None, None, "size + time + bar"])

        response = c.post('/calculator/set_terms/', {'bar' : 2, 'x' : 5})
        response = c.get('/calculator/get_result/')
        results  = eval(response.content.replace("null", "None"))
        self.assertEqual(results['foo'], [82, None, "size + time + bar"])
        self.assertEqual(results['x'], [5, None, ''])
        self.assertEqual(results['y'], [16, 'Newtons', '3 * x + 1'])

    def test_many_dependents(self):
        self.addTerm("x = ")
        self.addTerm("y = 3 * x + 1", "y = Newtons")
        self.addTerm("z = math.pow(y, 4) + (r * x) + 42")
        self.addTerm("theta = 2 * math.pi / 3 + r")
        self.addTerm("r = 3 * y + x")

        c = Client()
        response = c.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = c.post('/calculator/set_terms/', {})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertEqual(results['x'], [None, None, ''])
        self.assertEqual(results['y'], [None, 'Newtons', '3 * x + 1'])
        self.assertEqual(results['foo'], [None, None, "size + time + bar"])

        response = c.post('/calculator/set_terms/', {'bar' : 2, 'x' : 5, 'q' : 1})
        response = c.get('/calculator/get_result/')
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertEqual(results['foo'], [82, None, "size + time + bar"])
        self.assertEqual(results['x'], [5, None, ''])
        self.assertEqual(results['y'], [16, 'Newtons', '3 * x + 1'])
        self.assertEqual(results['theta'], [55.094395102393193, None, '2 * math.pi / 3 + r'])
        
    def test_setting_different_groups(self):
        self.addTerm("a = ")
        self.addTerm("b = ")
        self.addTerm("c = ")
        self.addTerm("d = ")

        c = Client()
        response = c.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = c.post('/calculator/set_terms/', {'a' : 1, 'b' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))
        response = c.post('/calculator/set_terms/', {'c' : 1, 'd' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))
        self.assertEqual(results['a'], [1, None, ''])
        self.assertEqual(results['b'], [1, None, ''])
        self.assertEqual(results['c'], [1, None, ''])
        self.assertEqual(results['d'], [1, None, ''])

