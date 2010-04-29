from Sesshun import Sesshun
from System  import System
from utilities import TimeAgent

from django.db import models
from math      import modf

class Target(models.Model):
    session    = models.ForeignKey(Sesshun)
    system     = models.ForeignKey(System)
    source     = models.CharField(null = True, max_length = 32, blank = True)
    vertical   = models.FloatField(null = True, blank = True)
    horizontal = models.FloatField(null = True, blank = True)

    def __str__(self):
        return "%s at %s : %s" % (self.source
                                , self.horizontal
                                , self.vertical
                                  )

    def __unicode__(self):
        return "%s @ (%5.2f, %5.2f), Sys: %s" % \
            (self.source
           , float(self.horizontal)
           , float(self.vertical)
           , self.system)

    def get_horizontal(self):
        "Returns the horizontal component in sexigesimal form."
        if self.horizontal is None:
            return ""

        horz = TimeAgent.rad2hr(self.horizontal)
        mins = (horz - int(horz)) * 60
        secs = (mins - int(mins)) * 60
        if abs(secs - 60.) < 0.1:
            mins = int(mins) + 1
            if abs(mins - 60.) < 0.1:
                mins = 0.0
                horz = int(horz) + 1
            secs = 0.0
        return "%02i:%02i:%04.1f" % (int(horz), int(mins), secs)

    def get_vertical(self):
        if self.vertical is None:
            return ""

        degs = TimeAgent.rad2deg(self.vertical)

        if degs < 0:
            degs = abs(degs)
            sign = "-"
        else:
            sign = " "

        fpart, ddegs = modf(degs)
        fpart, dmins = modf(fpart * 60)
        dsecs = round(fpart * 60, 1)

        if dsecs > 59.9:
            dmins = dmins + 1
            dsecs = 0.0
        if dmins > 59.9:
            ddegs = ddegs + 1
            dmins = 0.0

        return "%s%02i:%02i:%04.1f" % (sign, int(ddegs), int(dmins), dsecs)

    def isEphemeris(self):
        return self.system.name == "Ephemeris"

    class Meta:
        db_table  = "targets"
        app_label = "sesshuns"

