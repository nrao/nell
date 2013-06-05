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

#! /usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)
from datetime   import datetime

from scheduler.models import *
import urllib

# this module rocks!
import ephem


class UpdateEphemeris():

    """
    This class is responsible for finding all sessions that have moving sources
    and updating thier ra & dec, where possible, and reporting on results.
    It's two basic tools it uses are:
       * ephem library
       * website containing ephemeris info
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

        # resources for finding targets that aren't in ephem
        self.baseUrl = "http://www.minorplanetcenter.net/iau/Ephemerides/"
        self.resources = [("Comets"
                         , self.baseUrl + "Comets/Soft03Cmt.txt"
                         , self.parseCometLine)
                         , ("Asteroids"
                         , self.baseUrl + "Bright/2013/Soft03Bright.txt"
                         , self.parseAsteroidLine)
                         , ("Unusual"
                         , self.baseUrl + "Unusual/Soft03Unusual.txt"
                         , self.parseCometLine)
                         ]

        self.specialObjs = {}

    def add(self, lines):
        "For use with printing reports"

        if not self.quietReport:
            print lines
        self.reportLines += lines

    def report(self):
        "Write the results to the specified file"

        self.reportList(self.errors, "Errors")
        self.reportList(self.updates, "Updates")

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

        # update resources
        self.updateResources()
        self.add("Updated Ephemeris resources\n")

        tgsAll = Target.objects.filter(system__name = "Ephemeris")
        tgs = [tg for tg in tgsAll if not tg.session.status.complete]

        self.add("Attempting to update %d targets.\n" % len(tgs))

        for tg in tgs:
            self.updateTarget(tg)

        self.report()    

    def parseCometLine(self, line):
        "Custom function for parsing a line in the ephemeris file."
        if line[0] == "#":
            return (None, None)
        parts = line.split(",")
        name = parts[0]
        return (name, line)

    def parseAsteroidLine(self, line):
        "Custom function for parsing a line in the ephemeris file."
        # skip the comments
        if line[0] == "#":
            return (None, None)
        # skip the number line
        l2 = " ".join(line.split(" ")[1:])
        # get the name
        parts = l2.split(",")
        name = parts[0]
        return (name, l2)

    def updateResources(self):
        "Grabs text from websites and converts them to useful lookups"
        for name, url, parseFnc in self.resources:
            self.updateResource(name, url, parseFnc)

    def updateResource(self, name, url, parseFnc):
        lines = self.retrieveResource(name, url)
        self.parseResourceLines(name, lines, parseFnc)

    def retrieveResource(self, name, url):
        "Download the resource available at given url, and return the contents."

        # clean up txt file?
        filename =  name + ".txt"
        urllib.urlretrieve(url, filename = filename)
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()

        return lines

    def parseResourceLines(self, name, lines, parseFnc):
        """
        Interpret the website info into the ephemeris we will use.
        Given every lines of the resource, parse these lines using
        the given function, and update the specialObjs dictionary.
        """
        for l in lines:
            dataName, data = parseFnc(l)
            if dataName is not None and data is not None:
                self.specialObjs[dataName] = (data, name)

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
        "Make sure we can get the proper object which gives the ra & dec"

        # Either the source name is one of the supplied major/minor planets and 
        # satellites, or it is one in a number of different 
        # lists, such comets & asteroids ('special')
        if target.source in self.specialObjs.keys():
            obj = self.getEphemSpecialObj(target, self.specialObjs)
        else:
            obj = self.getEphemPlanetObj(target)
        return obj    

    def getEphemSpecialObj(self, target, objects):
        "Uses the given dict of ephemeris to calculate ra & dec"

        try:
            line, type = objects[target.source]
            comet = ephem.readdb(line)
            return comet
        except:
            self.errors.append("Unknown Error w/ comet: %s\n" % target.source)
            return None

    def getEphemPlanetObj(self, target):
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

if __name__ == '__main__':
    #up = UpdateEphemeris(filename = "updateEphemeris.txt")
    UpdateEphemeris().update()
