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
from pht.httpadapters import ProposalHttpAdapter
from pht.models       import *

class TestProposalHttpAdapter(TransactionTestCase):

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):

        # again, I'm too lazy to fix the fixture - so add a code here
        ot = ObservingType.objects.get(type = 'Spectroscopy')
        ot.code = 'S'
        ot.save()
        sc = ScientificCategory.objects.get(category = 'Interstellar Medium')
        sc.code = 'ISM'
        sc.save()

        # set this in order to diff these ridiculously long
        # Json dictionaries
        self.maxDiff = None

    def test_copy(self):
        proposal = Proposal.objects.get(pcode = 'GBT12A-002')

        # Fix up test session
        for s in proposal.session_set.all():
            n = SessionNextSemester()
            n.save()
            s.next_semester = n
            s.save()

        adapter = ProposalHttpAdapter(proposal)
        new_proposal = adapter.copy('GBT12A-003')
        self.assertTrue(new_proposal.source_set.all() > 0)
        self.assertTrue(new_proposal.session_set.all() > 0)

    def test_jsonDictAllHP(self):
        p = Proposal.objects.all()[0]
        pa = ProposalHttpAdapter(proposal = p)
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
            #else:
            #    print "ORM: ", ormJson.get(f)
            #    print "SQL: ", sqlJson.get(f)

    def test_from_post(self):

        self.assertEqual(1, len(Proposal.objects.all()))

        p = Proposal.objects.all()[0]
        pa = ProposalHttpAdapter(proposal = p)
        ormJson = pa.jsonDict()
        ormJson['pcode'] = u'GBT12A-003'

        pa.initFromPost(ormJson)
        self.assertEqual(2, len(Proposal.objects.all()))

