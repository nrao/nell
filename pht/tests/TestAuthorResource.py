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
from django.test         import TestCase
from django.conf         import settings
from django.contrib.auth import models as m

from scheduler.models    import User
from pht.models import Author, Proposal

class TestAuthorResource(TestCase):
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

    def test_read(self):
        proposal = Proposal.objects.all()[0]
        response = self.client.get('/pht/proposals/%s/authors' % proposal.pcode)
        self.failUnlessEqual(response.status_code, 200)

    def test_create(self):
        proposal = Proposal.objects.all()[0]
        data     = {'pcode' : proposal.pcode
                  , 'pst_person_id'     : 1
                  , 'affiliation'       : 'NRAO'
                  , 'domestic'          : 'true'
                  , 'new_user'          : 'false'
                  , 'email'             : 'foo@bar.com'
                  , 'telephone'         : '555-555-1234'
                  , 'last_name'         : 'Smith'
                  , 'first_name'        : 'John'
                  , 'thesis_observing'  : 'false'
                  , 'oldauthor_id'      : '0'
                  , 'storage_order'     : 500
                  , 'support_requester' : 'false'
                  , 'supported'         : 'false'
                  , 'budget'            : 2.5
                  }
        response = self.client.post('/pht/authors', json.dumps(data)
                                  , content_type='application/json')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace('false', 'False').replace('null', 'None'))
        self.assertEqual(results['email'], data['email'])

    def test_update(self):
        proposal = Proposal.objects.all()[0]
        data     = {'pcode' : proposal.pcode
                  , 'pst_person_id'     : proposal.pi.pst_person_id
                  , 'affiliation'       : proposal.pi.affiliation
                  , 'domestic'          : proposal.pi.domestic
                  , 'new_user'          : proposal.pi.new_user
                  , 'email'             : 'bar@foo.com'
                  , 'telephone'         : proposal.pi.telephone
                  , 'last_name'         : proposal.pi.last_name
                  , 'first_name'        : proposal.pi.first_name
                  , 'thesis_observing'  : proposal.pi.thesis_observing
                  , 'oldauthor_id'      : proposal.pi.oldauthor_id
                  , 'storage_order'     : proposal.pi.storage_order
                  , 'support_requester' : proposal.pi.support_requester
                  , 'supported'         : proposal.pi.supported
                  , 'budget'            : proposal.pi.budget
                  }
        response = self.client.put('/pht/proposals/%s/authors/%s' % (proposal.pcode, proposal.pi.id)
                                 , json.dumps(data)
                                 , content_type='application/json')
        self.failUnlessEqual(response.status_code, 200)
        author = Author.objects.get(id = proposal.pi.id)
        self.assertEqual(author.email, data['email'])

    def test_delete(self):
        proposal = Proposal.objects.all()[0]
        response = self.client.delete('/pht/authors/%s' % proposal.pi.id)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(len(Author.objects.filter(id = proposal.pi.id)) == 0)
