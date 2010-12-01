from calculator.models import FrequencyResolution

def getMinTopoFreq(backend, bandwidth, windows):
    if backend == 'SP':
        fr = FrequencyResolution.objects.filter(backend__name = backend)[0]
    elif backend == 'ACS':
        fr = FrequencyResolution.objects.filter(backend__name = backend, bandwidth = bandwidth)[0]

    return (bandwidth * windows) / fr.max_number_channels * 1000
