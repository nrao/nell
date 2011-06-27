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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from calculator.models   import *

class GBTResourceImport(object):

    def __init__(self, filename, silent = False):
        self.silent   = silent
        self.data     = None
        file          = open(filename)
        self.raw_data = [[i for n, i in enumerate(l.split('\t')) if n < 11] 
                            for l in file.readlines()[0].split('\r') ]
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
        'Backend'                : lambda v: Calc_Backend.objects.get_or_create(name = v)
      , 'Mode'                   : lambda v: Mode.objects.get_or_create(name = v)
      , 'Receiver'               : lambda v: Receiver.objects.get_or_create(name = v)
      , '# beams'                : lambda v: Beams.objects.get_or_create(name = v)
      , 'Polarization'           : lambda v: Polarization.objects.get_or_create(name = v)
      , 'Bandwidth (MHz)'        : lambda v: Bandwidth.objects.get_or_create(name = v)
      , 'Number spectral windows': lambda v: SpectralWindows.objects.get_or_create(name = v)
      , 'Min integ time'         : lambda v: Integration.objects.get_or_create(name = v)
      , 'Switching mode'         : lambda v: Switching.objects.get_or_create(abbreviation = v)
      }

        r, created = resource_map[k](v)
        if created and not self.silent:
            print "Added:", k, r
        return r

    def createConfigurations(self):
        """
            Use getResource to get resources from the database and use the
            models to build a list of dictionaries representing the
            configurations.
        """
        self.configs = \
           [dict([(k, [self.getResource(k, v)] if type(v) != list else [self.getResource(k, i)
                   for i in v]) for k, v in d.iteritems()]) for d in self.data]

        if not self.silent:
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
        if not self.silent:
            print len(Configuration.objects.all()), "hardware configurations created."

if __name__ == "__main__":
    resources = GBTResourceImport("calculator/data/gbt_resources_table.txt")
