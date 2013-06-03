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

#import unittest
from django.test import TestCase

from pht.models import *

class TestPressureWeight(TestCase):

    def test_LoadWeights(self):
        self.rfiWeights     = [0.54246575342465753
                             , 0.54520547945205478
                             , 0.54520547945205478
                             , 0.54246575342465753
                             , 0.54246575342465753
                             , 0.54246575342465753
                             , 0.50136986301369868
                             , 0.50136986301369868
                             , 0.50136986301369868
                             , 0.48493150684931507
                             , 0.46027397260273972
                             , 0.45753424657534247
                             , 0.46027397260273972
                             , 0.46027397260273972
                             , 0.46027397260273972
                             , 0.46027397260273972
                             , 0.45753424657534247
                             , 0.46301369863013697
                             , 0.50136986301369868
                             , 0.50136986301369868
                             , 0.49863013698630138
                             , 0.51780821917808217
                             , 0.54246575342465753
                             , 0.54246575342465753
                             ] 
        sem, cat  = '12B', 'RFI'
        PressureWeight.LoadWeights(sem, cat, self.rfiWeights)
        expected = PressureWeight.GetWeights(sem, cat)
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], self.rfiWeights[i], 5)
