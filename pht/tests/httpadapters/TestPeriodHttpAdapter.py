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

import simplejson as json
from django.test      import TransactionTestCase, TestCase
from pht.httpadapters import PeriodHttpAdapter
from pht.models       import *
from datetime         import datetime

class TestPeriodHttpAdapter(TransactionTestCase):

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):

        # set this in order to diff these ridiculously long
        # Json dictionaries
        self.maxDiff = None

        # creat a period
        p = Proposal.objects.all()[0]
        s = p.session_set.all()[0]

        p = Period( session = s
                  , start = datetime(2012, 1, 1, 12)
                  , duration = 2.0
                  )
        p.save()

    def test_jsonDictAllHP(self):
        p = Period.objects.all()[0]
        pa = PeriodHttpAdapter(period = p)
        # here's what the json for this session looks like when
        # we use the ORM
        ormJson = pa.jsonDict()
        # here's what the json for this session looks like when
        # we use the high performance query of the DB
        sqlJsons = pa.jsonDictAllHP()
        self.assertEqual(1, len(sqlJsons))
        sqlJson = sqlJsons[0]
        #keys = ormJson.keys()
        #print "ORM fields: "
        #for k in sorted(keys):
        #    if k != 'abstract':
        #        print k, " : ", ormJson[k]
        #print "********************"
        #print "SQL fields: "
        #keys = sqlJson.keys()
        #for k in sorted(keys):
        #    if k != 'abstract':
        #        print k, " : ", sqlJson[k]
        # still some issues w/ time accounting to figure out
        #self.assertEqual(ormJson, sqlJson)
        fields = sorted(ormJson.keys())
        ignoreFields = [] 
        for f in fields:
            if f not in ignoreFields:
                self.assertEqual(ormJson.get(f)
                               , sqlJson.get(f))

