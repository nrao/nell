from django.core.management import setup_environ
import settings
setup_environ(settings)

from calculator.models import TSky
from sesshuns.models   import first
import math, slalib

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
