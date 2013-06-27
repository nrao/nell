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

from calculator.models import FrequencyResolution, WeatherValues, TSky

import math
from pyslalib import slalib

from utilities.TimeAgent import *

freqRes = {800  : 8192
         , 200  : 32768
         , 50   : 131072
         , 12.5 : 131072
          }

spectrometerK1K2  = {800  : (1.235, 1.21)
                   , 200  : (1.235, 1.21)
                   , 50   : [(1.235, 1.21), (1.032, 1.21)]
                   , 12.5 : [(1.235, 1.21), (1.032, 1.21)]
                    }

vegasTopoFreq = { 100   : 0.000763
                , 187.5 : 0.001431
                , 850   : 0.061
                , 1250  : 0.088
                }

GBT_LAT = 38 + 26 / 60.
LAT     = 51.57
backendsWithKnownRes = ('Spectral Processor', 'GBT Spectrometer') #, 'VErsitile GB Astronomical Spectrometer')

def getMinTopoFreq(backend, bandwidth, windows, receiver, beams):
    if backend in backendsWithKnownRes:
        qBandwidth = None if backend == 'Spectral Processor' else bandwidth
        fr         = FrequencyResolution.objects.filter(backend__dss_backend__name = backend
                                                      , bandwidth = qBandwidth)
        #if backend == 'VErsitile GB Astronomical Spectrometer' and windows in (8, 16):
        #    fr = fr.filter(windows__name = int(windows))
        if len(fr) == 0:
            return 1 # DB lookup failed!
        channels = fr[0].max_number_channels

        # Note: KFPA is a 7 beam rx, but we want to use 8 beams for calculations.
        beams = 8 if receiver == 'KFPA' and beams == 7 else beams
        return (bandwidth / float(channels)) * windows  * beams * 1000 if channels is not None else 0.0

    elif backend == 'VErsitile GB Astronomical Spectrometer':
        if bandwidth == 23.44:
            mhz =  0.000045 if int(windows) <= 8 else 0.000357
        elif bandwidth == 11.72:
            mhz = 0.000022 if int(windows) <= 8 else 0.000179
        else:
            mhz = vegasTopoFreq.get(bandwidth, None)
        return mhz * 1e3

    else:
        return 1 # things like pulsar backends

def dec2Els(dec):
    "Returns the (min, max) elevation for the given declination (degrees)"
    if dec <= GBT_LAT:
        return 5, 90 - GBT_LAT + dec
    elif dec < 90 - GBT_LAT:
        return 5, 90 + GBT_LAT - dec
    else:
        return GBT_LAT - 90 + dec, 90 - dec + GBT_LAT

def getMinElevation(dec):
    return dec2Els(dec)[0]

def getMaxElevation(dec):
    return dec2Els(dec)[1]


def getSuggestedMinElevation(freq, dec, backend = None):
    sqrtEtaHAMin = math.sqrt(math.sqrt(0.5*calculateEtaMin(freq)))
    (minElev, maxElev) = dec2Els(dec)
    EST0Transit = calculateEST0(freq,1./math.sin(math.radians(maxElev)),backend)
    el = minElev
    while el < maxElev and \
        EST0Transit/calculateEST0(freq,1./math.sin(math.radians(el)),backend) < sqrtEtaHAMin:
        el = el + 1.
    return el

def calculateEtaMin(freq):
    # Equations 22 and 22a
    if freq <= 60000:
        relF = freq/1000./12.8
        eta_avrg = 0.74+0.155*math.cos(relF) + 0.120*math.cos(2*relF) - 0.030*math.cos(3*relF) - 0.010*math.cos(4*relF)
    else:
        eta_avrg = 0.5
    # Equation 23 (rearranged)
    return 1.1*eta_avrg - 0.12

def getAppEff(wavelength, min_elevation, max_elevation, eta_long):
    if wavelength > 3:
        return eta_long
    integrand1, integrand2 = 0, 0
    min_elevation, max_elevation = map(int, (min_elevation, max_elevation))
    for e in range(min_elevation, max_elevation + 1):
        weight = 90 - e
        integrand1 = integrand1 + weight * math.exp(-1 * math.pow(
            0.00125664 * (500.954 - 10.4728 * e + 0.09766 * e * e) / wavelength, 2))
        integrand2 = integrand2 + weight
    # Should return 0.253494449914 when lambda = 0.3, e1 = 30, e2 = 90, n0
    # = 0.70
    return eta_long * integrand1 / float(integrand2)

def sourceSizeCorrectionS(diameter, fwhm):
    x          = diameter / (1.2 * fwhm)
    if x < 0.1:
        return 1.0
    # Here's a model that fits the theoretical beam shape better than 
    # math.pow(x,2)/(1 - math.exp(-1 * math.pow(x, 2)))
    # and works well to the 1st null.  Only good for Te = 13 dB
    A = 1.0251535745047
    B = -0.122057498194532
    C = 0.475455422540657
    D = 0.209232924819001
    return 1./(A + B*x + C*math.pow(x,2) + D*math.pow(x,3))

def sourceSizeCorrectionTr(diameter, fwhm):
    x          = diameter / (1.2 * fwhm)
    # Here's a model that fits the theoretical beam shape better than
	# 1.2834*(1 - math.exp(-1 * math.pow(x, 2)))
    # and works well out to the first null.  Only good for Te = 13 dB
    A = 0.972173505743667
    B = 1.2336105495135
    D = -0.119234647391762
    return 1./(D + A/(1.-math.exp(-B*pow(x,2))))

def getKs(backend, bandwidth, bw, windows, receiver, beams):
    # Note: KFPA is a 7 beam rx, but we want to use 8 beams for calculations.
    beams = 8 if receiver == 'KFPA' and beams == 7 else beams
    if backend == 'Spectral Processor':
        retval = 1.3, 1.21
    elif backend == 'GBT Spectrometer':
        values = spectrometerK1K2.get(bandwidth)
        sampling = bw / (2.*float(windows) * float(beams))
        if bandwidth == 50 and sampling < 0.00076:
            retval = values[0]
        elif bandwidth == 50 and sampling >= 0.00076:
            retval = values[1]
        elif bandwidth == 12.5 and sampling < 0.00019:
            retval = values[0]
        elif bandwidth == 12.5 and sampling >= 0.00019:
            retval = values[1]
        else:
            retval = values
    else:
        retval = 1, 1
    return retval

def getK2(backend):
    return 1.21 if backend == 'Spectral Processor' or backend == 'GBT Spectrometer' else 1

def getEtaTrack(freq, backend):
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    return wv.eta_track_mustang if backend == 'Mustang' else wv.eta_track

def getEtaDSS(freq):
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    return wv.eta_dss

def getEtaSurf(freq):
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    return wv.eta_surf

def getTrcvr(freq, backend):
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    return wv.t_rcvr_mustang if backend == 'Mustang' else wv.t_rcvr

def getTatm(freq):
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    return wv.t_atm

def getTau0(freq):
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    return wv.tau0

def calculateEST0(freq, airmass, backend = None):
    """ Deprecated """
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    t_spill, t_cmb = 3, 3
    t_rcvr         = wv.t_rcvr_mustang if backend == 'Mustang' else wv.t_rcvr
    return (t_rcvr + t_spill + wv.t_atm) * math.exp(wv.tau0 * airmass) - (wv.t_atm - t_cmb) 

def calculateAttenuation(est0, freq, backend = None):
    """ Deprecated """
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    t_spill, t_cmb = 3, 3
    t_rcvr         = wv.t_rcvr_mustang if backend == 'Mustang' else wv.t_rcvr
    eta_track      = wv.eta_track_mustang if backend == 'Mustang' else wv.eta_track
    return (est0 * math.sqrt((eta_track * wv.eta_surf) / wv.eta_dss) + (wv.t_atm - t_cmb)) / \
              (t_rcvr + t_spill + wv.t_atm)

def calculateESTTS(freq, t_bg, t_gal_bg, est0, backend = None):
    """ Deprecated """
    wv = WeatherValues.objects.get(frequency = round(freq) / 1000)
    if wv is None:
        return None

    eta_track = wv.eta_track_mustang if backend == 'Mustang' else wv.eta_track
    return (t_bg + t_gal_bg) / math.sqrt(eta_track * wv.eta_surf) + est0 / math.sqrt(wv.eta_dss)
    
def raDec2thetaPhi(r, d):
    ra   = r * 15 * math.pi / 180
    dec  = d * math.pi / 180
    l, b = slalib.sla_eqgal(ra, dec)
    l *= 180 / math.pi
    b *= 180 / math.pi
    j = int(b + 91.5)
    j = 180 if j > 180 else j
    nl = int(l - 0.5)
    nl = 359 if l < 0.5 else nl
    i  = (nl / 4) + 1
    return i, j

def calcTsky(r, d, freq, gal):
    if gal != 'model':
        return 0
    i, j = raDec2thetaPhi(r, d)
    tsky = TSky.objects.get(theta = i - 1, phi = j - 1)
    return tsky.tsky * math.pow(freq / 408., -2.6) if tsky is not None else 0

def isNotVisible(declination, min_elevation):
    return min_elevation == 90.0 \
        or declination <= GBT_LAT - 90.0 + min_elevation \
        or declination >= GBT_LAT + 90. - min_elevation

def getTimeVisible(declination, min_elevation):
    """
    Returns number of hrs a source at a specified Declination is 
    visible above a specified elevation.  From Meeus, equation 12.6
    Code was copied from Ron's Tcl script.
    Inputs in degrees.
    """

    if isNotVisible(declination, min_elevation):
        # Never visible since no sky left to rise above; Or, never
        # visible since declination will never rise above min_el
        return 0.0
    
    # convert all to radians
    rEl = deg2rad(min_elevation)
    rDec = deg2rad(declination)
    rLAT = deg2rad(GBT_LAT)

    # denominator
    if GBT_LAT == 90. or declination == 90. :
        d = 0.0
    else: 
        d = math.cos(rLAT)*math.cos(rDec)

    # numerator
    n = math.sin(rEl) - math.sin(rLAT)*math.sin(rDec)

    if abs(n) >= d:
        # Circumpolar!  Always up!
        return 24.0
    else:
        return 2.0 * rad2hr(math.acos(n/d))

