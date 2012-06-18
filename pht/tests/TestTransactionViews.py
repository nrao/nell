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
from django.test.client  import Client
from django.test      import TransactionTestCase, TestCase
from pht.httpadapters import PeriodHttpAdapter
from pht.models       import *
from datetime         import datetime

from django.conf         import settings
from django.contrib.auth import models as m

from scheduler.models    import User
from pht.models          import *
from pht.httpadapters    import *
from pht.utilities       import *

class TestTransactionViews(TransactionTestCase):

    """
    This class was spawned off of TestViews because it contains
    tests that read directly from the DB w/ SQL - we need
    to subclass from TransactionTestCase to do this.
    """

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):
        # Don't use CAS for authentication during unit tests
        if 'django_cas.backends.CASBackend' in settings.AUTHENTICATION_BACKENDS:
            settings.AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS[:-1]
        if 'django_cas.middleware.CASMiddleware' in settings.MIDDLEWARE_CLASSES:
            settings.MIDDLEWARE_CLASSES      = settings.MIDDLEWARE_CLASSES[:-1]

        self.client = Client()

        self.auth_user = m.User.objects.create_user('dss', 'dss@nrao.edu', 'asdf5!')
        self.auth_user.is_staff = True
        self.auth_user.save()

        # create the user
        self.u = User(first_name = "dss" #"Test"
                    , last_name  = "account" #"User"
                    , pst_id     = 3251
                    #, username   = self.auth_user.username
                      )
        self.u.save()
        self.u.addRole("Administrator")
        self.u.addRole("Staff")

        self.client.login(username = "dss", password = "asdf5!")

        # load the single proposal from the fixture
        self.proposal = Proposal.objects.get(pcode = "GBT12A-002")
        # too lazy to remake the fixture:
        cmts = ProposalComments()
        cmts.save()
        self.proposal.comments = cmts
        self.proposal.save()

        self.dtfmt    = "%m/%d/%Y"

        sess = self.proposal.session_set.all()[0]
        self.session = sess
        # I'm too lazy to recreate the fixture
        n = SessionNextSemester()
        n.save()
        self.session.next_semester = n
        self.session.save()

        # create a period for this session
        start = datetime(2011, 1, 1, 12)
        dur = 2.5
        self.period = Period(session = sess
                           , start = start
                           , duration = dur
                            )
        self.period.save()
        self.period_data = {
            'session'    : sess.name
          , 'handle'     : "%s (%s)" % (sess.name, sess.proposal.pcode)
          , 'session_id' : sess.id
          , 'date' : '01/01/2011'
          , 'time' : '12:00'
          , 'duration'   : dur
        }

    def tearDown(self):
        for p in Proposal.objects.all():
            p.delete()

    def eval_response(self, response_content):
        "Makes sure we can turn the json string returned into a python dict"
        return eval(response_content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))

    def test_periods(self):
        response = self.client.get("/pht/periods")
        results = self.eval_response(response.content)

        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(1, len(results['periods']))
        self.assertEqual('He_ELD_5G', results['periods'][0]['session'])
        self.assertEqual('GBT12A-002', results['periods'][0]['pcode'])

    def test_sessions(self):
        sess = self.proposal.session_set.all()[0]
        response = self.client.get("/pht/sessions")
        results = self.eval_response(response.content)

        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(self.proposal.pcode, results['sessions'][0]['pcode'])
        self.assertEqual(sess.name, results['sessions'][0]['name'])
        
    def test_proposals(self):
        response = self.client.get("/pht/proposals")
        results = self.eval_response(response.content)

        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(self.proposal.pcode, results['proposals'][0]['pcode'])
        self.assertEqual(self.proposal.title, results['proposals'][0]['title'])
        self.assertEqual(self.proposal.proposal_type.type, results['proposals'][0]['proposal_type'])
