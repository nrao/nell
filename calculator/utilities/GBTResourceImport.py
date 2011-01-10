from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models     import first
from calculator.models   import *

class GBTResourceImport(object):

    def __init__(self, filename):
        self.data = None
        file      = open(filename)
        self.raw_data = [[i for n, i in enumerate(l.split('\t')) if n < 11] for l in file.readlines()[0].split('\r') ]
        file.close()
        self.processData()
        self.createConfigurations()

    def printConfigs(self):
        for c in self.configs:
            print c

    def processRow(self, key, value):
        if key in ('Switching mode', 'Receiver', 'Bandwidth (MHz)', 'Number spectral windows', 'Polarization', 'Mode'):
            value = [v.strip() for v in value.replace('"{', '').replace('}"', '').split(',')] \
                        if '{' in value else value.strip()
        return key, value

    def processData(self):
        self.raw_data = [r for r in self.raw_data if r != ['']]
        self.raw_data.reverse()
        headers = self.raw_data.pop()
        self.raw_data.reverse()
        bad_keys  = ['Additional Questions', 'Notes']
        self.data = [dict([self.processRow(k, v) for k, v in zip(headers, row) if k not in bad_keys]) for row in self.raw_data]

    def getResource(self, k, v):
        resource_map = {
        'Backend'                : lambda v: first(Calc_Backend.objects.filter(name = v)) or \
                                             Calc_Backend(name = v)
      , 'Mode'                   : lambda v: first(Mode.objects.filter(name = v)) or Mode(name = v)
      , 'Receiver'               : lambda v: first(Receiver.objects.filter(name = v))
      , '# beams'                : lambda v: first(Beams.objects.filter(name = v)) or Beams(name = v)
      , 'Polarization'           : lambda v: first(Polarization.objects.filter(name = v)) or \
                                             Polarization(name = v)
      , 'Bandwidth (MHz)'        : lambda v: first(Bandwidth.objects.filter(name = v)) or \
                                             Bandwidth(name = v)
      , 'Number spectral windows': lambda v: first(SpectralWindows.objects.filter(name = v)) or \
                                             SpectralWindows(name = v)
      , 'Min integ time'         : lambda v: first(Integration.objects.filter(name = v)) or \
                                             Integration(name = v)
      , 'Switching mode'         : lambda v: first(Switching.objects.filter(abbreviation = v)) or \
                                             Switching(name = v, abbreviation = v)
      }

        r = resource_map[k](v)
        if r is not None:
            if r.id is None:
                print "Added:", k, r
            r.save()
        return r

    def createConfigurations(self):
        # Use getResource to get resources from the database and use the
        # models to build a list of dictionaries representing the
        # configurations.
        self.configs = \
           [dict([(k, [self.getResource(k, v)] if type(v) != list else [self.getResource(k, i)
                   for i in v]) for k, v in d.iteritems()]) for d in self.data]
        #self.printConfigs()

        print len(Configuration.objects.all()), "hardware configurations initially."
        for c in self.configs:
            for r in c['Receiver']:
                for pol in c['Polarization']:
                    for bandwidth in c['Bandwidth (MHz)']:
                        for win in c['Number spectral windows']:
                            for switching in c['Switching mode']:
                                conf = Configuration(backend      = c['Backend'][0]
                                                   , mode         = c['Mode'][0]
                                                   , receiver     = r
                                                   , beams        = c['# beams'][0]
                                                   , polarization = pol
                                                   , bandwidth    = bandwidth
                                                   , windows      = win
                                                   , integration  = c['Min integ time'][0]
                                                   , switching    = switching
                                                   )
                                conf.save()
        print len(Configuration.objects.all()), "hardware configurations created."

if __name__ == "__main__":
    resources = GBTResourceImport("calculator/gbt_resources_table.txt")
