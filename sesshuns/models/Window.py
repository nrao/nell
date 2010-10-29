from django.db  import models
from datetime   import datetime, timedelta

from nell.utilities import TimeAgent

from common  import *
from Sesshun import Sesshun
from Period  import Period
from Period_State  import Period_State

class Window(models.Model):
    session        = models.ForeignKey(Sesshun)
    default_period = models.ForeignKey(Period
                                     , related_name = "default_window"
                                     , null = True
                                     , blank = True
                                     )
    #period         = models.ForeignKey(Period, related_name = "window", null = True, blank = True)
    start_date     = models.DateField(help_text = "yyyy-mm-dd hh:mm:ss")
    duration       = models.IntegerField(help_text = "Days")
    complete      = models.BooleanField(default = False)
    total_time     = models.FloatField(help_text = "Hours", null = True, default = 0.0)

    def __unicode__(self):
        return "Window (%d) for Sess (%d)" % \
            (self.id
           , self.session.id)

    def __str__(self):
        name = self.session.name if self.session is not None else "None"
        return "Window for %s, from %s for %d days, default: %s, # periods: %d" % \
            (name
           , self.start_date.strftime("%Y-%m-%d")
           , self.duration
           , self.default_period
           , len(self.periods.all())) #self.period)

    def end(self):
        return self.last_date()

    def last_date(self):
        "Ex: start = 1/10, duration = 2 days, last_date = 1/11"
        return self.start_date + timedelta(days = self.duration - 1)

    def inWindow(self, date):
        return (self.start_date <= date) and (date <= self.last_date())

    def start_datetime(self):
        return TimeAgent.date2datetime(self.start_date)

    def end_datetime(self):
        "We want this to go up to the last second of the last_date"
        dt = TimeAgent.date2datetime(self.last_date())
        return dt.replace(hour = 23, minute = 59, second = 59)

    def isInWindow(self, period):
        "Does the given period overlap at all in window"

        # need to compare date vs. datetime objs
        #winStart = datetime(self.start_date.year
        # with what we have in memory
        #                  , self.start_date.month
        #                  , self.start_date.day)
        #winEnd = winStart + timedelta(days = self.duration)                  
        return overlaps((self.start_datetime(), self.end_datetime())
                      , (period.start, period.end()))

        return False

    def timeRemaining(self):
        "Total - Billed"
        return self.total_time - self.timeBilled()

    def timeBilled(self):
        """
        Simply the sum of all the periods' time billed, regardless of
        state.  Remember that, in a healthy systme, pending and deleted
        periods should have no time billed.
        """
        return sum([p.accounting.time_billed() for p in self.periods.all()])

    def publish(self): #Period(self, p_id):
        "A period was just published, see if we can complete this."

        timeRemaining = self.timeRemaining()

        if timeRemaining == 0:
            # this window is complete!
            self.complete = True
            if self.default_period.isPending():
                self.default_period.move_to_deleted_state()
        else:    
            # window is not complete, but default gets adjusted
            self.default_period.duration = timeRemaining
            self.default_period.save()
        
    def setComplete(self, complete):
        """
        When a window is set as not complete, the default period
        comes back.
        """
        remaining = self.timeRemaining()
        if not complete and self.complete and \
          remaining != 0 and self.default_period is not None:
            self.default_period.duration = remaining
            self.default_period.state = Period_State.get_state("P")
            self.default_period.save()
        self.complete = complete
        self.save()

    def nonDefaultPeriods(self):
        return [p for p in self.periods.all() if p != self.default_period]

    def periodStates(self):
        return [p.state for p in self.periods.all().order_by("start")]

    def periodsByState(self, s):    
        "get periods by their state, which is one of ['P', 'D', 'S']"
        state = Period_State.get_state(s)
        return [p for p in self.periods.all() if p.state == state]

    def scheduledPeriods(self):
        return self.periodsByState("S")

    def pendingPeriods(self):
        return self.periodsByState("P")

    def handle2session(self, h):
        n, p = h.rsplit('(', 1)
        name = n.strip()
        pcode, _ = p.split(')', 1)
        return Sesshun.objects.filter(project__pcode__exact=pcode).get(name=name)

    def toHandle(self):
        if self.session is None:
            return ""
        if self.session.original_id is None:
            original_id = ""
        else:
            original_id = str(self.session.original_id)
        return "%s (%s) %s" % (self.session.name
                             , self.session.project.pcode
                             , original_id)

    def eventjson(self, id):
        end = self.start_date + timedelta(days = self.duration)

        return {
                "id"   :     id
              , "title":     "".join(["Window ", self.session.name])
              , "start":     self.start_date.isoformat()
              , "end"  :     end.isoformat()
              , "className": 'window'
        }
 
    class Meta:
        db_table  = "windows"
        app_label = "sesshuns"

