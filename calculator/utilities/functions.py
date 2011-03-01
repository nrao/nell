from calculator.models import WeatherValues
from sesshuns.models   import first

import math

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

def getMinTopoFreq(backend, bandwidth, windows, beams):
    if backend == 'Spectral Processor':
        channels = 1024
    elif backend == 'GBT Spectrometer':
        channels = freqRes.get(bandwidth)
    else:
        return 1

    retval = (bandwidth / float(channels)) * windows  * beams * 1000 if channels is not None else 0.0
    return retval

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

def getKs(backend, bandwidth, bw, windows, beams):
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
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    return wv.eta_track_mustang if backend == 'Mustang' else wv.eta_track

def getEtaDSS(freq):
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    return wv.eta_dss

def getEtaSurf(freq):
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    return wv.eta_surf

def getTrcvr(freq, backend):
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    return wv.t_rcvr_mustang if backend == 'Mustang' else wv.t_rcvr

def getTatm(freq):
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    return wv.t_atm

def getTau0(freq):
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    return wv.tau0

def calculateEST0(freq, airmass, backend = None):
    """ Deprecated """
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    t_spill, t_cmb = 3, 3
    t_rcvr         = wv.t_rcvr_mustang if backend == 'Mustang' else wv.t_rcvr
    return (t_rcvr + t_spill + wv.t_atm) * math.exp(wv.tau0 * airmass) - (wv.t_atm - t_cmb) 

def calculateAttenuation(est0, freq, backend = None):
    """ Deprecated """
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    t_spill, t_cmb = 3, 3
    t_rcvr         = wv.t_rcvr_mustang if backend == 'Mustang' else wv.t_rcvr
    eta_track      = wv.eta_track_mustang if backend == 'Mustang' else wv.eta_track
    return (est0 * math.sqrt((eta_track * wv.eta_surf) / wv.eta_dss) + (wv.t_atm - t_cmb)) / \
              (t_rcvr + t_spill + wv.t_atm)

def calculateESTTS(freq, t_bg, t_gal_bg, est0, backend = None):
    """ Deprecated """
    wv = first(WeatherValues.objects.filter(frequency = round(freq) / 1000))
    if wv is None:
        return None

    eta_track = wv.eta_track_mustang if backend == 'Mustang' else wv.eta_track
    return (t_bg + t_gal_bg) / math.sqrt(eta_track * wv.eta_surf) + est0 / math.sqrt(wv.eta_dss)
    
