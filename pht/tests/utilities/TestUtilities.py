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

from pht.utilities import *

class TestUtilities(unittest.TestCase):

    def test_angularDistance(self):

        # common sense
        d = angularDistance(0.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(0.0, d, 3)
        d = angularDistance(0.0, 0.0, 0.0, math.pi/2.0)
        self.assertAlmostEqual(math.pi/2.0, d, 3)

        # from Practical Astronomy w/ Your Calculator, page 53
        ra1  = hr2rad(5.225)
        dec1 = deg2rad(-8.225)
        ra2  = hr2rad(6.737)         
        dec2 = deg2rad(-16.686)        
        d = angularDistance(ra1, dec1, ra2, dec2)
        self.assertAlmostEqual(0.41328374, d, 3)

        # from Ron:
        ra1  = deg2rad(15.*11.35)
        dec1 = deg2rad(4.18)
        ra2  = deg2rad(15.*12.)
        dec2 = deg2rad(0.26)
        d = angularDistance(ra1, dec1, ra2, dec2)
        self.assertAlmostEqual(0.18325, d, 3)

        ra1  = deg2rad(15.*11.41)
        dec1 = deg2rad(3.83)
        ra2  = deg2rad(15.*12.)
        dec2 = deg2rad(15.)
        d = angularDistance(ra1, dec1, ra2, dec2)
        self.assertAlmostEqual(0.24727, d, 3)

    def test_genDateTimesFromDays(self):

        days = [1,3,5]
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 3)
             , datetime(2011, 1, 5)
              ]
        start = exp[0]      
        dts = genDateTimesFromDays(start, days)

        self.assertEqual(exp, dts)

    def test_genDateTimesFromDaySeparations(self):

        days = [1,3,5]
        exp = [datetime(2011, 1, 1)
             , datetime(2011, 1, 4)
             , datetime(2011, 1, 9)
              ]
        start = exp[0]      
        dts = genDateTimesFromDaySeparations(start, days)

        self.assertEqual(exp, dts)

    def test_extDatetime2Datetime(self):

        dt = "01/01/2011"
        time = "00:00"
        exp = datetime(2011, 1, 1)
        r = extDatetime2Datetime(dt, time)
        self.assertEqual(exp, r)

        dt = "12/24/2011"
        time = "01:15"
        exp = datetime(2011, 12, 24, 1, 15)
        r = extDatetime2Datetime(dt, time)
        self.assertEqual(exp, r)

    def test_sex2flt_identity(self):

        # the functions sexigesimel2float and float2sexigesimel
        # should produce identity
        xs = ['00:00:00.0'
            , '00:00:00.1'
            , '00:00:00.9'
            , '00:30:30.0'
            , '01:30:30.2'
            , '23:59:59.5'
            , '89:00:59.8'
            , '-00:30:30.0'
            , '-01:30:30.2'
            , '-23:59:59.5'
            , '-89:00:59.8'
             ]
        for x in xs:
            self.assertEquals(x, float2sexigesimel(sexigesimel2float(x)))
            self.assertEquals(x, rad2sexHrs(sexHrs2rad(x)))
            self.assertEquals(x, rad2sexDeg(sexDeg2rad(x)))

    def test_sexigesimel2float(self):
        self.assertEquals('' , sexigesimel2float(''))
        self.assertEquals(2.0, sexigesimel2float('2.0'))
        self.assertEquals(0.0, sexigesimel2float('0:00'))
        self.assertEquals(0.0, sexigesimel2float('0:00:00'))
        self.assertEquals(1.0, sexigesimel2float('1:00:00'))
        self.assertEquals(-1.0, sexigesimel2float('-1:00:00'))
        self.assertEquals(1.5, sexigesimel2float('1:30:00'))
        self.assertAlmostEquals(1.50833, sexigesimel2float('1:30:30'), 5)
        self.assertAlmostEquals(23.9997, sexigesimel2float('23:59:59'), 2)
        self.assertAlmostEquals(-12.0, sexigesimel2float('-12:00:00'), 5)

    def test_sexigesimelFormTwo2float(self):
        self.assertEquals('' , sexigesimelFormTwo2float(''))
        self.assertEquals(2.0, sexigesimelFormTwo2float('2.0'))
        self.assertEquals(0.0, sexigesimelFormTwo2float('0 00'))
        self.assertEquals(0.0, sexigesimelFormTwo2float('0 00 00'))
        self.assertEquals(1.0, sexigesimelFormTwo2float('1 00 00'))
        self.assertEquals(1.0, sexigesimelFormTwo2float('1 00   00'))
        self.assertEquals(-1.0, sexigesimelFormTwo2float('-1 00 00'))
        self.assertEquals(1.5, sexigesimelFormTwo2float('1 30 00'))
        self.assertAlmostEquals(1.50833, sexigesimelFormTwo2float('1 30 30'), 5)
        self.assertAlmostEquals(23.9997, sexigesimelFormTwo2float('23 59 59'), 2)

    def test_sexigesimelFormThree2float(self):
        self.assertEquals('' , sexigesimelFormThree2float(''))
        self.assertEquals(-1.0, sexigesimelFormThree2float('-1d00m00s'))
        self.assertEquals(1.5, sexigesimelFormThree2float('1d30m00s'))
        self.assertAlmostEquals(1.50833, sexigesimelFormThree2float('1d30m30s'), 5)
        self.assertAlmostEquals(23.9997, sexigesimelFormThree2float('23d59m59s'), 2)

    def test_float2sexigesimel(self):
        self.assertEquals('00:00:00.0',float2sexigesimel(0.0))
        self.assertEquals('12:30:00.0',float2sexigesimel(12.5))
        self.assertEquals('-12:30:00.0',float2sexigesimel(-12.5))
        self.assertEquals('01:30:00.0', float2sexigesimel(1.5))
        self.assertEquals('01:30:30.0', float2sexigesimel(1.508333))
        self.assertEquals('23:58:58.8', float2sexigesimel(23.983))

    def test_sex2flt(self):
        self.assertAlmostEquals(0.0,         sexHrs2rad('00:00:00.0'), 2)
        self.assertAlmostEquals(math.pi/2.0, sexHrs2rad('06:00:00.0'), 2)
        self.assertAlmostEquals(2.0*math.pi, sexHrs2rad('23:59:59.9'), 2)
        self.assertAlmostEquals(0.0,         sexDeg2rad('00:00:00.0'), 2)
        self.assertAlmostEquals(math.pi/2.0, sexDeg2rad('90:00:00.0'), 2)
        self.assertAlmostEquals(2.0*math.pi, sexDeg2rad('359:59:59.9'), 2)

    def test_conversions(self):

        # test identity - use a range of degrees
        xs = range(0, 364)
        for x in xs:
            self.assertAlmostEquals(x, rad2deg(deg2rad(x)), 5)
            self.assertAlmostEquals(x
                , rad2deg(hr2rad(rad2hr(deg2rad(x)))), 5)
            self.assertAlmostEquals(x
                , arcMin2deg(deg2arcMin(x)), 5)
            self.assertAlmostEquals(x
                , rad2deg(arcMin2rad(rad2arcMin(deg2rad(x)))), 5)

