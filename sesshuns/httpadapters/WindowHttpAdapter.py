from datetime               import datetime
from PeriodHttpAdapter      import PeriodHttpAdapter
from WindowRangeHttpAdapter import WindowRangeHttpAdapter
from SessionHttpAdapter     import SessionHttpAdapter
from sesshuns.models        import Period, Sesshun, Period_State
from sesshuns.models.common import *

class WindowHttpAdapter (object):

    def __init__(self, window):
        self.window = window

    def load(self, window):
        self.window = window

    def jsondict(self):
        if len(self.window.ranges()) == 0:
            start = end = duration = None
        else:    
            start = self.window.start_date().strftime("%Y-%m-%d")
            end = self.window.end().strftime("%Y-%m-%d")
            duration = self.window.duration()
            
        js = {  "id"             : self.window.id
              , "handle"         : self.window.toHandle()
              , "start"          : start
              , "end"            : end
              , "duration"       : duration
              , "total_time"     : self.window.total_time
              , "time_billed"    : self.window.timeBilled()
              , "time_remaining" : self.window.timeRemaining()
              , "complete"       : self.window.complete
              , "contigious"     : self.window.isContigious()
              , "num_periods"    : self.window.periods.count()
              , "periods"        : [PeriodHttpAdapter(p).jsondict('UTC', 0.0) for p in self.window.periods.all()]
              , "ranges"         : [WindowRangeHttpAdapter(wr).jsondict() for wr in self.window.ranges()]
              , "errors"         : self.window.errors()
              }
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

        self.window.total_time = float(fdata.get("total_time", "0.0"))
        self.window.setComplete(fdata.get("complete", "false") == "true")

        self.window.save()
