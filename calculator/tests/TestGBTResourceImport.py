from calculator.utilities  import GBTResourceImport

import unittest

class TestGBTResourceImport(unittest.TestCase):

    def test_init(self):
        resources = GBTResourceImport("calculator/gbt_resources_table.txt", silent = True)
        for c in resources.configs:
            for k, vs in c.iteritems():
                for v in vs: 
                    self.assertNotEqual((k, None), (k, v))

if __name__ == "__main__":
    unittest.main()
