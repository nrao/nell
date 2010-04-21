from django.db  import models
from common     import *

from Project           import Project
from Sesshun           import Sesshun
from Period_Accounting import Period_Accounting
from Period_State      import Period_State
from Receiver          import Receiver
from Receiver_Schedule import Receiver_Schedule

class Period(models.Model):
    session    = models.ForeignKey(Sesshun)
    accounting = models.ForeignKey(Period_Accounting, null=True)
    state      = models.ForeignKey(Period_State, null=True)
    start      = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm")
    duration   = models.FloatField(help_text = "Hours")
    score      = models.FloatField(null = True, editable=False, blank = True)
    forecast   = models.DateTimeField(null = True, editable=False, blank = True)
    backup     = models.BooleanField()
    moc_ack    = models.BooleanField(default = False)
    receivers  = models.ManyToManyField(Receiver, through = "Period_Receiver")

    class Meta:
        db_table  = "periods"
        app_label = "sesshuns"
    
    @staticmethod
    def create(*args, **kws):
        """
        Recomended way of 'overriding' the constructor.  Here we want to make
        sure that all new Periods init their rcvrs correctly.
        """
        p = Period(**kws)
        # don't save & init rcvrs unless you can
        if not kws.has_key("session"):
            # need the session first!
            return p
        p.save()
        p.init_rcvrs_from_session()
        return p
            
    def end(self):
        "The period ends at start + duration"
        return self.start + timedelta(hours = self.duration)

    def on_day(self, day):
        "Does this period ever take place on the specified day (a datetime)?"
        next_day = day + timedelta(days = 1)
        return (self.end() > day) and (self.start < next_day)

    def __unicode__(self):
        return "Period for Session (%d): %s for %5.2f Hrs (%s)" % \
            (self.session.id, self.start, self.duration, self.state.abbreviation)

    def __str__(self):
        return "%s: %s for %5.2f Hrs" % \
            (self.session.name, self.start, self.duration)

    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def display_name(self):
        return self.__str__()

    def isDeleted(self):
        return self.state.abbreviation == 'D'

    def isScheduled(self):
        return self.state.abbreviation == 'S'

    def isPending(self):
        return self.state.abbreviation == 'P'

    def isCompleted(self):
        return self.state.abbreviation == 'C'

    def init_from_post(self, fdata, tz):
        self.from_post(fdata, tz)

    def update_from_post(self, fdata, tz):
        self.from_post(fdata, tz)
        # TBF: should we do this?
        if self.accounting is not None:
            self.accounting.update_from_post(fdata)

    def from_post(self, fdata, tz):

        # only update the score if something in the period has changed
        update_score = False
        if not update_score:
            update_score = self.id is None
        # if newly created then start with a default of zero
        if update_score:
            self.score = 0.0
            self.forecast = TimeAgent.quarter(datetime.utcnow())
        handle = fdata.get("handle", "")
        if handle:
            new_session = self.handle2session(handle)
            if not update_score:
                update_score = self.session != new_session
            self.session = new_session
        else:
            try:
                maintenance = first(Project.objects.filter(pcode='Maintenance'))
                self.session = first(Sesshun.objects.filter(project=maintenance))
            except:
                self.session  = Sesshun.objects.get(id=fdata.get("session", 1))
        now           = TimeAgent.quarter(datetime.utcnow())
        date          = fdata.get("date", None)
        time          = fdata.get("time", "00:00")
        if date is None:
            self.start = now
        else:
            new_start = TimeAgent.quarter(strStr2dt(date, time + ':00'))
            if tz == 'ET':
                new_start = TimeAgent.est2utc(self.start)
            if not update_score:
                update_score = self.start != new_start
            self.start = new_start
        new_duration = TimeAgent.rndHr2Qtr(float(fdata.get("duration", "1.0")))
        if not update_score:
            update_score = self.duration != new_duration
        self.duration = new_duration
        scorer = Score()
        if update_score and now < self.start:
            self.score = scorer.session(self.session.id
                                       , self.start
                                       , self.duration)
            self.forecast = TimeAgent.quarter(datetime.utcnow())
        else:
            scorer.clear()
        self.backup   = True if fdata.get("backup", None) == 'true' else False
        stateAbbr = fdata.get("state", "P")
        self.state = first(Period_State.objects.filter(abbreviation=stateAbbr))
        self.moc_ack = fdata.get("moc_ack", self.moc_ack)

        # how to initialize scheduled time? when they get published!
        # so, only create an accounting object if it needs it.
        if self.accounting is None:
            pa = Period_Accounting(scheduled = 0.0)
            pa.save()
            self.accounting = pa

        self.save()

        # now that we have an id (from saving), we can specify the relation
        # between this period and assocaited rcvrs
        self.update_rcvrs_from_post(fdata)

    def update_rcvrs_from_post(self, fdata):

        # clear them out
        rps = Period_Receiver.objects.filter(period = self)
        for rp in rps:
            rp.delete()

        # insert the new ones: what are they?
        rcvrStr = fdata.get("receivers", "")
        if rcvrStr == "":
            # use the sessions receivers - this will happen on init
            if self.session is not None:
                rcvrAbbrs = self.session.rcvrs_specified()
            else:
                rcvrAbbrs = []
        else:    
            rcvrAbbrs = rcvrStr.split(",")

        # now that we have their names, put them in the DB    
        for r in rcvrAbbrs:
            rcvr = first(Receiver.objects.filter(abbreviation = r.strip()))
            if rcvr is not None:
                rp = Period_Receiver(receiver = rcvr, period = self)
                rp.save()
            
    def init_rcvrs_from_session(self):
        "Use the session's rcvrs for the ones associated w/ this period."
        if self.session is None:
            return
        rcvrAbbrs = self.session.rcvrs_specified()
        for r in rcvrAbbrs:
            rcvr = first(Receiver.objects.filter(abbreviation = r.strip()))
            if rcvr is not None:
                rp = Period_Receiver(receiver = rcvr, period = self)
                rp.save()

    def handle2session(self, h):
        n, p = h.rsplit('(', 1)
        name = n.strip()
        pcode, _ = p.split(')', 1)
        return Sesshun.objects.filter(project__pcode__exact=pcode).get(name=name)

    def toHandle(self):
        if self.session.original_id is None:
            original_id = ""
        else:
            original_id = str(self.session.original_id)
        return "%s (%s) %s" % (self.session.name
                             , self.session.project.pcode
                             , original_id)

    def eventjson(self, id):
        end = self.start + timedelta(hours = self.duration)

        return {
                "id"   : id
              , "title": "".join(["Observing ", self.session.name])
              , "start": self.start.isoformat()
              , "end"  : end.isoformat()
        }

    def jsondict(self, tz, cscore):
        start = self.start if tz == 'UTC' else TimeAgent.utc2est(self.start)
        w = self.get_window()
        js =   {"id"           : self.id
              , "session"      : self.session.jsondict()
              , "session_name" : self.session.name
              , "handle"       : self.toHandle()
              , "stype"        : self.session.session_type.type[0].swapcase()
              , "date"         : d2str(start)
              , "time"         : t2str(start)
              , "lst"          : str(TimeAgent.dt2tlst(self.start))
              , "duration"     : self.duration
              , "sscore"       : self.score       # scheduling score
              , "cscore"       : cscore           # current score
              , "forecast"     : dt2str(self.forecast)
              , "backup"       : self.backup
              , "moc_ack"      : self.moc_ack
              , "state"        : self.state.abbreviation
              , "windowed"     : True if w is not None else False
              , "wdefault"     : self.is_windowed_default() \
                                     if w is not None else None
              , "wstart"       : d2str(w.start_date) if w is not None else None
              , "wend"         : d2str(w.last_date()) if w is not None else None
              , "receivers"    : self.get_rcvrs_json()
                }
        # include the accounting but keep the dict flat
        if self.accounting is not None:
            accounting_js = self.accounting.jsondict()
            # make sure the final jsondict has only one 'id'
            accounting_id = accounting_js.pop('id')
            accounting_js.update({'accounting_id' : accounting_id})
            js.update(accounting_js)
        return js

    def get_rcvr_ranges(self):
        ranges = ["%5.2f - %5.2f".strip() % (r.freq_low, r.freq_hi) for r in self.receivers.all()]
        return ", ".join(ranges)

    def receiver_list(self):
        return self.get_rcvrs_json()

    def get_rcvrs_json(self):
        rcvrs = [r.abbreviation for r in self.receivers.all()]
        return ", ".join(rcvrs)

    def moc_met(self):
        """
        Returns a Boolean indicated if MOC are met (True) or not (False).
        Only bothers to calculate MOC for open and windowed sessions whose
        end time is not already past.
        """
        # TBF: When correctly calculating MOC for < 2 GHz observations,
        #      remove this hack.
        if self.session.frequency <= 2.:
            return True

        if self.session.session_type.type not in ("open", "windowed") or \
           self.end() < datetime.utcnow():
            return True

        url = ANTIOCH_SERVER_URL + \
              "/moc?session_id=" + \
              `self.session.id` + \
              "&start=" + \
              self.start.isoformat().replace("T", "+").replace(":", "%3A")
        try:
            antioch_cnn = urllib2.build_opener().open(url)
            moc = json.loads(antioch_cnn.read(0x4000))['moc']
        except:
            moc = True

        return moc

    def has_required_receivers(self):

        # Find all the required receiver sets for this period and schedule.
        # E.g. for one session:
        #     [[a, b, c], [x, y, z]] = (a OR b OR c) AND (x OR y OR z)
        required = [self.session.receiver_group_set.all()]
        if all([len(set) == 0 for set in required]):
            return False # No receivers, problem!

        schedule = Receiver_Schedule.extract_schedule(self.start, 0)
        if schedule == {} or \
           (len(schedule.values()) == 1 and schedule.values()[0] == []):
            return False # no schedule, no required rcvrs!

        # should return a single date w/ rcvr list
        items = schedule.items()
        assert len(items) == 1
        dt, receivers = items[0]

        receivers = Set(receivers)
        if not any([all([Set(g.receivers.all()).intersection(receivers) \
                        for g in set]) for set in required]):
            return False # Receiver isn't up
        else:
            return True # Receiver is up

    def has_observed_rcvrs_in_schedule(self):


        #obs_rcvrs = [r.abbreviation for r in self.receivers.all()]
        obs_rcvrs = self.receivers.all()

        schedule = Receiver_Schedule.extract_schedule(self.start, 0)
        if schedule == {} or \
           (len(schedule.values()) == 1 and schedule.values()[0] == []):
            return False # no schedule, no required rcvrs!

        # should return a single date w/ rcvr list
        items = schedule.items()
        assert len(items) == 1
        dt, receivers = items[0]

        for r in obs_rcvrs:
            if r not in receivers:
                return False # Receiver isn't up

        return True # Receiver is up

    def move_to_deleted_state(self):
        "all in the name"
        self.state = Period_State.get_state("D")
        self.save()

    def move_to_scheduled_state(self):
        "worker for publish method: pending -> scheduled, and init time accnt."
        if self.state.abbreviation == "P":
            self.state = first(Period_State.objects.filter(abbreviation = 'S'))
            self.accounting.scheduled = self.duration
            self.accounting.save()
            self.save()

    def publish(self):
        "pending state -> scheduled state: and init the time accounting"
        # NOTE: it would be ideal to 'publish' a period's associated
        # window (reconcile it, really).  But we haven't been able to
        # get that to work properly, so windowed periods must be handled
        # elsewhere when publishing.
        if not self.is_windowed():
            if self.state.abbreviation == 'P':
                self.move_to_scheduled_state()


    def delete(self):
        "Keep non-pending periods from being deleted."
        if self.state.abbreviation != 'P':
            self.move_to_deleted_state()
        else:
            models.Model.delete(self)  # pending can really get removed!

    def remove(self):
        "A backdoor method for really deleting!"
        models.Model.delete(self)

    def is_windowed(self):
        return self.session.session_type.type == "windowed"

    def has_valid_windows(self):
        """
        If a period belongs to a Windowed Session, then it should be assigned
        to a Window as either a 'default_period' or a 'period'
        """
        if self.session.session_type.type != "windowed":
            return False # who cares?

        default_windows = self.default_window.all()
        windows = self.window.all()

        # neither one of these should point to more then one window
        if len(default_windows) > 1 or len(windows) > 1:
            return False

        # this period should be assigned to at least one window
        if len(default_windows) == 0 and len(windows) == 0:
            return False
        
        return True

    def get_default_window(self):
        "Get the window this period is a default period for."
        if self.is_windowed() and self.has_valid_windows():
            return first(self.default_window.all())
        else:
            return None

    def get_window(self):
        "Get the window this period is either default or choosen period for."
        if self.is_windowed() and self.has_valid_windows():
            if len(self.default_window.all()) == 1:
                return first(self.default_window.all())
            else:
                return first(self.window.all())
        else:
            return None

    def is_windowed_default(self):
        "Is this period the default period for a window? If not, is the choosen"
        # assume error checking done before hand
        # self.is_windowed() and self.has_valid_windows()
        if len(self.default_window.all()) == 1:
            return True
        else:
            return False

    @staticmethod
    def get_periods(start, duration, ignore_deleted = True):
        "Returns all periods that overlap given time interval (start, minutes)"
        end = start + timedelta(minutes = duration)
        # there is no Period.end in the database, so, first cast a wide net.
        # we can do this because periods won't last more then 16 hours ...
        beforeStart = start - timedelta(days = 1)
        afterEnd    = end   + timedelta(days = 1)
        some = Period.objects.filter(start__gt = beforeStart
                                   , start__lt = afterEnd).order_by('start')
        # now widdle this down to just the periods that overlap  
        ps = [p for p in some if (p.start >= start and p.end() <= end) \
                              or (p.start <= start and p.end() > start) \
                              or (p.start < end    and p.end() >= end)]
        if ignore_deleted:                      
            ps = [p for p in ps if p.state.abbreviation != 'D']
        return ps
          
        
    @staticmethod    
    def in_time_range(begin, end, ignore_deleted = True):
        """
        Returns all periods in a time range, taking into account that periods
        can overlap into the first day.
        """
        # TBF: why doesn't ps.query.group_by = ['start'] work?
        ps = Period.objects.filter(start__gt = begin - timedelta(days = 1)
                                 , start__lt = end).order_by('start')
        ps = [p for p in ps if p.end() >= begin]

        if ignore_deleted:                      
            ps = [p for p in ps if p.state.abbreviation != 'D']

        return ps

    @staticmethod
    def publish_periods(start, duration):
        """
        Due to problems we encountered with the relationship between
        periods and windows in the DB, we can't reconcile windows
        from within a period's publish method, we must take this approach.
        """

        periods = Period.get_periods(start, duration)

        # Publishing moves any period whose state is Pending to Scheduled,
        # and initializes time accounting (scheduled == period duration).
        windows = []
        for p in periods:
            if p.session.session_type.type != 'windowed':
                p.publish()
                p.save()
            else:
                # Don't publish this period, instead, find out the window
                # to which it belongs so we can reconcile it latter.
                window = p.get_window()
                if window is not None and \
                   window.id not in [w.id for w in windows]:
                    windows.append(window)

        # Now, reconcile any windows.
        for w in windows:
            w.reconcile()
            w.save()

class Period_Receiver(models.Model):
    period   = models.ForeignKey(Period)
    receiver = models.ForeignKey(Receiver)

    class Meta:
        db_table  = "periods_receivers"
        app_label = "sesshuns"
