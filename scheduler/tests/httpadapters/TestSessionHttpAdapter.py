from test_utils import NellTestCase
from scheduler.models import *
from scheduler.httpadapters import SessionHttpAdapter
from scheduler.tests.utils  import create_sesshun

class TestSessionHttpAdapter(NellTestCase):

    def setUp(self):
        super(TestSessionHttpAdapter, self).setUp()
        self.s       = create_sesshun()
        self.adapter = SessionHttpAdapter(self.s)

    def test_jsondict(self):

        json = self.adapter.jsondict()
        exp = {'req_max': 6.0
             , 'grade': 4.0
             , 'nighttime': False
             , 'transit': False
             , 'sem_time': 0.0
             , 'lst_in': ''
             , 'id': 1L
             , 'guaranteed': True
             , 'lst_ex': ''
             , 'source': u'test source'
             , 'pcode': u'GBT09A-001'
             , 'authorized': True
             , 'between': '0'
             , 'type': u'open'
             , 'req_min': 2.0
             , 'total_time': 3.0
             , 'coord_mode': u'J2000'
             , 'handle': u'Low Frequency With No RFI (GBT09A-001) 0'
             , 'complete': False
             , 'project_complete': 'No'
             , 'source_h': 1.0
             , 'source_v': 2.2999999999999998
             , 'trk_err_threshold': 0.20000000000000001
             , 'PSC_time': 2.0
             , 'freq': 6.0
             , 'name': 'Low Frequency With No RFI'
             , 'science': u'pulsar'
             , 'orig_ID': 0
             , 'enabled': True
             , 'remaining': 3.0
             , 'xi_factor': 1.0
             , 'receiver': ''
             , 'backup': False}
        self.assertEquals(exp, json)

    def test_udpate_tr_err_threshold_obs_param(self):

        # check inital state
        th = self.adapter.sesshun.get_tracking_error_threshold_param()
        self.assertEquals(None, th)
        th = self.adapter.sesshun.get_tracking_error_threshold()
        self.assertEquals(0.2, th)

        # no-op
        fdata = {}
        old_value = self.adapter.sesshun.get_tracking_error_threshold_param()
        self.adapter.update_tr_err_threshold_obs_param(fdata, old_value)
        th = self.adapter.sesshun.get_tracking_error_threshold()
        self.assertEquals(0.2, th)

        # add the new param
        fdata = {'trk_err_threshold' : 0.5}
        old_value = self.adapter.sesshun.get_tracking_error_threshold_param()
        self.adapter.update_tr_err_threshold_obs_param(fdata, old_value)
        th = self.adapter.sesshun.get_tracking_error_threshold()
        self.assertEquals(0.5, th)

        # change the param
        fdata = {'trk_err_threshold' : 0.6}
        old_value = self.adapter.sesshun.get_tracking_error_threshold_param()
        self.adapter.update_tr_err_threshold_obs_param(fdata, old_value)
        th = self.adapter.sesshun.get_tracking_error_threshold()
        self.assertAlmostEquals(0.6, th, 1)

    def test_udpate_source_size_obs_param(self):

        # check inital state
        old_value = self.adapter.sesshun.get_source_size()
        self.assertEquals(None, old_value)

        # no-op
        fdata = {}
        old_value = self.adapter.sesshun.get_source_size()
        self.adapter.update_source_size_obs_param(fdata, old_value)
        new_value = self.adapter.sesshun.get_source_size()
        self.assertEquals(None, new_value)

        # add the new param
        fdata = {'src_size' : 500.0}
        old_value = self.adapter.sesshun.get_source_size()
        self.adapter.update_source_size_obs_param(fdata, old_value)
        new_value = self.adapter.sesshun.get_source_size()
        self.assertEquals(500.0, new_value)

        # change the param
        fdata = {'src_size' : 600.0}
        old_value = self.adapter.sesshun.get_source_size()
        self.adapter.update_source_size_obs_param(fdata, old_value)
        new_value = self.adapter.sesshun.get_source_size()
        self.assertEquals(600.0, new_value)

    def test_update_lst_parameters(self):
        error = False
        try:
            self.adapter.update_lst_parameters('lst_ex', '14.0-10')
        except NameError:
            error = True
        self.assertTrue(error)

        try:
            self.adapter.update_lst_parameters('lst_ex', '2.0 - 8.0, 4.0 - 10.0')
        except NameError:
            error = True
        self.assertTrue(error)

        self.adapter.update_lst_parameters('lst_ex', '4.0-10')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [], 'LST Exclude': [[4.0, 10.0]]}, results)

        self.adapter.update_lst_parameters('lst_ex', '2.0 - 8.5, 22.0 - 24.0')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [], 'LST Exclude': [[2.0, 8.5], [22.0, 24.0]]}, results)

        self.adapter.update_lst_parameters('lst_in', '0.0 - 2.0')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [[0.0, 2.0]], 'LST Exclude': [[2.0, 8.5], [22.0, 24.0]]}
                       , results)

        self.adapter.update_lst_parameters('lst_in', '4.0 - 8.0, 12.0 - 18.0')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [[4.0, 8.0], [12.0, 18.0]]
                        , 'LST Exclude': [[2.0, 8.5], [22.0, 24.0]]}
                       , results)

        self.adapter.update_lst_parameters('lst_ex', '')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [[4.0, 8.0], [12.0, 18.0]]
                        , 'LST Exclude': []}
                       , results)
        
        self.adapter.update_lst_parameters('lst_in', '')
        results = self.s.get_lst_parameters()
        self.assertEqual({'LST Include': [], 'LST Exclude': []}, results)
