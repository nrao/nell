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

import MySQLdb as m

class InitDSSPrime(object):
    """
    This class is responsible for initializing the dss_prime MySQL database
    prior to data transfer from Carl's database.
    """

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "dss"
                     , passwd = "asdf5!"
                     , database = "dss_prime"
                 ):
        self.host     = host
        self.user     = user
        self.passwd   = passwd
        self.database = database
        self.resetDB()
        self.initDB()

    def connect(self):
        self.db = m.connect(host   = self.host
                          , user   = self.user
                          , passwd = self.passwd
                          , db     = self.database
                            )
        self.cursor   = self.db.cursor()

    def disconnect(self):
        self.cursor.close()

    def resetDB(self):
        """
        Drop and create the database.  This is the quitest way to empty
        the database.  Then load the schema and data.  Notice we use
        a different connection for dropping the database.  MySQL will
        not let you drop a database that has open connections, so the
        connection we are using here is opened on a different database.
        """
        db = m.connect(host   = self.host
                     , user   = self.user
                     , passwd = self.passwd
                     , db     = "dss"
                      )
        cursor = db.cursor()
        cursor.execute("DROP DATABASE IF EXISTS %s" % self.database)
        cursor.execute("CREATE DATABASE %s" % self.database)
        cursor.close()


    def initDB(self):
        self.connect()
        #  Load schema
        sql = open("dss_prime.sql").read()
        print "Loading DB schema..."
        self.cursor.execute(sql)
        self.disconnect()

        self.connect()
        #  Load inital data
        sql = open("populate_dss_prime.sql").read()
        print "Loading inital data..."
        self.cursor.execute(sql)
        self.disconnect()

def show_help():
    print "\nUsage: python tools/database/InitDSSPrime.py <database name>\n"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        show_help()
        sys.exit()

    dbname = sys.argv[1]
    InitDSSPrime(database = dbname)
    print "DSS Prime database initialized at", dbname

