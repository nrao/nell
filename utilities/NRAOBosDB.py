import urllib2
import lxml.etree    as ET
from sesshuns.models import *
from datetime        import datetime

class NRAOBosDB:

    """
    This class is responsible for getting info from the BOS 
    query services.  Thankfully, there is no security to get around.
    """

    def __init__(self):

        self.opener = urllib2.build_opener()

        #baseUrl ='https://bostest.cv.nrao.edu/resReports/reservationsByPerson/'
        self.baseUrlByPerson = \
            'https://bos.nrao.edu/resReports/reservationsByPerson/'

    def getReservationsByUsername(self, username):
        "Uses BOS query service to return list of reservations for username."

        url = self.baseUrlByPerson + username
        fh = self.opener.open(url)
        str = fh.read(0x4000)
        return self.parseReservationsXML(str)

    def parseReservationsXML(self, str):
        "Parses XML returned by reservationsByPerson query."

        data = ET.fromstring(str)
        reservations = []
        for i in range(len(data)):
            # TBF: why can't I use self.findTag?
            dates = data[i].getchildren()
            assert 'startDate' in dates[0].tag
            start = self.str2dt(dates[0].text)
            end   = self.str2dt(dates[1].text)
            reservations.append((start, end))
        return reservations

    def _testSystem(self):
        "for testing purposes."
        users = User.objects.all()

        for u in users:
            if u.username is None:
                continue
            print u, u.username
            url = self.baseUrlByPerson + u.username
        
            # no security!  Ha Ha!
            try:
                fh = self.opener.open(url)
            except:
                print "exception for user, username: ", u, u.username
                continue
            str = fh.read(0x4000)
            data = ET.fromstring(str)
            #print data
            if len(data) > 0:
                print "found a reservation!"
                print len(data)
                print data
                print str

    def str2dt(self, str):
        "YYYY-MM-DD -> DateTime"
        return datetime.strptime(str, "%Y-%m-%d")

    def findTag(self, node, tag):
        value = None
        value_tag = node.find(tag)
        if value_tag is not None:
            value = value_tag.text
        return value  

