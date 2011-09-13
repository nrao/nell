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

from copy                      import copy
from django.test.client        import Client
from django.conf               import settings
from django.contrib.auth       import models as m

from test_utils                import BenchTestCase, timeIt
from scheduler.models          import *
from scheduler.httpadapters    import *
from scheduler.tests.utils     import create_sesshun, fdata
from users.utilities        import create_user
from users.GBTCalendarEvent import CalEventPeriod

class TestObserversBase(BenchTestCase):

    def setUp(self):
        super(TestObserversBase, self).setUp()

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

        # create a user to act as friend
        self.uFriend = User(first_name = "Best"
                          , last_name = "Friend"
                          , pst_id = None
                           )
        self.uFriend.save()
        self.uFriend.addRole("Staff")
        self.uFriend.addRole("Friend")

        # create a project
        self.p = Project()
        adapter = ProjectHttpAdapter(self.p)
        adapter.init_from_post({'semester'   : '09C'
                             , 'type'       : 'science'
                             , 'pcode'      : 'mike'
                             , 'name'       : 'mikes awesome project!'
                             , 'PSC_time'   : '100.0'
                             , 'total_time' : '100.0'
                             , 'sem_time'   : '50.0'
                               })

        # make the first user an investigator on this project
        i =  Investigator(project = self.p
                        , user    = self.u
                         )
        i.save()

        # assign the friend user to theis project
        self.friend = Friend(project = self.p
                 , user = self.uFriend)
        self.friend.save()

        # create a session for the project
        fdata2 = copy(fdata)
        fdata2.update({'source_v' : 1.0
                     , 'source_h' : 1.0
                     , 'source'   : 'testing'
                       })
        self.s = Sesshun()
        SessionHttpAdapter(self.s).init_from_post(fdata2)
        self.s.project = self.p
        self.s.save()

    def tearDown(self):
        super(TestObserversBase, self).tearDown()

    def get(self, url, data = {}):
        """
        Sets the USER extra kwar
        """
        return self.client.get(url, data, USER = self.auth_user.username)

    def post(self, url, data = {}):
        """
        Sets the USER extra kwar
        """
        return self.client.post(url, data, USER = self.auth_user.username)
