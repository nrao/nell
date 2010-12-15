from django.test.client  import Client
import unittest

class TestViews(unittest.TestCase):

    def test_initiateHardware(self):
        c        = Client()
        response = c.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)

    def test_setHardware(self):
        c  = Client()
        selected = {'mode': 1}
        response = c.post('/calculator/set_hardware', selected)
        self.failUnlessEqual(response.status_code, 200)

    def test_reset(self):
        c = Client()
        response = c.get('/calculator/reset')
        self.failUnlessEqual(response.status_code, 200)

    def test_set_terms(self):
        c = Client()
        data = {'receiver-hidden'    : ['K2']
              , 'beams-hidden'       : ['1']
              , 'switching-hidden'   : ['BSW-NOD']
              , 'bandwidth-hidden'   : ['8']
              , 'integration-hidden' : ['NA']
              , 'polarization-hidden': ['NA']
              , 'backend-hidden'     : ['Mark V']
              , 'switching'          : ['BSW-NOD']
              , 'windows'            : ['CF:1']
              , 'windows-hidden'     : ['CF:1']
              , 'receiver'           : ['K2']
              , 'mode-hidden'        : ['HTR']
              , 'backend'            : ['Mark V']
              }
        response = c.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)

        data = {u'receiver-hidden': [u'L'], u'beams-hidden': [u'1'], u'switching-hidden': [u'TP'], u'bandwidth-hidden': [u'0.625'], u'integration-hidden': [u'1.00'], u'polarization-hidden': [u'(I,Q,U,V)'], u'backend-hidden': [u'SP'], u'windows-hidden': [u'RF:1'], u'switching': [u'TP'], u'polarization': [u'(I,Q,U,V)'], u'windows': [u'RF:1'], u'bandwidth': [u'0.625'], u'mode': [u'Spectral Line'], u'receiver': [u'L'], u'mode-hidden': [u'Spectral Line'], u'backend': [u'SP']}
        response = c.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)

    def test_get_result(self):
        c = Client()
        response = c.get('/calculator/initiate_hardware')
        data = {u'receiver-hidden': [u'L'], u'beams-hidden': [u'1'], u'switching-hidden': [u'TP'], u'bandwidth-hidden': [u'0.625'], u'integration-hidden': [u'1.00'], u'polarization-hidden': [u'(I,Q,U,V)'], u'backend-hidden': [u'SP'], u'windows-hidden': [u'RF:1'], u'switching': [u'TP'], u'polarization': [u'(I,Q,U,V)'], u'windows': [u'RF:1'], u'bandwidth': [u'0.625'], u'mode': [u'Spectral Line'], u'receiver': [u'L'], u'mode-hidden': [u'Spectral Line'], u'backend': [u'SP']}
        response = c.post('/calculator/set_terms/', data)
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)

    def test_spectral_line_mode(self):
        c = Client()
        response = c.get('/calculator/initiate_hardware')
        data = {'receiver': ['L']
              , 'beams-hidden': [u'1']
              , 'switching-hidden': [u'TP']
              , 'bandwidth-hidden': [u'0.625']
              , 'integration-hidden': [u'1.00']
              , 'polarization-hidden': [u'(I,Q,U,V)']
              , 'backend-hidden': [u'SP']
              , 'windows': [u'1']
              , 'switching': [u'TP']
              , 'polarization': [u'(I,Q,U,V)']
              , 'bandwidth': [u'0.625']
              , 'mode': [u'Spectral Line']
              , 'receiver': [u'L']
              , 'mode-hidden': [u'Spectral Line']
              , 'backend': [u'Spectral Processor']
              }
        response = c.post('/calculator/set_terms/', data)
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace("null", "None"))
        self.assertEqual(results['min_topo_freq']
             , [0.6103515625, 'kHz', 'getMinTopoFreq(backend, bandwidth, windows) if mode.lower() == "spectral line" else ""'])

        response = c.post('/calculator/set_terms/', {'mode' : 'DCR'})
        response = c.get('/calculator/get_result/')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace("null", "None"))
        self.assertEqual(results['min_topo_freq']
             , [None, 'kHz', 'getMinTopoFreq(backend, bandwidth, windows) if mode.lower() == "spectral line" else ""'])

