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

from   Archiver  import Archiver
from   mx        import DateTime
from   nell      import settings
import pg
import os
import csv

CNN = pg.connect(dbname = settings.BENCHMARK_DB_NAME
               , host   = settings.DATABASE_HOST
               , port   = int(settings.DATABASE_PORT)
               , user   = settings.DATABASE_USER
               , passwd = settings.DATABASE_PASSWORD
                )

# The sql file utilities/database/create_benchmark.sql
# may used to initiate a benchmark database.

class dbArchiver(Archiver):

    def __init__(self, kase):
        Archiver.__init__(self)

        self.cnn = CNN
        if self.cnn == None:
            raise LookupError, "Failed to connect to Benchmark database."

        self.kase = kase

    def Text2SQLText(self, script):
        return script.replace("\'", r"\'")

    def getAvgElapsedTime(self):
        r = self.cnn.query(
            """
            SELECT AVG(elapsed_time)
            FROM test
            WHERE kase = '%s' AND name = '%s'
            """ % (self.kase,self.values["name"]))

        return r.getresult()[0][0]

    def onStartTest(self):
        self.hostname = os.uname()[1]
        self.username = os.getenv("USER") #os.getlogin()
        self.values["process_info_start"] = self.getTopSummary() 
        
    def onEndTest(self):
        self.values["process_info_end"] = self.getTopSummary() 
        
    def write(self):

        r = self.cnn.query(
            """
            INSERT INTO test (kase, name, start_time, elapsed_time, username, hostname, process_info_start, process_info_end)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
            """ % (self.kase
                 , self.values["name"]
                 , str(DateTime.gmtime(self.values["start_time"]))[0:19]
                 , self.values["elapsed_time"]
                 , self.username
                 , self.hostname
                 , self.Text2SQLText(self.values["process_info_start"])
                 , self.Text2SQLText(self.values["process_info_end"])))

        return int(r)

    def getTopSummary(self):
        processData = self.getTopData()
        processData = self.siftTopData(processData)
        return self.reportTopData(processData)
    
    def getTopData(self):
        header = os.popen("top -S -b -n 1 2>/dev/null | head -7")
        header = csv.reader(header, delimiter = " ", skipinitialspace = True)
        topData = []
        for row in header:
            if row: #if row is not empty
                for item in row:
                    topData.append(item)
        del header
        return topData
    
    def siftTopData(self,rawTopData):
        topResults = [self.hostname]
        topResults.append(rawTopData[0])
        offsets = [7, 9, 11, 13, 15, 19, 21, 23, 25, 27, 30, 32, 34]
    
        for m in range(len(rawTopData)):
            if rawTopData[m].find("user") != -1:
                baseIndex = m - 1
                break
        else:
            baseIndex = 5
        topResults.append(rawTopData[baseIndex])
        for offset in offsets:
            topResults.append(rawTopData[baseIndex + offset].replace("%", ""))
        del rawTopData
        return topResults
    
    def reportTopData(self,siftedTopResults):
        header = ["hostname"
            , "timestamp"
            , "users"
            , "total processes"
            , "sleeping processes"
            , "running processes"
            , "zombie processes"
            , "stopped processes"
            , "CPU: user"
            , "CPU: system"
            , "CPU: nice"
            , "CPU: iowait"
            , "CPU: idle"
            , "Mem: avail"
            , "Mem: used" 
            , "Mem: free" ]
        info = ""
        for i in range(len(header)):
            info += header[i] + " = "+siftedTopResults[i]
            if i != len(header)-1:
                info += ", "
        del siftedTopResults
        return info    
                
    def printLatency(self, latency):
        pass
