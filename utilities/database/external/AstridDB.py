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

from datetime                          import datetime, timedelta
from utilities                         import getConfigValue
import MySQLdb as m


class AstridDB(object):

    def __init__(self, host = None
                     , user = None
                     , passwd = None
                     , dbname = "turtle_sim" # guard the prod. DB
                     , test = False
                     , quiet = False
                     ):

        # protect the production DB?
        self.test = test

        # for reporting
        self.reportLines = []
        self.quiet = quiet
        self.filename = "AstridDBReport.txt"

        self.configFile = "/home/gbt/etc/config/system.conf"             
        self.host   = self.getConfigValue(host,   "DatabaseHost")
        self.dbname = self.getConfigValue(dbname, "Turtle_Database_User")
        self.user   = self.getConfigValue(user,   "Turtle_Database_User")
        self.passwd = self.getConfigValue(passwd, "Turtle_Database_Passwd")

        self.db = m.connect(host   = self.host
                          , user   = self.user
                          , passwd = self.passwd
                          , db     = self.dbname
                            )
        self.cursor = self.db.cursor()

    def __del__(self):
        self.cursor.close()

    def add(self, lines):
        "For use with printing reports"
        if not self.quiet:
            print lines
        self.reportLines += lines

    def writeReport(self):
        "Write out what transactions occured to a file."
        f = open(self.filename, 'w')
        f.writelines(self.reportLines)
        f.close()

    def getConfigValue(self, value, keyword):
        if value is not None:
            return value
        else:
            return getConfigValue(None, keyword, self.configFile)

    def addProjects(self, pcodes):
        """
        Given a list of project codes from the DSS, translates eachone
        to its Astrid equivalent, and inserts it in the Astrid DB.
        """

        self.add("Adding %d new project codes to database %s\n" % \
            (len(pcodes), self.dbname))
        count = 0    
        for pcode in pcodes:
            astridCode = self.dssCode2astridCode(pcode)
            self.add("Translated %s to %s\n" % (pcode, astridCode))
            if not self.astridCodeExists(astridCode):
                self.add("Inserting Astrid Code: %s\n" % astridCode)
                self.insertAstridCode(astridCode)
                count += 1
            else:
                self.add("Astrid Code %s already exists\n" % astridCode)
        self.add("Successfully added %d new project codes\n" % count)        
        self.writeReport()

    def dssCode2astridCode(self, pcode):
        "Simple algorithm for converting DSS codes to Astrid codes."

        astridCode = pcode.replace("-", "_")
        if astridCode[0] != "T":
            astridCode = "A" + astridCode
        return astridCode    

    def astridCodeExists(self, pcode):

        # Why are we doing it this way, and not more direclty with
        # a 'WHERE name = pcode' in the query?
        # Because that's the way it's done in 
        # /users/monctrl/bin/add_project.py
        query = "SELECT name FROM ObsProjectRef"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for r in rows:
            name = r[0]
            if pcode == name:
                return True
        return False
        
    def insertAstridCode(self, pcode):

        query = "INSERT INTO ObsProjectRef (id, name, primary_observer, session) VALUES (DEFAULT, '%s', DEFAULT, DEFAULT)" % pcode
        self.cursor.execute(query)

    def removeAstridCode(self, pcode):
        "Only for keeping the turtle_sim DB clean"

        # double check that we can't touch the production DB
        assert self.test
        assert self.dbname != "turtle"
        query = "DELETE FROM ObsProjectRef WHERE name = '%s'" % pcode
        self.cursor.execute(query)

