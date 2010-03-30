import urllib

from settings                 import PROXY_PORT

class ScorePeriod(object):

    def __init__(self):
        if PROXY_PORT != 0:
            self.url = "http://trent.gb.nrao.edu:%d/score" % PROXY_PORT
        else:
            self.url = None

    def run(self, periodId):
        # Make unit tests run faster for Mike!
        if self.url is None:
            return
        params = urllib.urlencode({'id': periodId})
        try:
            f = urllib.urlopen(self.url, params)
        except IOError:
            print "IOError service", self.url
        else:
            f.read()
