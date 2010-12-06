from calculator.models import FrequencyResolution

def getMinTopoFreq(backend, bandwidth, windows):
    if backend == 'Spectral Processor':
        fr = FrequencyResolution.objects.filter(backend__dss_backend__name = backend)[0]
    elif backend == 'GBT Spectrometer':
        fr = FrequencyResolution.objects.filter(
               backend__dss_backend__name = backend, bandwidth = bandwidth)[0]
    else:
        return 1

    return (bandwidth * windows) / float(fr.max_number_channels) * 1000

def getMaxElevation(declination):
    return 85

def getMinCircumpolarElevation(declination):
    return -5
