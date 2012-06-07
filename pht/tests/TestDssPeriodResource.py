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
from datetime            import datetime
import math

from scheduler.models       import *
from scheduler.tests.utils  import create_sesshun
from scheduler.httpadapters import PeriodHttpAdapter
from pht.httpadapters       import DssPeriodHttpAdapter

class TestDssPeriodResource(TestCase):
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

        self.sess  = create_sesshun()
        self.fdata = {'session'  : self.sess.id
                    , 'date'    : '2009-06-01'
                    , 'time'    : '00:00'
                    , 'duration' : 1.0
                    , 'backup'   : True}

        # create the dss period            
        self.period  = Period()
        adapter = PeriodHttpAdapter(self.period)
        adapter.init_from_post(self.fdata, 'UTC')
        self.period.save()

    def eval_response(self, response_content):
        "Makes sure we can turn the json string returned into a python dict"
        return eval(response_content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))

    def test_get(self):
        response = self.client.get("/pht/dss/periods/UTC/%d" % self.period.id)
        results = self.eval_response(response.content)

        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(self.period.session.observing_type.type, results['session']['science'])
        self.assertEqual(self.period.session.session_type.type, results['session']['type'])
        self.assertEqual(self.period.duration, results['duration'])
        self.assertEqual(self.fdata['date'], results['date'])
        self.assertEqual(self.fdata['time'], results['time'])


        
