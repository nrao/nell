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
from pht.utilities import * 
from pht.utilities.Conversions import Conversions 

class PstInterface(object):

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "nrao_200"
                     , passwd = "wugupHA8"
                     , database = "nrao_200"
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                            )
        self.cursor = self.db.cursor()
        self.silent = silent

    def __del__(self):
        self.cursor.close()

    def getKeys(self):
        return [v for v, _, _, _, _, _, _ in self.cursor.description]

    def safeUnicode(self, string):
        try:
            uni = unicode(string)
        except UnicodeDecodeError:
            if len(string) == 1:
                uni = ''
            else:
                uni = ''.join([self.safeUnicode(s) for s in string])
        return uni

    def getUsers(self):
        q = """
            select person_id, firstName, lastName
            from person
            """
        self.cursor.execute(q)
        keys = self.getKeys()
        return [dict(zip(keys, map(self.safeUnicode, row))) for row in self.cursor.fetchall()]

    def getAuthor(self, author_id):
        q = """
            select * from author where author_id = %s
            """ % author_id
        self.cursor.execute(q)
        keys = self.getKeys()
        row  = self.cursor.fetchone()
        return dict(zip(keys, map(self.safeUnicode, row)))

    def getSrcField(self, field, table):
        q = "select DISTINCT %s from %s order by %s" % (field, table, field)
        print q
        self.cursor.execute(q)
        keys = self.getKeys()
        return [dict(zip(keys, map(self.safeUnicode, row))) for row in self.cursor.fetchall()]

    def getRange(self, field, table):

        rows = self.getSrcField(field, table)
        values = [r[field] for r in rows]
        minV = None
        maxV = None
        diffs = []
        exceptions = 0
        for v in values:
            if v.find(':') != -1:
                parts = v.split(':')
                if len(parts) > 1:
                    try:
                        x = int(parts[0])
                        if minV is None or x < minV:
                            minV = x
                        if maxV is None or x > maxV:
                            maxV = x
                    except:
                        exceptions = exceptions + 1
            else:
                diffs.append(v)
        
        print "min for field: %s = %d" % (field, minV)
        print "max for field: %s = %d" % (field, maxV)
        print "from %d distinct rows" % len(values)
        print "number of non sexigesimals : %d" % len(diffs)
        print "number of exceptions: %d" % exceptions
        print ""
        return (values, diffs)

    def reportOnFields(self):
        
        fields = [('right_ascension', 'source')
                , ('right_ascension_range', 'source')
                , ('declination', 'source')
                , ('declination_range', 'source')
                , ('MINIMUM_LST', 'session')
                , ('MAXIMUM_LST', 'session')
                , ('ELEVATION_MINIMUM', 'session')
                 ]
        for field, table in fields:
            self.getRange(field, table)

    def testFieldConversionsFields(self):
        "Tests the same conversions we'll be doing when importing on ALL values"

        c = Conversions()

        fields = [('right_ascension', 'source', c.tryHourConversions)
                , ('right_ascension_range', 'source', c.tryHourConversions)
                , ('declination', 'source', c.tryDegreeConversions)
                , ('declination_range', 'source', c.tryDegreeConversions)
                , ('MINIMUM_LST', 'session', c.tryHourConversions)
                , ('MAXIMUM_LST', 'session', c.tryHourConversions)
                 ]

        for field, table, fn in fields:
            bads = []
            rows = self.getSrcField(field, table)
            values = [r[field] for r in rows]
            for v in values:
               anyMatch, value = fn(v)
               if value is None:
                   bads.append((v, anyMatch, value))
            print "Of %d rows of %s, %d failed conversion." % \
                (len(rows), field, len(bads))

            f = open(field,'w')
            lines = [v+"\n" for v, _, _ in bads] 
            f.writelines(lines)
            f.close()
                

            
            

