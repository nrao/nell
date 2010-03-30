from django.db  import models
from datetime   import datetime, timedelta

from utilities import TimeAgent

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
        #default_period = self.default_period.__str__() if self.default_period is not None else "None"
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

    def jsondict(self):
        js = {  "id"             : self.id
              , "handle"         : self.toHandle()
              , "session"        : self.session.jsondict()
              , "start"          : self.start_date.strftime("%Y-%m-%d")
              , "end"            : self.end().strftime("%Y-%m-%d")
              , "duration"       : self.duration
              }
        # we need to do this so that the window explorer can work with
        # a 'flat' json dictionary
        self.add_period_json(js, "default", self.default_period)
        self.add_period_json(js, "choosen", self.period)
        return js    

    def add_period_json(self, jsondict, type, period):
        "Adss part of the given period's json to given json dict"

        if period is None:
            keys = ['date', 'time', 'duration', 'state', 'period']
            for k in keys:
                key = "%s_%s" % (type, k)
                jsondict[key] = None
        else:
            pjson = period.jsondict('UTC')
            jsondict["%s_%s" % (type, "date")] = pjson['date']
            jsondict["%s_%s" % (type, "time")] = pjson['time']
            jsondict["%s_%s" % (type, "duration")]   = pjson['duration']
            jsondict["%s_%s" % (type, "state")]      = pjson['state']

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

    def init_from_post(self, fdata):
        self.from_post(fdata)

    def update_from_post(self, fdata):
        self.from_post(fdata)

    def from_post(self, fdata):

        # most likely, we'll be specifying sessions for windows in the same
        # manner as we do for periods
        handle = fdata.get("handle", "")
        if handle:
            self.session = self.handle2session(handle)
        else:
            try:
                maintenance = first(Project.objects.filter(pcode='Maintenance'))
                self.session = first(Sesshun.objects.filter(project=maintenance))
            except:
                self.session  = Sesshun.objects.get(id=fdata.get("session", 1))

         # get the date
        date = fdata.get("start", datetime.utcnow().strftime("%Y-%m-%d"))
        self.start_date = datetime.strptime(date, "%Y-%m-%d").date()

        # TBF: why is this going back and forth as a float?
        self.duration = int(float(fdata.get("duration", "1.0")))

        # we are working with a 'flat' dictionary that has only a few
        # of the specified fields for it's two periods.
        self.period_from_post(fdata, "default", self.session)
        self.period_from_post(fdata, "choosen", self.session)
       
        self.save()

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
            p = self.default_period
        elif type == "choosen":
            p = self.period
        else:
            raise "unknown type"

        if p is None:
            # try to create it from given info
            if start is not None and duration is not None \
                and sesshun is not None:
               # create it! reuse the period code!
               p = Period.create()
               pfdata = dict(date = date
                           , time = time
                           , duration = duration
                           , handle = self.toHandle())
               p.init_from_post(pfdata, 'UTC')
               if type == "default":
                  self.default_period = p
                  self.default_period.save()

               elif type == "choosen":
                  self.period = p
                  self.period.save()
        else:
            # update it
            p.start = start
            p.duration = duration
            p.save()

    def eventjson(self, id):
        end = self.start_date + timedelta(days = self.duration)

        return {
                "id"   : id
              , "title": "".join(["Window ", self.session.name])
              , "start": self.start_date.isoformat()
              , "end"  : end.isoformat()
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

