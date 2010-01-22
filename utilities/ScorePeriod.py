import urllib

from settings                 import PROXY_PORT

class ScorePeriod(object):

    def __init__(self):
        self.url = "http://trent.gb.nrao.edu:%d/score" % PROXY_PORT

    def run(self, periodId):
        params = urllib.urlencode({'id': periodId})
        try:
            f = urllib.urlopen(self.url, params)
        except IOError:
            print "IOError service", self.url
        else:
            f.read()
