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
import unittest
import math
from pht.utilities.Conversions import Conversions 

class TestConversions(unittest.TestCase):

    def setUp(self):
        self.c = Conversions()

    def test_tryHourConversions(self):

        # varaitions off HH:MM:SS.S
        tests = ['10:00:00.0'
               , '10:00:00.000'
               , '10:00:00'
               , '010:00:00'
               # varaitions off HH MM SS.S
               , '10 00 00.0'
               , '10 00     00.0'
               # varaitions off ##h ##m ##s
               , '10d00m00s'
               , '10h00m00s'
               , '10d 00m 00s'
               , '10d 00m 00.0s'
               # simple
               , '10.0'
                ]
        for t in tests:        
            anyMatch, value = self.c.tryHourConversions(t) 
            self.assertEqual(True, anyMatch)
            self.assertAlmostEquals(10.0, value, 2)
            
        # spot check    
        anyMatch, value = self.c.tryHourConversions('    09:43:25') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(9.723, value, 2)
        anyMatch, value = self.c.tryHourConversions('23:30:00') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(23.50, value, 2)
        anyMatch, value = self.c.tryHourConversions('123:30:00') 
        self.assertTrue(value is None)

    def test_tryDegreeConversions(self):

        # varaitions off HH:MM:SS.S
        tests = ['310:00:00.0'
               , '310:00:00.000'
               , '-310:00:00.000'
               , '310:00:00'
               , '0310:00:00'
               # varaitions off HH MM SS.S
               , '310 00 00.0'
               , '310 00     00.0'
               , '-310 00     00.0'
               # varaitions off ##h ##m ##s
               , '310d00m00s'
               , '310d00m00s'
               , '-310d00m00s'
               , '310d 00m 00s'
               , '310d 00m 00.0s'
               # simple
               , '310.0'
                ]
        for t in tests:        
            anyMatch, value = self.c.tryDegreeConversions(t) 
            self.assertEqual(True, anyMatch)
            self.assertAlmostEquals(310.0, abs(value), 2)
            
        # spot check    
        anyMatch, value = self.c.tryDegreeConversions('    09:43:25') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(9.723, value, 2)
        anyMatch, value = self.c.tryDegreeConversions('23:30:00') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(23.50, value, 2)
        anyMatch, value = self.c.tryDegreeConversions('523:30:00') 
        self.assertTrue(value is None)
        anyMatch, value = self.c.tryDegreeConversions('23 13 13') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(23.220, value, 2)
        anyMatch, value = self.c.tryDegreeConversions('+23 13 13') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(23.220, value, 2)
        anyMatch, value = self.c.tryDegreeConversions('-23 13 13') 
        self.assertEqual(True, anyMatch)
        self.assertAlmostEquals(-23.220, value, 2)

