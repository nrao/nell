from calculator.models       import FrequencyResolution
from utilities.SLATimeAgent  import dec2MaxEl

def getMinTopoFreq(backend, bandwidth, windows):
    if backend == 'Spectral Processor':
        fr = FrequencyResolution.objects.filter(backend__dss_backend__name = backend)[0]
    elif backend == 'GBT Spectrometer':
        fr = FrequencyResolution.objects.filter(
               backend__dss_backend__name = backend, bandwidth = bandwidth)[0]
    else:
        return 1

    return (bandwidth * windows) / float(fr.max_number_channels) * 1000

def getMaxElevation(dec):
    return dec2MaxEl(dec)

def getMinCircumpolarElevation(declination):
    return -5
