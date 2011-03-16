from django.test.client  import Client

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
        pending = first(Period_State.objects.filter(abbreviation = "P"))
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
        response = self.client.post('/windows', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_empty(self):
        response = self.client.post('/windows')
        self.failUnlessEqual(response.status_code, 200)

    def test_read_one(self):
        response = self.client.get('/windows/%d' % self.w.id)
        self.failUnlessEqual(response.status_code, 200)

        self.assertTrue('"end": "2010-01-07"' in response.content)

    def test_read_filter(self):
        response = self.client.get('/windows'
                                , {'filterSession' : self.sesshun.name})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1}' in response.content)

        response = self.client.get('/windows'
                                , {'filterSession' : "not_there"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('{"windows": [], "total": 0}' in response.content)

        #YYYY-MM-DD hh:mm:ss
        response = self.client.get('/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 30})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)

        # make sure we catch overlaps
        response = self.client.get('/windows'
                                , {'filterStartDate' : '2010-01-07' # 00:00:00' 
                                 , 'filterDuration' : 30})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)

        response = self.client.get('/windows'
                                , {'filterStartDate' : '2011-05-25' # 00:00:00' 
                                 , 'filterDuration' : 30})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('{"windows": [], "total": 0}' in response.content)

    def test_read_filter_2(self):

        #YYYY-MM-DD hh:mm:ss
        response = self.client.get('/windows'
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
        response = self.client.get('/windows'
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
        response = self.client.get('/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 90})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1' in response.content)

        response = self.client.get('/windows'
                                , {'filterStartDate' : '2009-12-25' # 00:00:00' 
                                 , 'filterDuration' : 120})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-05-07"' in response.content)
        self.assertTrue('"total": 2' in response.content)

    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('/windows/%s' % self.w.id, fdata)
        self.failUnlessEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('/windows/%s' % self.w.id, {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)
        

