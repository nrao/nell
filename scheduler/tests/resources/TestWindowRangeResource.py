from django.test.client  import Client

from test_utils              import BenchTestCase, timeIt
from scheduler.httpadapters   import *
from scheduler.models         import *
from scheduler.tests.utils    import *

class TestWindowRangeResource(BenchTestCase):

    def setUp(self):
        super(TestWindowRangeResource, self).setUp()
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
        fdata = {"session":  self.sesshun.id
               , "num_periods": 0
                }
        self.w = Window()
        w_adapter = WindowHttpAdapter(self.w)
        w_adapter.init_from_post(fdata)

        # go through the back door to set the range
        startDt = date(2010, 1, 1)
        duration = 7
        self.fdata = {"window_id" : self.w.id
                    , "start" : startDt
                    , "duration" : duration }
        self.wr = WindowRange(window = self.w
                            , start_date = date(2010, 1, 1)
                            , duration = 7
                             )
        self.wr.save()                

    @timeIt
    def test_create(self):
        response = self.client.post('/windowRanges', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_create_empty(self):
        response = self.client.post('/windowRanges')
        self.failUnlessEqual(response.status_code, 200)

    def test_read_one(self):
        response = self.client.get('/windowRanges/%d' % self.wr.id)
        self.failUnlessEqual(response.status_code, 200)

        self.assertTrue('"end": "2010-01-07"' in response.content)

    def test_read_filter(self):
        response = self.client.get('/windowRanges'
                                , {'filterWindowId' : self.w.id})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"end": "2010-01-07"' in response.content)
        self.assertTrue('"total": 1' in response.content)

        response = self.client.get('/windowRanges'
                                , {'filterWindowId' : "666"})
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('"total": 0' in response.content)

    @timeIt
    def test_update(self):
        fdata = self.fdata
        fdata.update({"_method" : "put"})
        response = self.client.post('/windowRanges/%s' % self.wr.id, fdata)
        self.failUnlessEqual(response.status_code, 200)

    @timeIt
    def test_delete(self):
        response = self.client.post('/windowRanges/%s' % self.wr.id, {"_method" : "delete"})
        self.failUnlessEqual(response.status_code, 200)

