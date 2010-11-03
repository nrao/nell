from django.test.client  import Client

from test_utils.NellTestCase import NellTestCase
from utils                   import create_sesshun
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestPeriodResource(NellTestCase):

    def setUp(self):
        super(TestPeriodResource, self).setUp()
        self.rootURL = '/periods'
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
    def test_create(self):
        response = self.client.post(self.rootURL + '/UTC', self.fdata)
        self.failUnlessEqual(response.status_code, 200)

    # Requires antioch server
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


    # If antioch server running requires it contain the appropriate periods
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

