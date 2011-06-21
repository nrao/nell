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

from django.test.client  import Client
from CalculatorTestCase  import CalculatorTestCase, equations
import settings

class TestViewsTestConf(CalculatorTestCase):

    def get_data(self, response):
        content  = response.content.replace("null", "None")
        results  = eval(content)
        values = dict([(r['term'], r['value']) for r in results['results']])
        inputs = dict([(i['term'], i['value']) for i in results['input']])
        return inputs, values

    def test_modify_terms(self):
        """
        Just testing added functionality to modify terms in the config file.
        """
        self.addTerm("x = 1")
        self.addTerm("y = x + 1", "y = Newtons")

        #  Make sure the new terms are loaded.
        response = self.client.get('/calculator/initiate_hardware')
        response = self.client.post('/calculator/set_terms/', {})
        response = self.client.get('/calculator/get_results')

        inputs, values = self.get_data(response)
        self.assertEqual(values['y'], 2)
        self.assertEqual(values['x'], 1)

        xsys     = [k for k, _ in values.items() if k in ('x', 'y')]
        self.assertEqual(len(xsys), 2)
        self.failUnlessEqual(response.status_code, 200)

        self.resetTerms()

        #  Make sure the add terms are really gone.
        response = self.client.post('/calculator/set_terms/', {})
        response = self.client.get('/calculator/get_results')

        inputs, values = self.get_data(response)
        xsys     = [k for k, _ in values.items() if k in ('x', 'y')]
        self.assertEqual(len(xsys), 0)
        self.failUnlessEqual(response.status_code, 200)

    def test_one_dependent_variable(self):
        response = self.client.get('/calculator/initiate_hardware')
        response = self.client.post('/calculator/set_terms/', {})
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)

        inputs, values = self.get_data(response)
        self.assertEqual(values['foo'], None)

        response = self.client.post('/calculator/set_terms/', {'bar' : 2})
        response = self.client.get('/calculator/get_results')

        inputs, values = self.get_data(response)
        self.assertEqual(values['foo'], 82)

    def test_two_dependent_variables(self):
        self.addTerm("x = ")
        self.addTerm("y = 3 * x + 1", "y = Newtons")

        response = self.client.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/calculator/set_terms/', {})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)

        inputs, values = self.get_data(response)
        self.assertEqual(inputs['x'], None)
        self.assertEqual(values['y'], None)
        self.assertEqual(values['foo'], None)

        response = self.client.post('/calculator/set_terms/', {'bar' : 2, 'x' : 5})
        response = self.client.get('/calculator/get_results')

        inputs, values = self.get_data(response)
        self.assertEqual(inputs['x'], 5.0)
        self.assertEqual(values['y'], 16.0)
        self.assertEqual(values['foo'], 82.0)

    def test_many_dependents(self):
        self.addTerm("x = ")
        self.addTerm("y = 3 * x + 1", "y = Newtons")
        self.addTerm("z = math.pow(y, 4) + (r * x) + 42")
        self.addTerm("theta = 2 * math.pi / 3 + r")
        self.addTerm("r = 3 * y + x")

        response = self.client.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/calculator/set_terms/', {})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)

        inputs, values = self.get_data(response)
        self.assertEqual(inputs['x'], None)
        self.assertEqual(values['y'], None)
        self.assertEqual(values['foo'], None)

        response = self.client.post('/calculator/set_terms/', {'bar' : 2, 'x' : 5, 'q' : 1})
        response = self.client.get('/calculator/get_results')

        inputs, values = self.get_data(response)
        self.assertEqual(inputs['x'], 5.0)
        self.assertEqual(values['y'], 16.0)
        self.assertEqual(values['foo'], 82.0)
        self.assertEqual(values['theta'], 55.094395102393193)

    def test_shared_dependencies(self):
        self.addTerm("a = c * 2 + d")
        self.addTerm("b = c * 3 + d")
        self.addTerm("c = ")
        self.addTerm("d = ")

        response = self.client.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/calculator/set_terms/', {'c' : 2, 'd' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)

        inputs, values = self.get_data(response)
        self.assertEqual(values['a'], 5.0)
        self.assertEqual(values['b'], 7.0)
        self.assertEqual(inputs['c'], 2.0)
        self.assertEqual(inputs['d'], 1.0)

    def test_setting_different_groups(self):
        self.addTerm("a = ")
        self.addTerm("b = ")
        self.addTerm("c = ")
        self.addTerm("d = ")

        response = self.client.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/calculator/set_terms/', {'a' : 1, 'b' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/calculator/set_terms/', {'c' : 1, 'd' : 1})
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)

        inputs, values = self.get_data(response)
        self.assertEqual(inputs['a'], 1.0)
        self.assertEqual(inputs['b'], 1.0)
        self.assertEqual(inputs['c'], 1.0)
        self.assertEqual(inputs['d'], 1.0)
