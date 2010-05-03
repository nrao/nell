from datetime               import datetime
from PeriodHttpAdapter      import PeriodHttpAdapter
from SessionHttpAdapter     import SessionHttpAdapter
from sesshuns.models        import Period, Sesshun
from sesshuns.models.common import *

class WindowHttpAdapter (object):

    def __init__(self, window):
        self.window = window

    def load(self, window):
        self.window = window

    def jsondict(self):
        js = {  "id"             : self.window.id
              , "handle"         : self.window.toHandle()
              , "session"        : SessionHttpAdapter(self.window.session).jsondict()
              , "start"          : self.window.start_date.strftime("%Y-%m-%d")
              , "end"            : self.window.end().strftime("%Y-%m-%d")
              , "duration"       : self.window.duration
              }
        # we need to do this so that the window explorer can work with
        # a 'flat' json dictionary
        self.add_period_json(js, "default", self.window.default_period)
        self.add_period_json(js, "choosen", self.window.period)
        return js    

    def init_from_post(self, fdata):
        self.from_post(fdata)

    def update_from_post(self, fdata):
        self.from_post(fdata)

    def from_post(self, fdata):

        # most likely, we'll be specifying sessions for windows in the same
        # manner as we do for periods
        handle = fdata.get("handle", "")
        if handle:
            self.window.session = self.window.handle2session(handle)
        else:
            try:
                maintenance = first(Project.objects.filter(pcode='Maintenance'))
                self.window.session = first(Sesshun.objects.filter(project=maintenance))
            except:
                self.window.session  = Sesshun.objects.get(id=fdata.get("session", 1))

         # get the date
        date = fdata.get("start", datetime.utcnow().strftime("%Y-%m-%d"))
        self.window.start_date = datetime.strptime(date, "%Y-%m-%d").date()

        # TBF: why is this going back and forth as a float?
        self.window.duration = int(float(fdata.get("duration", "1.0")))

        # we are working with a 'flat' dictionary that has only a few
        # of the specified fields for it's two periods.
        self.period_from_post(fdata, "default", self.window.session)
        self.period_from_post(fdata, "choosen", self.window.session)
       
        self.window.save()

    def add_period_json(self, jsondict, type, period):
        "Adss part of the given period's json to given json dict"

        if period is None:
            keys = ['date', 'time', 'duration', 'state', 'period']
            for k in keys:
                key = "%s_%s" % (type, k)
                jsondict[key] = None
        else:
            pjson = PeriodHttpAdapter(period).jsondict('UTC', 0.0)
            jsondict["%s_%s" % (type, "date")] = pjson['date']
            jsondict["%s_%s" % (type, "time")] = pjson['time']
            jsondict["%s_%s" % (type, "duration")]   = pjson['duration']
            jsondict["%s_%s" % (type, "state")]      = pjson['state']

    def period_from_post(self, fdata, type, sesshun):
        "Update or create a period for a window based on post data."

        # TBF:  Too much code in this try block.  What error(s) are we 
        #       guarding against here?
        try:
            dur = float(fdata.get("%s_%s" % (type, "duration"), None))
            duration = TimeAgent.rndHr2Qtr(dur)
            date = fdata.get("%s_%s" % (type, "date"), None)
            time = fdata.get("%s_%s" % (type, "time"), None)
            now           = dt2str(TimeAgent.quarter(datetime.utcnow()))
            if date is None:
                start = now
            else:
                start = TimeAgent.quarter(strStr2dt(date, time + ':00'))
        except:
            duration = None
            start = None

        # do we have a period of this type yet?
        if type == "default":
            p = self.window.default_period
        elif type == "choosen":
            p = self.window.period
        else:
            raise "unknown type"

        if p is None:
            # try to create it from given info
            if start is not None and duration is not None \
                and sesshun is not None:
               # create it! reuse the period code!
               p = PeriodHttpAdapter.create()
               pfdata = dict(date = date
                           , time = time
                           , duration = duration
                           , handle = self.window.toHandle())
               PeriodHttpAdapter(p).init_from_post(pfdata, 'UTC')
               if type == "default":
                  self.window.default_period = p
                  self.window.default_period.save()

               elif type == "choosen":
                  self.window.period = p
                  self.window.period.save()
        else:
            # update it
            p.start = start
            p.duration = duration
            p.save()

