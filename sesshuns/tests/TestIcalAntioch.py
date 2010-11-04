from test_utils.NellTestCase import NellTestCase
from nell.tools              import IcalAntioch

class TestIcalAntioch(NellTestCase):

    def testWriteSchedule(self):
        #ic = IcalAntioch.IcalAntioch(None, None)
        ic = IcalAntioch(None, None)
        pStr = "Period: 18 (0)  at 2006-02-01 00:00:00 for 420 (420) with score of 3.669943 from 2006-02-01 00:00:00 Scheduled  band: X  RA: 4.674547 grade: 4.0"
        dct = ic.parsePeriod(pStr)
        self.assertEquals('18', dct["sName"])
        self.assertEquals('X',  dct["band"])
        dct['id'] = 34
        event = ic.createEvent(dct)
        self.assertTrue(event is not None)

