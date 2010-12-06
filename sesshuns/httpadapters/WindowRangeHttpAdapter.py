from datetime               import datetime
from sesshuns.models        import Window, Period, Sesshun, Period_State
from sesshuns.models.common import *

class WindowRangeHttpAdapter (object):

    def __init__(self, windowRange):
        self.windowRange = windowRange

    def load(self, windowRange):
        self.windowRange = windowRange

    def jsondict(self):
        js = {"id"       : self.windowRange.id
            , "start"    : self.windowRange.start_date.strftime("%Y-%m-%d")
            , "end"      : self.windowRange.end().strftime("%Y-%m-%d")
            , "duration" : self.windowRange.duration
             }
        return js                     

    def init_from_post(self, fdata):
        self.from_post(fdata)

    def update_from_post(self, fdata):
        self.from_post(fdata)

    def from_post(self, fdata):
        w_id = fdata.get("window_id", None)
        if w_id is not None:
            window = first(Window.objects.filter(id = int(w_id)))
            self.windowRange.window = window

        date = fdata.get("start", datetime.utcnow().strftime("%Y-%m-%d"))
        self.windowRange.start_date = datetime.strptime(date, "%Y-%m-%d").date()

        self.windowRange.duration = int(float(fdata.get("duration", "1.0")))

        self.windowRange.save()        
