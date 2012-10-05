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

import settings

class PstInterface(object):

    def __init__(self, silent = True):
        self.db = m.connect(host   = settings.PST['HOST']
                          , user   = settings.PST['USER']
                          , passwd = settings.PST['PASSWORD']
                          , db     = settings.PST['NAME']
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

    def getProposalCodes(self):
        q = """
            select PROP_ID
            from proposal
            order by PROP_ID
            """
        self.cursor.execute(q)
        return [{'pcode' : r[0]} for r in self.cursor.fetchall()]
        #keys = self.getKeys()
        #return [dict(zip(keys, map(self.safeUnicode, row))) for row in self.cursor.fetchall()]

    def getUsers(self):
        q = """
            select person_id, firstName, lastName
            from person
            """
        self.cursor.execute(q)
        keys = self.getKeys()
        return [dict(zip(keys, map(self.safeUnicode, row))) for row in self.cursor.fetchall()]

    def fetchoneDict(self):
        keys = self.getKeys()
        row  = self.cursor.fetchone()
        return dict(zip(keys, map(self.safeUnicode, row)))

    def isJointProposal(self, pcode):
        pcode    = pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/')
        q = "select JOINT_PROPOSAL_TYPE from proposal where PROP_ID = '%s'" % pcode
        self.cursor.execute(q)
        row = self.cursor.fetchone()
        if row is not None:
            return row[0].lower() != 'not a joint proposal'
        else:
            return False

    def getAuthor(self, author_id):
        q = """
            select * from author where author_id = %s
            """ % author_id
        self.cursor.execute(q)
        return self.fetchoneDict()

    def getUserInfo(self, person_id):
        q = """
        select p.lastName, p.firstName, o.formalName as affiliation, pt.personType, e.email, 
          ph.phone, a.street1, a.street2, a.city, s.state, a.postalCode, c.addressCountry
        from (((((((person as p 
          left outer join organization as o on o.organization_id = p.defaultOrganization_id)
          left outer join email as e on e.person_id = p.person_id and e.defaultEmail = true)
          left outer join phone as ph on ph.person_id = p.person_id and ph.defaultPhone = true)
          left outer join address as a on a.person_id = p.person_id and a.defaultAddress = true)
          left outer join addressState as s on s.addressState_id = a.addressState_id)
          left outer join addressCountry as c on c.addressCountry_id = a.addressCountry_id)
          left outer join person_personType as ppt on ppt.person_id = p.person_id)
          left outer join personType as pt on pt.personType_id = ppt.personType_id
        where p.person_id = %s limit 1
            """ % person_id
        self.cursor.execute(q)
        return dict([(k, v if v is not None and v != 'None' else '') for k, v in self.fetchoneDict().iteritems()])

    def getProposalTechnicalReviews(self, pcode):
        pcode = pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/')
        q = """
        select tr.commentsForAuthors, tr.commentsForTAC, person.firstName, person.lastName
        from (((proposal as p 
          join proposal_reviews as pr on pr.proposal_id = p.proposal_id) 
          join technical_reviews as tr on tr.review_id = pr.review_id)
          join referees as ref on ref.referee_id = pr.referee_id)
          join person on person.person_id = ref.person_id
        where PROP_ID = '%s'
        """ % pcode
        self.cursor.execute(q)
        return self.cursor.fetchall()
        
    def getSrcField(self, field, table):
        q = "select DISTINCT %s from %s order by %s" % (field, table, field)
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
                

            
            

