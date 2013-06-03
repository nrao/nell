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

from calculator.utilities  import GBTResourceImport

import unittest

class TestGBTResourceImport(unittest.TestCase):

    def test_init(self):
        resources = GBTResourceImport("calculator/data/gbt_resources_table.txt", silent = True)
        for c in resources.configs:
            for k, vs in c.iteritems():
                for v in vs: 
                    self.assertNotEqual((k, None), (k, v))

    def test_processEnumeration(self):

        # first init our object w/ nothing
        empty = "calculator/data/empty_resources_table.txt"
        r = GBTResourceImport(empty, silent = True)

        enum = '"{1,2,3,4}"'
        exp = ['1', '2', '3', '4']
        self.assertEqual(exp, r.processEnumeration(enum))

        enum = '"{1:4}"'
        self.assertEqual(exp, r.processEnumeration(enum))

    def test_processRow(self):

        # first init our object w/ nothing
        empty = "calculator/data/empty_resources_table.txt"
        r = GBTResourceImport(empty, silent = True)

        # now hard code the raw data so we can test processRow method
        header = ['Backend',
                  'Mode',
                  'Receiver',
                  '# beams',
                  'Polarization',
                  'Bandwidth (MHz)',
                  'Number spectral windows',
                  'Min integ time',
                  'Switching mode',
                  'Additional Questions',
                  'Notes']
        data = ['VEGAS',
                'Spectral Line',
                '"{KFPA,U,Q,W1,W2,W3,W4}"',
                '1',
                '"{Dual, Full}"',
                '"{1250,850,187.5,100}"',
                '"{1,2,3,4}"',
                '0.100',
                '"{TP-PS, IFSW, OFSW}"',
                '',
                '']
        data2 = ['', ''] # make sure we can't handle any type of blanks       
        data3 = ['VEGAS',
                  'Spectral Line',
                  '"{B1,B2,B3}"',
                  '1',
                  'Single',
                  '"{1250,850,187.5,100}"',
                  '{1:8}', # this is new: ':', plus lack of dbl quotes
                  '0.100',
                  '"{TP-PS, IFSW, OFSW}"',
                  '',
                  '']

        r.raw_data = [header, data, data2, data3]

        # process this raw data
        r.processData()

        # now check it
        exp = {'Polarization': ['Dual', 'Full'], 'Number spectral windows': ['1', '2', '3', '4'], 'Min integ time': '0.100', 'Bandwidth (MHz)': ['1250', '850', '187.5', '100'], '# beams': '1', 'Switching mode': ['TP-PS', 'IFSW', 'OFSW'], 'Mode': 'Spectral Line', 'Receiver': ['KFPA', 'U', 'Q', 'W1', 'W2', 'W3', 'W4'], 'Backend': 'VEGAS'}
        exp2 = {'Polarization': 'Single', 'Number spectral windows': ['1', '2', '3', '4', '5', '6', '7', '8'], 'Min integ time': '0.100', 'Bandwidth (MHz)': ['1250', '850', '187.5', '100'], '# beams': '1', 'Switching mode': ['TP-PS', 'IFSW', 'OFSW'], 'Mode': 'Spectral Line', 'Receiver': ['B1', 'B2', 'B3'], 'Backend': 'VEGAS'}
        self.assertEqual(exp, r.data[0])
        self.assertEqual(exp2, r.data[1])

if __name__ == "__main__":
    unittest.main()
