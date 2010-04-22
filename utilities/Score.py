from settings                 import PROXY_PORT, ANTIOCH_HOST
import TimeAgent
import urllib
import simplejson as json
import time
from Borg import Borg

class Score(Borg):
    _shared_state = {}

    def __init__(self):
        self.clear()
        self.url = "%s:%d/score" % (ANTIOCH_HOST, PROXY_PORT)

    def clear(self):
        self.scores = {}
        self.time = time.time()

    def periods(self, periodIds):
        """
        Given a list of period ids, returns a dictionary with the
        ids as keys and the values the associated scores.
        """
        new_time = time.time()
        if new_time - self.time > 5*60:
            self.clear()
        # sets
        available = set(self.scores.keys())
        need = set(periodIds)
        get = need - available
        have = need & available
        # dictionaries
        new_scores = self.get_scores(list(get))
        self.scores.update(new_scores)
        for k in have:
            new_scores[k] = self.scores[k]
        return new_scores

    def session(self, sessionId, start, durHrs):
        """
        Given a session id, a start time, and duration
        returns its score.
        """
        self.clear()
        params = urllib.urlencode(dict(sid      = sessionId
                                     , start    = TimeAgent.quarter(start)
                                     , duration = int(round(4.0*durHrs))*15))
        url = "".join([self.url, "/session?", params])
        try:
            f = urllib.urlopen(url)
            asstr = f.read()
            retval = float(json.loads(asstr)['score'])
        except IOError:
            print "IOError service", url
            return 0.0
        except ValueError:
            print "ValueError - is antioch running?"
            return 0.0
        else:
            return retval

    def get_scores(self, periodIds):
        if not periodIds:
            return {}
        pdict = "&pids=".join(map(str, periodIds))
        url = "".join([self.url, "/periods?pids=", pdict])
        try:
            f = urllib.urlopen(url)
            asstr = f.read()
            results = json.loads(asstr)['scores']
            retval = {}
            for d in results:
                retval[d['pid']] = d['score']
        except IOError:
            print "IOError service", url
            return {}
        except ValueError:
            print "ValueError - is antioch running?"
            self.clear()
            return {}
        else:
            return retval

