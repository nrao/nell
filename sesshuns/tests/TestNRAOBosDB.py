from datetime import datetime
import lxml.etree as et

from test_utils              import NellTestCase
from nell.utilities.database.external          import NRAOBosDB

class TestNRAOBosDB(NellTestCase):

    def setUp(self):
        super(TestNRAOBosDB, self).setUp()

        self.bos = NRAOBosDB()

        #<?xml version="1.0" encoding="utf-8"?>
        self.xmlStr =  """
        <nrao:user domestic="true" id="dbalser" xmlns:nrao="http://www.nrao.edu/namespaces/nrao">
            <nrao:reservation id="2704">
                <nrao:startDate>2009-08-25</nrao:startDate>
                <nrao:endDate>2009-08-28</nrao:endDate>
            </nrao:reservation>
        </nrao:user>
        """
        self.xml = et.fromstring(self.xmlStr)

        self.xmlStr2 = """
        <nrao:reservations domestic="true" xmlns:nrao="http://www.nrao.edu/namespaces/nrao">
            <nrao:reservation id="3407">
                <nrao:user id="1">Mike McCarty</nrao:user>
                <nrao:startDate>2010-07-19</nrao:startDate>
                <nrao:endDate>2010-07-25</nrao:endDate>
            </nrao:reservation>
        </nrao:reservations>
        """
        self.xml2 = et.fromstring(self.xmlStr)

    def test_parseReservationsXML(self):

        dates = self.bos.parseReservationsXML(self.xmlStr)
        exp = [(datetime(2009, 8, 25, 0, 0), datetime(2009, 8, 28, 0, 0))]
        self.assertEqual(dates, exp)

    def test_parseReservationsDateRangeXML(self):

        dates = self.bos.parseReservationsDateRangeXML(self.xmlStr2)
        exp = [('1', 'Mike McCarty', datetime(2010, 7, 19, 0, 0), datetime(2010, 7, 25, 0, 0))]
        self.assertEqual(dates, exp)

