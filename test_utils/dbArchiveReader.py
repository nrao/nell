# Copyright (C) 2005 Associated Universities, Inc. Washington DC, USA.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 675 Mass Ave Cambridge, MA 02139, USA.
#
# Correspondence concerning GBT software should be addressed as follows:
#     GBT Operations
#     National Radio Astronomy Observatory
#     P. O. Box 2
#     Green Bank, WV 24944-0002 USA

from   Archiver import Archiver
from   mx       import DateTime
from   nell     import settings
import pg

class dbArchiveReader(Archiver):

    """
    Simple class for making it easier to read benchmark test results from 
    nell database.
    """

    def __init__(self):
        Archiver.__init__(self)

        self.host = settings.DATABASE_HOST
        self.cnn = pg.connect(dbname = settings.BENCHMARK_DB_NAME
                            , host   = self.host
                            , port   = int(settings.DATABASE_PORT)
                            , user   = settings.DATABASE_USER
                            , passwd = settings.DATABASE_PASSWORD
                             )
                             
        if self.cnn == None:
            raise LookupError, "Failed to connect to Benchmark database."

    def getTestTables(self):
        query = "SELECT DISTINCT kase FROM test"
        retval = dict()
        rs = self.cnn.query(query)
        for r in rs.getresult():
            kase = r[0]
            query = "SELECT DISTINCT name FROM test WHERE kase = '%s'" % kase
            names = []
            rs = self.cnn.query(query)
            for r in rs.getresult():
                name = r[0]
                names.append(name)
            retval[kase] = names
        return retval

    def getTestElapsedTimes(self, testKase, testName, hostName = None):
        "Gets the elapsed times for a certain test run on a certain host."
        return self.getTestValues(testKase, testName, ["elapsed_time"], hostName)

    def getTestElapsedAndStartTimes(self, testKase,  testName, hostName = None):
        """
        Gets the elapsed times and start times for a certain test run
        on a certain host.
        """
        return self.getTestValues(testKase
                                , testName
                                , ["elapsed_time", "start_time"]
                                , hostName)
        
    def getTestValues(self, testKase, testName, columns, hostName = None):
        "Gets the column values for a certain test run on certain host."
        hostName = self.host if hostName is None else hostName
        
        query = """ 
            SELECT %s
            FROM test
            WHERE kase = '%s' AND name = '%s'
        """ % (','.join(columns), testKase, testName)
           
        query += " AND hostname = '%s' " % hostName
        ncols = len(columns)
            
        values = []
        rs = self.cnn.query(query)
        for r in rs.getresult():
            value = r[0] if ncols == 1 else r
            values.append(value)
        
        return values
