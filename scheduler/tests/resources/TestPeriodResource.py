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

from django.test.client  import Client
from datetime                   import datetime, timedelta

from test_utils              import BenchTestCase, timeIt
from scheduler.tests.utils    import create_sesshun
from scheduler.models         import *
from scheduler.httpadapters   import *

class TestPeriodResource(BenchTestCase):

    def setUp(self):
        super(TestPeriodResource, self).setUp()
        self.rootURL = '/scheduler/periods'
        self.sess = create_sesshun()
        self.client = Client()
        self.fdata = {'session'  : self.sess.id
                    , 'date'    : '2009-06-01'
                    , 'time'    : '00:00'
                    , 'duration' : 1.0
                    , 'backup'   : True}
        self.p = Period()
        adapter = PeriodHttpAdapter(self.p)
        adapter.init_from_post(self.fdata, 'UTC')
        self.p.save()

    # Requires antioch server
    @timeIt
    def test_create(self):
        response = self.client.post(self.rootURL + '/UTC', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    # Requires antioch server
    @timeIt
    def test_create_empty(self):
        response = self.client.post(self.rootURL + '/ET')
        self.failUnlessEqual(response.status_code, 200)

    # Requires antioch server
    def test_read(self):
        url = "%s/%s?startPeriods=%s&daysPeriods=%d" % \
                            (self.rootURL 
                           , 'UTC'
                           , self.fdata['date'] + '%20' + self.fdata['time'] + ':00'
                           , 2)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 1')

    # Requires antioch server
    def test_read_keywords(self):
        # use a date range that picks up our one period
        url = "%s/%s?startPeriods=%s&daysPeriods=%d" % \
                            (self.rootURL 
                           , 'UTC'
                           , self.fdata['date'] + '%20' + self.fdata['time'] + ':00'
                           , 3)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 1')
        # now use a date range that doesn't
        url = "%s/%s?startPeriods=%s&daysPeriods=%d" % (
                                                     self.rootURL 
                                                   , 'UTC'
                                                   , '2009-06-02 00:00:00' 
                                                   , 3)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 0')

        # now don't use any keywords: filter should default
        # to today (circa 2010), so NO periods should be found.
        response = self.client.get("%s/UTC" % self.rootURL)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 0')

        # fail to find a period for an imaginary window
        url = "%s/UTC?filterWnd=1" % self.rootURL
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 0')

    def test_update_does_not_exist(self):
        response = self.client.post('/period/UTC/1000', {'_method' : 'put'})
        self.failUnlessEqual(response.status_code, 404)

    # If antioch server running requires it contain the appropriate periods
    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('%s/%s/%s' % (self.rootURL
                                                 ,'ET'
                                                 , self.p.id), fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('%s/%s/%s' % (self.rootURL
                                                , 'ET'
                                                , self.p.id)
                                  , {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)

    def test_windowed_period(self):
        
        # create a window
        #w = Window(start_date = self.p.start - timedelta(days = 10)
        #         , duration = 15
        w = Window(total_time = self.p.duration
                 , complete = True
                 , session = self.p.session
                  )
        w.save()
        wr = WindowRange(window = w
                       , start_date = self.p.start - timedelta(days = 10)
                       , duration = 15
                         )
        wr.save()

        self.p.window = w
        self.p.save()

        url = "%s/%s?filterWnd=%d" % (self.rootURL, 'UTC', w.id)
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(response.content[:11], '{"total": 1')

