#from calculator.models       import FrequencyResolution
#from sesshuns.models         import first
from utilities.SLATimeAgent  import dec2MaxEl

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

def getMinTopoFreq(backend, bandwidth, windows, beams):
    if backend == 'Spectral Processor':
        channels = 1024
    elif backend == 'GBT Spectrometer':
        channels = freqRes.get(bandwidth)
    else:
        return 1

    retval = (bandwidth / float(channels)) * windows  * beams * 1000 if channels is not None else 0.0
    return retval

def getMaxElevation(dec):
    return dec2MaxEl(dec)

def getMinCircumpolarElevation(declination):
    return -5

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
        if bandwidth == 50 and sampling < 0.76:
            retval = values[0]
        elif bandwidth == 50 and sampling >= 0.76:
            retval = values[1]
        elif bandwidth == 12.5 and sampling < 0.19:
            retval = values[0]
        elif bandwidth == 12.5 and sampling >= 0.19:
            retval = values[1]
        else:
            retval = values
    else:
        retval = 1, 1
    return retval

def getK2(backend):
    return 1.21 if backend == 'Spectral Processor' or backend == 'GBT Spectrometer' else 1
