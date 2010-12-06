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
           , self.start_date().strftime("%Y-%m-%d")
           , self.duration()
           , self.default_period
           , len(self.periods.all())) 

    
    def isContigious(self):
        """
        A non-contigious Window has more then one window range, with 
        gaps between them.
        """
        wrs = self.ranges()
        if len(wrs) > 1:
            # if any one end isn't at the next start, then non-cont.
            for i in range(len(wrs)-1):
                end = wrs[i].start_date + timedelta(days = wrs[i].duration)
                nextStart = wrs[i+1].start_date
                if nextStart != end:
                    return False
            # if we get to here, it's contigious
            return True
        else:
            return True

    def ranges(self):
        return self.windowrange_set.all().order_by("start_date")

    def first_range(self):
        wrs = self.ranges()
        return wrs[0] if len(wrs) > 0 else None

    def last_range(self):
        wrs = self.ranges() 
        return wrs[len(wrs)-1] if len(wrs) > 0 else None

    # ****** This group of methods below can be used if gaps between
    # ****** window ranges can be ignored or Window is contigious.

    def start(self):
        return self.first_range().start_date

    def start_date(self):
        return self.start()

    def end(self):
        return self.last_date()

    def last_date(self):
        "Ex: start = 1/10, duration = 2 days, last_date = 1/11"
        start = self.last_range().start_date 
        days  = timedelta(days = self.last_range().duration - 1)
        return start + days

    def start_datetime(self):
        return TimeAgent.date2datetime(self.start())

    def end_datetime(self):
        "We want this to go up to the last second of the last_date"
        dt = TimeAgent.date2datetime(self.last_date())
        return dt.replace(hour = 23, minute = 59, second = 59)

    def duration(self):
        return (self.last_date() - self.start()).days + 1

    def inWindow(self, date):
        return (self.start() <= date) and (date <= self.last_date())

    def isInWindow(self, period):
        "Does the given period overlap at all in window"
        return overlaps((self.start_datetime(), self.end_datetime())
                      , (period.start, period.end()))

        return False
    
    # ****** end of group above that ignores window ranges ***

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

    def publish(self): 
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
        """
        This is just a summary: if the window is non contigious
        then this will not include gaps.
        """

        return {
                "id"   :     id
              , "title":     "".join(["Window ", self.session.name])
              , "start":     self.start_date().isoformat()
              , "end"  :     self.end().isoformat()
              , "className": 'window'
        }
 
    def getWindowTimeNotSchedulable(self, blackouts = True):
        "How many hours in this window are not schedulable?"
        ns = self.session.get_time_not_schedulable( \
            self.start_datetime()
          , self.end_datetime()
          , blackouts = blackouts)
        return sum([TimeAgent.timedelta2minutes(n[1] - n[0])/60.0 \
            for n in ns])
        
    def getWindowTimeBlackedOut(self):
        "How many hours in this window have been blacked out?"
        bs = self.session.project.get_blackout_times(\
            self.start_datetime()
          , self.end_datetime()) 
        return sum([TimeAgent.timedelta2minutes(b[1] - b[0])/60.0 \
            for b in bs])

    def getBlackedOutSchedulableTime(self):
        """
        Of the hours in this window that are schedulable, how
        many have been blacked out?
        """
        return self.session.getBlackedOutSchedulableTime( \
            self.start_datetime()
          , self.end_datetime())

    def defaultPeriodBlackedOut(self):
        """
        Do any of the times that are not schedulable for this 
        session due to blackouts overlapping with the default
        period?
        """

        # no default, no problem
        if self.default_period is None:
            return False

        bs = self.session.project.get_blackout_times(\
            self.default_period.start
          , self.default_period.end())

        return len(bs) > 0  
    class Meta:
        db_table  = "windows"
        app_label = "sesshuns"

