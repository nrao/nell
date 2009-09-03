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

    def reservations(self, project):
        """
        Constructs a dictionary mapping the project's users to lists of
        reservations, where a reservation is a binary tuple of datetimes
        representing the check-in and check-out dates.
        """
        retval = dict()
        for i in project.investigator_set.all():
            if not i.friend:
                u = i.user
                rs = self.getReservationsByUsername(u.username)
                if rs:
                    retval[u] = rs
        return retval

    def jsondict(self, project, id):
        """
        Take a Project and a starting id and returns a list of json
        dictionaries representing each reservation.  The keys of the json
        dictionary are: id, title, start, end.
        """
        jsonobjlist = []
        for user, reservations in self.reservations(project):
            for start, end in reservations:
                jsonobjlist.extend({
                    "id"   : id
                  , "title": user.name + ": reservation"
                  , "start": start
                  , "end"  : end
                })
        return jsonobjlist, id
 
    def getReservationsByUsername(self, username):
        """
        Uses BOS query service to return list of reservations for
        username, where a reservation is a binary tuple of datetimes
        representing the check-in and check-out dates.
        """
        if username is None:
            print "Error: getReservationsByUsername username arg is None"
            return []
        url = self.baseUrlByPerson + username
        fh = self.opener.open(url)
        str = fh.read(0x4000)
        parsed = self.parseReservationsXML(str)
        return parsed

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

    def str2dt(self, str):
        "YYYY-MM-DD -> DateTime"
        return datetime.strptime(str, "%Y-%m-%d")

    def findTag(self, node, tag):
        value = None
        value_tag = node.find(tag)
        if value_tag is not None:
            value = value_tag.text
        return value  

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


