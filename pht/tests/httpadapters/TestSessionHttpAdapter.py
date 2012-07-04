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
from pht.httpadapters import SessionHttpAdapter
from pht.models       import Session, SessionNextSemester

class TestSessionHttpAdapter(TransactionTestCase):

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):

        # too lazy to fix the fixture
        s = Session.objects.all()[0]
        ns = SessionNextSemester()
        ns.save()
        s.next_semester = ns
        s.save()
        
        # *really* get it to the DB
        #transaction.commit()

        # set this in order to diff these ridiculously long
        # Json dictionaries
        self.maxDiff = None

    def test_jsonDictAllHP(self):
        sa = SessionHttpAdapter(session = Session.objects.all()[0])
        # here's what the json for this session looks like when
        # we use the ORM
        ormJson = sa.jsonDict()
        # here's what the json for this session looks like when
        # we use the high performance query of the DB
        sqlJsons = sa.jsonDictAllHP()
        self.assertEqual(1, len(sqlJsons))
        sqlJson = sqlJsons[0]
        #keys = ormJson.keys()
        #for k in sorted(keys):
        #    print k, " : ", ormJson[k]
        #print "********************"
        #keys = sqlJson.keys()
        #for k in sorted(keys):
        #    print k, " : ", sqlJson[k]
        self.assertEqual(ormJson, sqlJson)


