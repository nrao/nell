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

from TestViewsBase       import TestViewsBase

class TestViews(TestViewsBase):

    def test_initiateHardware(self):
        response = self.client.get('/calculator/initiate_hardware')
        self.failUnlessEqual(response.status_code, 200)

    def test_setHardware(self):
        selected = {'mode': 1}
        response = self.client.post('/calculator/set_hardware', selected)
        self.failUnlessEqual(response.status_code, 200)

    def test_set_terms(self):
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
        response = self.client.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)

        data = {u'receiver-hidden': [u'L'], u'beams-hidden': [u'1'], u'switching-hidden': [u'TP'], u'bandwidth-hidden': [u'0.625'], u'integration-hidden': [u'1.00'], u'polarization-hidden': [u'(I,Q,U,V)'], u'backend-hidden': [u'SP'], u'windows-hidden': [u'RF:1'], u'switching': [u'TP'], u'polarization': [u'(I,Q,U,V)'], u'windows': [u'RF:1'], u'bandwidth': [u'0.625'], u'mode': [u'Spectral Line'], u'receiver': [u'L'], u'mode-hidden': [u'Spectral Line'], u'backend': [u'SP']}
        response = self.client.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)

    def test_get_result(self):
        response = self.client.get('/calculator/initiate_hardware')
        data = {u'receiver-hidden': [u'L'], u'beams-hidden': [u'1'], u'switching-hidden': [u'TP'], u'bandwidth-hidden': [u'0.625'], u'integration-hidden': [u'1.00'], u'polarization-hidden': [u'(I,Q,U,V)'], u'backend-hidden': [u'SP'], u'windows-hidden': [u'RF:1'], u'switching': [u'TP'], u'polarization': [u'(I,Q,U,V)'], u'windows': [u'RF:1'], u'bandwidth': [u'0.625'], u'mode': [u'Spectral Line'], u'receiver': [u'L'], u'mode-hidden': [u'Spectral Line'], u'backend': [u'SP']}
        response = self.client.post('/calculator/set_terms/', data)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)

    def test_vegas(self):
        response = self.client.get('/calculator/initiate_hardware')
        data = {'receiver': ['L']
              , 'beams-hidden': [u'1']
              , 'switching-hidden': [u'TP']
              , 'bandwidth-hidden': [u'1500']
              , 'integration-hidden': [u'1.00']
              , 'polarization-hidden': [u'(I,Q,U,V)']
              , 'backend-hidden': [u'SP']
              , 'windows': [u'1']
              , 'switching': [u'TP']
              , 'polarization': [u'(I,Q,U,V)']
              , 'bandwidth': [u'1500']
              , 'mode': [u'Spectral Line']
              , 'receiver': [u'L']
              , 'mode-hidden': [u'Spectral Line']
              , 'backend': [u'FPGA Spectrometer']
              }
        response = self.client.post('/calculator/set_terms/', data)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace("null", "None"))
        mtf     = [r for r in results['results'] if r['term'] == 'min_topo_freq']
        self.assertAlmostEqual(mtf[0]['value'], 1464.844, 3)

    def test_vegas2(self):
        response = self.client.get('/calculator/initiate_hardware')
        data = {'receiver': ['L']
              , 'beams-hidden': [u'1']
              , 'switching-hidden': [u'TP']
              , 'bandwidth-hidden': [u'5']
              , 'integration-hidden': [u'1.00']
              , 'polarization-hidden': [u'(I,Q,U,V)']
              , 'backend-hidden': [u'SP']
              , 'windows': [u'8']
              , 'switching': [u'TP']
              , 'polarization': [u'(I,Q,U,V)']
              , 'bandwidth': [u'5']
              , 'mode': [u'Spectral Line']
              , 'receiver': [u'L']
              , 'mode-hidden': [u'Spectral Line']
              , 'backend': [u'FPGA Spectrometer']
              }
        response = self.client.post('/calculator/set_terms/', data)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace("null", "None"))
        mtf     = [r for r in results['results'] if r['term'] == 'min_topo_freq']
        self.assertAlmostEqual(mtf[0]['value'], 1.221, 3)

    def test_spectral_line_mode(self):
        response = self.client.get('/calculator/initiate_hardware')
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
        response = self.client.post('/calculator/set_terms/', data)
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace("null", "None"))
        mtf     = [r for r in results['results'] if r['term'] == 'min_topo_freq']
        self.assertAlmostEqual(mtf[0]['value'], 0.610, 3)

        response = self.client.post('/calculator/set_terms/', {'mode' : 'DCR'})
        response = self.client.get('/calculator/get_results')
        self.failUnlessEqual(response.status_code, 200)
        results = eval(response.content.replace("null", "None"))
        mtf     = [r for r in results['results'] if r['term'] == 'min_topo_freq']
        self.assertEqual(mtf[0]['value'], '')

    def test_results(self):
        response = self.client.get('/calculator/initiate_hardware')

        # General Information
        data = {'units': [u'tr']
              , 'conversion': [u'Sensitivity to Time']
              , 'sensitivity': [u'1']
              , 'semester': [u'A']
              , 'time': [u'1']
              }
        response = self.client.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/results')
        self.failUnlessEqual(response.status_code, 200)

        # Hardware Information
        data = {'receiver-hidden': [u'L (1.15 - 1.73 GHz)']
              , 'beams-hidden': [u'1']
              , 'switching-hidden': [u'In-Band Frequency Switching']
              , 'bandwidth-hidden': [u'12.5']
              , 'polarization-hidden': [u'Dual']
              , 'backend-hidden': [u'GBT Spectrometer']
              , 'windows-hidden': [u'1']
              , 'switching': [u'In-Band Frequency Switching']
              , 'polarization': [u'Dual']
              , 'windows': [u'1']
              , 'bandwidth': [u'12.5']
              , 'receiver': [u'L (1.15 - 1.73 GHz)']
              , 'mode-hidden': [u'Spectral Line']
              , 'backend': [u'GBT Spectrometer']
              }
        response = self.client.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/results')
        self.failUnlessEqual(response.status_code, 200)

        # Source Information
        data = {'doppler': [u'Optical']
              , 'galactic': [u'no_correction']
              , 'redshift': [u'0']
              , 'frame': [u'Rest Frame']
              , 'source_diameter_slider': [u'0']
              , 'right_ascension': [u'']
              , 'rest_freq': [u'1440.0']
              , 'source_velocity': [u'0']
              , 'declination': [u'38']
              , 'estimated_continuum': [u'0']
              , 'topocentric_freq': [u'1440.0']
              , 'doppler-hidden': [u'Optical']
              }
        response = self.client.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/results')
        self.failUnlessEqual(response.status_code, 200)

        # Data Reduction Information
        data = {'smoothing_resolution': [u'1']
              , 'diff_signal': [u'true']
              , 'smoothing': [u'velocity_resolution_rest']
              , 'r_sig_ref': [u'1']
              , 'bw': [u'0.004803322970701629']
              , 'smoothing_factor': [u'1']
              , 'avg_pol': [u'true']
              , 'no_avg_ref': [u'1']
              }
        response = self.client.post('/calculator/set_terms/', data)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get('/calculator/results')
        self.failUnlessEqual(response.status_code, 200)
