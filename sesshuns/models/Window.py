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
    period         = models.ForeignKey(Period, related_name = "window", null = True, blank = True)
    start_date     = models.DateField(help_text = "yyyy-mm-dd hh:mm:ss")
    duration       = models.IntegerField(help_text = "Days")

    def __unicode__(self):
        return "Window (%d) for Sess (%d)" % \
            (self.id
           , self.session.id)

    def __str__(self):
        name = self.session.name if self.session is not None else "None"
        return "Window for %s, from %s for %d days, default: %s, period: %s" % \
            (name
           , self.start_date.strftime("%Y-%m-%d")
           , self.duration
           , self.default_period
           , self.period)

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

    # TBF: is this correct?
    def is_published(self):
        return self.default_period and self.default_period.abbreviaton in ['S', 'C']

    # TBF: refactor this to use the state method
    def is_scheduled_or_completed(self):
        period = self.period if self.period is not None and self.period.state.abbreviation in ['S', 'C'] else None
        if period is None:
            period = self.default_period if self.default_period is not None and self.default_period.state.abbreviation in ['S', 'C'] else None
        return period

    ##################################################################
    # state will return the state of the window, or none if the window
    # is not in a legal state.  The truth table is as follows, where
    # 'D' is deleted, 'P' pending, 'S' scheduled, and 'C' completed:
    #
    #    period                default_period         state
    #    None                  P                      P
    #    S                     D                      S
    #    S                     S                      S
    #    C                     C                      C
    #    C                     D                      C
    #    P                     P                      P*
    #
    # Any other combinaton returns None
    #
    # * This is legal, but Antioch won't accept a window in this state
    ##################################################################
    def state(self):
        "A Windows state is a combination of the state's of it's Periods"

        # TBF: need to check that these make sense
        deleted   = Period_State.get_state("D")
        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")
        completed = Period_State.get_state("C")

        if self.default_period:
            if self.default_period.isPending() and self.period is None:
                # initial state windows are in when created
                return pending
            else:
                if self.period:
                    if self.default_period.isCompleted() and self.period.isCompleted():
                        return completed
                    if self.default_period.isPending() and self.period.isPending():
                        return pending
                    if self.default_period.isDeleted() and self.period.isScheduled():
                        return scheduled
                    if self.default_period.isScheduled() and self.period.isScheduled():
                        return scheduled
                    if self.default_period.isDeleted() and self.period.isCompleted():
                        return completed
                # We have a default period, it is not pending, and
                # none of the other conditions is met.
                return None
        else:
            # No default period!
            return None

    state.short_description = 'Window State'

    def dual_pending_state(self):
        """
        Returns true if both period and default_period exist and are
        in a Pending state
        """
        if self.default_period and self.period:
            if self.default_period.isPending() and self.period.isPending():
                return True
        return False

    dual_pending_state.short_description = 'Window special pending state'

    def reconcile(self):
        """
        Similar to publishing a period, this moves a window from an inital,
        or transitory state, to a final scheduled state.
        Move the default period to deleted, and publish the scheduled period.
        """

        deleted   = Period_State.get_state("D")
        pending   = Period_State.get_state("P")
        scheduled = Period_State.get_state("S")
        
        # raise an error?
        assert self.default_period is not None

        # if this has already been reconciled, or is in an invalid
        # state, don't do anything.
        state = self.state()
        if state is None or state == scheduled:
            return

        if self.period is not None:
            # use this period as the scheduled one!
            self.default_period.move_to_deleted_state()
            self.default_period.save()
            self.period.move_to_scheduled_state()
            self.period.save()
        else:
            # use the default period!
            self.default_period.move_to_scheduled_state()
            self.default_period.save()
            self.period = self.default_period
            self.period.save()

        self.save()    

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

    def assignPeriod(self, periodId, default):
        "Assign the given period to the default or choosen period"
        p = first(Period.objects.filter(id = periodId))
        if p is None:
            return
        if default:
            self.default_period = p
        else:
            self.period = p
        self.save()

    class Meta:
        db_table  = "windows"
        app_label = "sesshuns"

