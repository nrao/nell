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

GBT_LAT = 38 + 26 / 60.
LAT     = 51.57
backendsWithKnownRes = ('Spectral Processor', 'GBT Spectrometer', 'FPGA Spectrometer')

def getMinTopoFreq(backend, bandwidth, windows, receiver, beams):
    if backend in backendsWithKnownRes:
        qBandwidth = None if backend == 'Spectral Processor' else bandwidth
        fr         = FrequencyResolution.objects.filter(backend__dss_backend__name = backend
                                                      , bandwidth = qBandwidth)
        if backend == 'FPGA Spectrometer' and windows in (8, 16):
            fr = fr.filter(windows__name = int(windows))
        if len(fr) == 0:
            return 1
        channels = fr[0].max_number_channels
    else:
        return 1

    if backend == 'FPGA Spectrometer':
        return bandwidth * 1e3 / float(channels) # kHz
    else:
        # Note: KFPA is a 7 beam rx, but we want to use 8 beams for calculations.
        beams = 8 if receiver == 'KFPA' and beams == 7 else beams
        return (bandwidth / float(channels)) * windows  * beams * 1000 if channels is not None else 0.0

def dec2Els(dec):
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

def sourceSizeCorrection(diameter, fwhm):
    try:
        x          = diameter / (1.2 * fwhm)
        correction = (1 - math.exp(-1 * math.pow(x, 2))) / math.pow(x, 2)
    except ZeroDivisionError:
        return 1
    return correction

def getKs(backend, bandwidth, bw, windows, receiver, beams):
    # Note: KFPA is a 7 beam rx, but we want to use 8 beams for calculations.
    beams = 8 if receiver == 'KFPA' and beams == 7 else beams
    if backend == 'Spectral Processor':
        retval = 1.3, 1.21
    elif backend == 'GBT Spectrometer':
        values = spectrometerK1K2.get(bandwidth)
        sampling = bw / (float(windows) * float(beams))
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
