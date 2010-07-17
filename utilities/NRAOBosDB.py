import urllib2
import lxml.etree        as ET
from datetime            import datetime
from django.core.cache   import cache

class NRAOBosDB:

    """
    This class is responsible for getting info from the BOS 
    query services.  Thankfully, there is no security to get around.
    """

    def __init__(self):

        self.opener = urllib2.build_opener()

        # we must use bostest.cv.nrao.edu because bos.nrao.edu
        # knows nothing about PST users
        #baseUrl ='https://bostest.cv.nrao.edu/resReports/reservationsByPerson/'
        self.baseUrlByPerson = \
            'https://bos.nrao.edu/resReports/reservationsByPerson/'
        #    'https://bost#est.cv.nrao.edu/resReports/reservationsByPerson/'
        self.baseUrl= \
            'https://bos.nrao.edu/resReports/reservations'

    def reservations(self, project, use_cache = True):
        """
        Constructs a dictionary mapping the project's users to lists of
        reservations, where a reservation is a binary tuple of datetimes
        representing the check-in and check-out dates.
        """
        retval = dict()
        for i in project.investigator_set.all():
            u = i.user
            rs = self.getReservationsByUsername(u.username, use_cache)
            if rs:
                retval[u] = rs
        return retval

    def reservationsRange(self, start, end):
        return [{'name'  : u
               , 'start' : s.strftime("%m/%d/%Y")
               , 'end'   : e.strftime("%m/%d/%Y")} for u, s, e in self.getReservationsByDateRange(start, end)]

    def eventjson(self, project, id, tz = None):
        """
        Take a Project and a starting id and returns a list of json
        dictionaries representing each reservation.  The keys of the json
        dictionary are: id, title, start, end.
        """
        jsonobjlist = []
        for user, reservations in self.reservations(project).items():
            for start, end in reservations:
                jsonobjlist.append({
                    "id"       : id
                  , "title"    : "".join([user.name(), " in Green Bank"])
                  , "start"    : start.isoformat()
                  , "end"      : end.isoformat()
                  , "className": 'reservation'
                })
                id = id + 1
        return jsonobjlist, id
 
    def getReservationsByDateRange(self, start, end):
        """
        Uses BOS query service to return list of reservations for
        a specified date range, where a reservation is a binary tuple of datetimes
        representing the check-in and check-out dates.
        """
        if start is None or end is None:
            return []

        url = self.baseUrl + '?sdate=%s&edate=%s' % (start, end)
        print url
        try:
            fh           = self.opener.open(url)
            reservations = self.parseReservationsDateRangeXML(fh.read(0x4000))
        except:
            reservations = []
        return reservations


    def getReservationsByUsername(self, username, use_cache = True):
        """
        Uses BOS query service to return list of reservations for
        username, where a reservation is a binary tuple of datetimes
        representing the check-in and check-out dates.
        """
        if username is None:
            #print "Error: getReservationsByUsername username arg is None"
            return []

        if not use_cache or cache.get(username) is None:
            url          = self.baseUrlByPerson + username
            try:
                fh           = self.opener.open(url)
                reservations = self.parseReservationsXML(fh.read(0x4000))
            except:
                reservations = []

            if cache.get(username) is None:
                cache.add(username, reservations)
            else:
                cache.set(username, reservations)
        else:
            reservations = cache.get(username)

        return reservations

    def parseReservationsDateRangeXML(self, str):
        "Parses XML returned by reservations query."
        data = ET.fromstring(str)
        reservations = []
        for i in range(len(data)):
            # TBF: why can't I use self.findTag?
            res = data[i].getchildren()
            assert 'startDate' in res[1].tag
            name  = res[0].text
            start = self.str2dt(res[1].text)
            end   = self.str2dt(res[2].text)
            reservations.append((name, start, end))
        return reservations

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
