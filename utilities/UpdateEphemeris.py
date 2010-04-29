#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *

# this module rocks!
import ephem


class UpdateEphemeris():

    """
    This class is responsible for finding all sessions that have moving sources
    and updating thier ra & dec, where possible, and reporting on results.
    """

    def __init__(self, filename = None):

        self.reportLines = []
        self.quietReport = False
        self.filename = filename

        self.errors = []
        self.updates = []

        # the following are the defaults for ephemClass.compute
        # but lets be explicit
        self.epoch = "2000"
        now = datetime.utcnow()
        self.nowStr = now.strftime("%Y/%m/%d")

    def add(self, lines):
        "For use with printing reports"

        if not self.quietReport:
            print lines
        self.reportLines += lines

    def report(self):
        "Write the results to the specified file"

        self.reportList(self.updates, "Updates")
        self.reportList(self.errors, "Errors")

        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)

    def reportList(self, lines, subject):
        "Used for adding stored strings to the report."

        if len(lines) > 0:
            self.add("\n*** %s:\n" % subject)
            for l in lines:
               self.add(l)
        else:
            self.add("\n*** NO %s\n" % subject)

    def update(self):
        "Find all moving targets, update their ra & dec, report on it."

        # init reporting
        self.updates = []
        self.errors = []
        self.reportLines = []

        self.add("Updating Ephemeris for %s (UTC)\n" % datetime.utcnow())

        tgs = Target.objects.filter(system__name = "Ephemeris")

        self.add("Attempting to update %d targets.\n" % len(tgs))

        for tg in tgs:
            self.updateTarget(tg)

        self.report()    

    def updateTarget(self, target):
        "Set this target's ra & dec to today's appropriate value"
         
        ep = self.getEphemObj(target)

        if ep is None:
            return

        ep.compute(self.nowStr, self.epoch)

        orgRa = target.get_horizontal()
        orgDec = target.get_vertical()

        target.horizontal= ep.ra
        target.vertical = ep.dec
        target.save()

        # report 
        line = "Session %s, Source %s (ra, dec) change : (%s, %s) -> (%s, %s)\n" % (target.session.name
                                                     , target.source
                                                     , orgRa
                                                     , orgDec
                                                     , target.horizontal
                                                     , target.vertical)
        self.updates.append(line) 

    def getEphemObj(self, target):
        "Make sure we can get the object which gives the ra & dec"

        className = target.source
        try:
            epClass = getattr(ephem, className)
            ep = epClass()
            return ep
        except AttributeError:
            self.errors.append("Source name incorrect: %s\n" % className)
            return None
        except:
            self.errors.append("Unknown Error with: %s\n" % className)
            return None

# TBF: does not work - import errors when trying to call this way
if __name__ == '__main__':
    up = UpdateEphemeris(filename = "updateEphemeris.txt")
