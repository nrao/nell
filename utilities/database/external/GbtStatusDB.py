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
import settings

class GbtStatusDB(object):

    """
    This class provides a simple interface to the Gbt Status DB,
    which provides data to the Gbt Status clients.
    """

    def __init__(self, host = None
                     , user = None
                     , passwd = None
                     , dbname = None 
                     , test = False
                     , quiet = False
                     ):

        # protect the production DB?
        self.test = test

        # for reporting
        self.reportLines = []
        self.quiet = quiet
        self.filename = "GbtStatusDBReport.txt"

        self.host   = self.getConfigValue(host,   "HOST")
        self.dbname = self.getConfigValue(dbname, "NAME")
        self.user   = self.getConfigValue(user,   "USER")
        self.passwd = self.getConfigValue(passwd, "PASSWORD")

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
            return settings.GBTSTATUSDB.get(keyword)

        
    def getSourceInfo(self):

        query = "SELECT source, major, minor, epoch FROM status"
        self.cursor.execute(query)
        return self.cursor.fetchone()



