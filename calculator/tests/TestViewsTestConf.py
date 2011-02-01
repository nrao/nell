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
        response = c.get('/calculator/get_results')
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertTrue({'units': 'Newtons', 'term': 'y', 'value': 2} in results['results'])
        self.assertTrue({'units': None, 'term': 'x', 'value': 1} in results['results'])
        xsys     = [r for r in results['results'] if 'x' in r.values() or 'y' in r.values()]
        self.assertEqual(len(xsys), 2)
        self.failUnlessEqual(response.status_code, 200)

        self.resetTerms()

        #  Make sure the add terms are really gone.
        response = c.post('/calculator/set_terms/', {})
        response = c.get('/calculator/get_results')
        content  = response.content.replace("null", "None")
        results  = eval(content)
        xsys     = [r for r in results['results'] if 'x' in r.values() or 'y' in r.values()]
        self.assertEqual(len(xsys), 0)
        self.failUnlessEqual(response.status_code, 200)

    def test_one_dependent_variable(self):
        c = Client()
        response = c.get('/calculator/initiate_hardware')
        response = c.post('/calculator/set_terms/', {})
        response = c.get('/calculator/get_results')
        results  = eval(response.content.replace("null", "None"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue({'units': None, 'term': 'foo', 'value': None} in results['results'])

        response = c.post('/calculator/set_terms/', {'bar' : 2})
        response = c.get('/calculator/get_results')
        results  = eval(response.content.replace("null", "None"))
        self.assertTrue({'units': None, 'term': 'foo', 'value': 82} in results['results'])

    def test_two_dependent_variables(self):
        self.addTerm("x = ")
        self.addTerm("y = 3 * x + 1", "y = Newtons")

        c = Client()
        response = c.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = c.post('/calculator/set_terms/', {})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))
        self.assertTrue({'units': 'Newtons', 'term': 'y', 'value': None} in results['results'])
        self.assertTrue({'units': None, 'term': 'x', 'value': None} in results['results'])
        self.assertTrue({'units': None, 'term': 'foo', 'value': None} in results['results'])

        response = c.post('/calculator/set_terms/', {'bar' : 2, 'x' : 5})
        response = c.get('/calculator/get_results')
        results  = eval(response.content.replace("null", "None"))
        self.assertTrue({'units': 'Newtons', 'term': 'y', 'value': 16.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'x', 'value': 5.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'foo', 'value': 82.0} in results['results'])

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
        response = c.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertTrue({'units': None, 'term': 'x', 'value': None} in results['results'])
        self.assertTrue({'units': 'Newtons', 'term': 'y', 'value': None} in results['results'])
        self.assertTrue({'units': None, 'term': 'foo', 'value': None} in results['results'])

        response = c.post('/calculator/set_terms/', {'bar' : 2, 'x' : 5, 'q' : 1})
        response = c.get('/calculator/get_results')
        content  = response.content.replace("null", "None")
        results  = eval(content)
        self.assertTrue({'units': None, 'term': 'foo', 'value': 82.0} in results['results'])
        self.assertTrue({'units': 'Newtons', 'term': 'y', 'value': 16.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'x', 'value': 5.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'theta', 'value': 55.094395102393193})
        
    def test_shared_dependencies(self):
        self.addTerm("a = c * 2 + d")
        self.addTerm("b = c * 3 + d")
        self.addTerm("c = ")
        self.addTerm("d = ")

        c = Client()
        response = c.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = c.post('/calculator/set_terms/', {'c' : 2, 'd' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))
        self.assertTrue({'units': None, 'term': 'a', 'value': 5.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'b', 'value': 7.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'c', 'value': 2.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'd', 'value': 1.0} in results['results'])

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
        response = c.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))
        response = c.post('/calculator/set_terms/', {'c' : 1, 'd' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = c.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results  = eval(response.content.replace("null", "None"))

        self.assertTrue({'units': None, 'term': 'a', 'value': 1.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'b', 'value': 1.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'c', 'value': 1.0} in results['results'])
        self.assertTrue({'units': None, 'term': 'd', 'value': 1.0} in results['results'])
