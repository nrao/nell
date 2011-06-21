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
from datetime            import datetime, date

from test_utils              import BenchTestCase, timeIt
from scheduler.httpadapters   import *
from scheduler.models         import *
from scheduler.tests.utils    import *

class TestWindowResource(BenchTestCase):

    def setUp(self):
        super(TestWindowResource, self).setUp()
        self.client = Client()
        self.sesshun = create_sesshun()
        dt = datetime(2010, 1, 1, 12, 15)
        pending = Period_State.objects.get(abbreviation = "P")
        pa = Period_Accounting(scheduled = 0)
        pa.save()
        self.default_period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = pending
                                   , accounting = pa
                                   )
        self.default_period.save()                           
        p_adapter = PeriodHttpAdapter(self.default_period)
        pjson = p_adapter.jsondict('UTC', 1.1)
        self.fdata = {"session":  self.sesshun.id
                    #, "start":    "2010-01-01"
                    #, "duration": 7
                    , "num_periods": 0
                    }
        self.w = Window()
        w_adapter = WindowHttpAdapter(self.w)
        w_adapter.init_from_post(self.fdata)

        # go through the back door to set the range
        wr = WindowRange(window = self.w
                       , start_date = date(2010, 1, 1)
                       , duration = 7
                        )
        wr.save()                

    def tearDown(self):
        super(TestWindowResource, self).tearDown()

        # cleanup
        self.w.delete()
        self.default_period.delete()
        self.sesshun.delete()

    @timeIt
    def test_create(self):
        response = self.client.post('/scheduler/windows', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_empty(self):
        response = self.client.post('/scheduler/windows')
        self.failUnlessEqual(response.status_code, 200)

    def test_read_one(self):
        response = self.client.get('/scheduler/windows/%d' % self.w.id)
        self.failUnlessEqual(response.status_code, 200)

        self.assertTrue('"end": "2010-01-07"' in response.content)

    def test_read_filter(self):
        response = self.client.get('/scheduler/windows'
                                , {'filterSession' : self.sesshun.name})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1}' in response.content)

        response = self.client.get('/scheduler/windows'
                                , {'filterSession' : "not_there"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('{"windows": [], "total": 0}' in response.content)

        #YYYY-MM-DD hh:mm:ss
        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 30})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)

        # make sure we catch overlaps
        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2010-01-07' # 00:00:00' 
                                 , 'filterDuration' : 30})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)

        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2011-05-25' # 00:00:00' 
                                 , 'filterDuration' : 30})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('{"windows": [], "total": 0}' in response.content)

    def test_read_filter_2(self):

        #YYYY-MM-DD hh:mm:ss
        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 120})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1' in response.content)
 
        # now add multiple ranges
        wr = WindowRange(window = self.w
                       , start_date = datetime(2010, 3, 1)
                       , duration = 7)
        wr.save()
        wr = WindowRange(window = self.w
                       , start_date = datetime(2010, 2, 1)
                       , duration = 7)
        wr.save()

        # test it
        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 120})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1' in response.content)

        # create a second window
        w2 = Window(session = self.sesshun
                  , total_time = 2.0
                  , complete = False)
        w2.save()
        wr = WindowRange(window = w2 
                       , start_date = date(2010, 4, 1)
                       , duration = 7
                        )
        wr.save()
        wr = WindowRange(window = w2 
                       , start_date = date(2010, 5, 1)
                       , duration = 7
                        )
        wr.save()
        
        # test it
        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 90})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1' in response.content)

        response = self.client.get('/scheduler/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 120})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-05-07"' in response.content)
        self.assertTrue('"total": 2' in response.content)

    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('/scheduler/windows/%s' % self.w.id, fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('/scheduler/windows/%s' % self.w.id, {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)
        

