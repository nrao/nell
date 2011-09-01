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

from calculator.models import TSky
import math
from pyslalib import slalib

class TSkyImport(object):

    def __init__(self, filename):
        f    = open(filename)
        flat = "". join([l.replace('\n', '') for l in f.readlines()])
        data = map(float, [flat[i:i + 5].strip() for i in range(0, len(flat), 5)])
        step = 180
        self.tsky = [data[i:i + step] for i in range(0, len(data), step)]
        f.close()
        for i, row in enumerate(self.tsky):
            for j, t in enumerate(row):
                tsky = TSky(theta = i, phi = j, tsky = t)
                tsky.save()

if __name__ == "__main__":
    tsky = TSkyImport('calculator/data/tsky.dat')
