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

from django.test import TestCase

from calculator.utilities.functions import *

class TestFunctions(TestCase):

    def assertMinTopoFreq(self, backend, bandwidths, windows, receiver, beams, exp):
        i = 0
        for bw in bandwidths:
           for w in windows:
              for b in beams:
                  f = getMinTopoFreq(backend, bw, w, receiver, b)
                  self.assertAlmostEquals(exp[i], f, 6)
                  #print "bw = %.2f, w = %d, b = %d, f = %5.3f" % (bw, w, b, f)
                  i += 1

    def test_getMinTopoFreq(self):

        # GBT Spectrometer tests
        backend = 'GBT Spectrometer'

        # L band
        receiver = 'L (1.15 - 1.73 GHz)'
        bandwidths = [12.5, 50, 200, 800]
        windows = [1, 2, 4, 8] 
        beams = [1.0]
        exp = [0.095367431640625, 0.19073486328125, 0.3814697265625, 0.762939453125, 0.3814697265625, 0.762939453125, 1.52587890625, 3.0517578125, 6.103515625, 12.20703125, 24.4140625, 48.828125, 97.65625, 195.3125, 390.625, 781.25]
        self.assertMinTopoFreq(backend, bandwidths, windows, receiver, beams, exp)

        # PF1
        receiver = 'PF1 (0.29 - 0.395 GHz)'
        beams = [1, 2]
        exp = [0.095367431640625, 0.19073486328125, 0.19073486328125, 0.3814697265625, 0.3814697265625, 0.762939453125, 0.762939453125, 1.52587890625, 0.3814697265625, 0.762939453125, 0.762939453125, 1.52587890625, 1.52587890625, 3.0517578125, 3.0517578125, 6.103515625, 6.103515625, 12.20703125, 12.20703125, 24.4140625, 24.4140625, 48.828125, 48.828125, 97.65625, 97.65625, 195.3125, 195.3125, 390.625, 390.625, 781.25, 781.25, 1562.5]
        self.assertMinTopoFreq(backend, bandwidths, windows, receiver, beams, exp)

        # test backends w/ out known resolution:
        f = getMinTopoFreq('Mustang 1.5', None, None, None, None)
        self.assertEqual(1, f)

        # the vegas stuff shouldn't work, because the DB lookup now don't work.
        backend = 'VErsitile GB Astronomical Spectrometer'
        bandwidths = [11.72, 23.44, 100, 187.5, 850, 1250]
        windows = range(1, 9)
        #print "VEGAS & PF1"
        #self.assertMinTopoFreq(backend, bandwidths, windows, receiver, beams, [])


    def test_getTimeVisible(self):

        # Check against Ron's results for this min. elevation
        minEl = 10.0
        decs1 = range(-90, -41)
        for d in decs1:
            self.assertEqual(0.0, getTimeVisible(d, minEl))

        decs2 = range(-41, -37)
        exp1 = [1.3883594994
              , 2.29455878167
              , 2.92003968103
              ,3.42296389013
               ]
        for d, exp in zip(decs2, exp1):
            self.assertAlmostEqual(exp, getTimeVisible(d, minEl), 3)        
        decs3 = range(58, 62)
        exp1 = [19.7846602664
              , 20.3872020526
              , 21.1471354295
              , 22.2649133951
               ]
        for d, exp in zip(decs3, exp1):
            self.assertAlmostEqual(exp, getTimeVisible(d, minEl), 3)        
        decs4 = range(62, 90)
        for d in decs4:
            self.assertEqual(24.0, getTimeVisible(d, minEl))

        # and for this min. elevation
        minEl = 45.0
        decs1 = range(-90, -6)
        for d in decs1:
            self.assertEqual(0.0, getTimeVisible(d, minEl))

        decs2 = range(-6, 2)
        exp1 = [
             1.02209227744
          ,  1.69242662209
          ,  2.15760990169
          ,  2.53345067507
          ,  2.85557861975
          ,  3.14067869313
          ,  3.39818344892
          ,  3.63405281888      
               ]

        for d, exp in zip(decs2, exp1):
            self.assertAlmostEqual(exp, getTimeVisible(d, minEl), 3)        
        decs3 = range(80, 84)
        exp1 = [ 
             6.09735485686
          ,  5.4019871385
          ,  4.38386884241
          ,  2.56344352291
               ]
        for d, exp in zip(decs3, exp1):
            self.assertAlmostEqual(exp, getTimeVisible(d, minEl), 2)        
        decs4 = range(84, 90)
        for d in decs4:
            self.assertEqual(0.0, getTimeVisible(d, minEl))

        #for dec in range(-90, 90):
        #    t = getTimeVisible(dec, 10.0)
            #print dec, t

        
    def test_sourceSizeCorrection(self):
        correction = sourceSizeCorrectionS(6, 8)
        self.assertAlmostEqual(correction, 0.828, 3)

    def test_getKs(self):
        k1, k2 = getKs('Spectral Processor', 1, 1, 1, 1, 1)  #  bandwidth, bw, windows, and beams not used
        self.assertEqual(k1, 1.3)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 200, 1, 1, 1, 1)  #  bw, windows, and beams not used
        self.assertEqual(k1, 1.235)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 800, 1, 1, 1, 1)  #  bw, windows, and beams not used
        self.assertEqual(k1, 1.235)
        self.assertEqual(k2, 1.21)

        
        k1, k2 = getKs('GBT Spectrometer', 50, 8, 8, 1, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 50, 1, 8, 1, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 12.5, 8, 8, 1, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

        k1, k2 = getKs('GBT Spectrometer', 12.5, 1, 8, 1, 1)
        self.assertEqual(k1, 1.032)
        self.assertEqual(k2, 1.21)

    def test_dec2Els(self):
        min_el, max_el = dec2Els(-20)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(31.57, max_el, 2)

        min_el, max_el = dec2Els(20)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(71.57, max_el, 2)

        min_el, max_el = dec2Els(38.43)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(90, max_el, 2)

        min_el, max_el = dec2Els(50)
        self.assertEqual(5, min_el)
        self.assertAlmostEqual(78.43, max_el, 2)

        min_el, max_el = dec2Els(60)
        self.assertAlmostEqual(8.43, min_el, 2)
        self.assertAlmostEqual(68.43, max_el, 2)

        min_el, max_el = dec2Els(85)
        self.assertAlmostEqual(33.43, min_el, 2)
        self.assertAlmostEqual(43.43, max_el, 2)

    def test_calculateEST0(self):
        for wv in WeatherValues.objects.all():
            r = calculateEST0(wv.frequency * 1000, 1)
            if wv.frequency < 85 and wv.frequency > 93:
                self.assertAlmostEqual(r, wv.est0, 1)

        for wv_must in WeatherValues.objects.exclude(t_rcvr_mustang = None):
            r = calculateEST0(wv_must.frequency * 1000, 1, 'Mustang')
            self.assertAlmostEqual(r, wv_must.est0_mustang, 1)

    def test_calculateAttenuation(self):
        attenuation = calculateAttenuation(2.11, 1420)
        self.assertAlmostEqual(attenuation, 0.961, 3)

    def test_getAppEff(self):
        appEff = getAppEff(0.3, 30, 90, 0.7)
        self.assertAlmostEqual(appEff, 0.2535, 4)

    def test_calculateEtaMin(self):

        inputsOutputs = [
            (1000, 0.951806870543)
          , (6000, 0.922116375739)
          , (11000, 0.824282996949)
          , (16000, 0.665969680288)
          , (21000, 0.533952791312)
          , (26000, 0.508899792477)
          , (31000, 0.575382941633)
          , (36000, 0.652488595023)
          , (41000, 0.676595219781)
          , (46000, 0.631849984379)
          , (51000, 0.549159696647)
          , (56000, 0.504091450641)
        ]
        for f in range(61, 91, 5):
            inputsOutputs.append((f*1000, 0.43))
        for i, o in inputsOutputs:
            self.assertAlmostEquals(o, calculateEtaMin(i), 6)

    def test_getSuggestedMinElevation(self):

        freqs = [5000, 10000, 20000, 90000] # MHz
        decs = [-40., -30., -20., -0., 20., 40., 60., 70. ] # degrees
        inputs = [(f, d) for f in freqs for d in decs]
        exp = [8.0
          , 13.0
          , 16.0
          , 21.0
          , 23.0
          , 24.0
          , 22.4333333333
          , 21.4333333333
          , 8.0
          , 12.0
          , 15.0
          , 19.0
          , 21.0
          , 21.0
          , 20.4333333333
          , 19.4333333333
          , 7.0
          , 11.0
          , 13.0
          , 16.0
          , 18.0
          , 18.0
          , 17.4333333333
          , 18.4333333333
          , 7.0
          , 11.0
          , 13.0
          , 15.0
          , 17.0
          , 17.0
          , 16.4333333333
          , 18.4333333333                
            ]

        for input, output in zip(inputs, exp):
            f, d = input
            self.assertAlmostEqual(output, getSuggestedMinElevation(f, d))
  
