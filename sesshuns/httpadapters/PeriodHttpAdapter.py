from datetime               import datetime
from nell.utilities         import TimeAgent, Score
from sesshuns.models        import Period, Period_Accounting, Period_Receiver, \
                                   Period_State, Project, Receiver, Sesshun
from sesshuns.models.common import first, d2str, dt2str, strStr2dt, t2str
from SessionHttpAdapter     import SessionHttpAdapter

class PeriodHttpAdapter (object):

    def __init__(self, period):
        self.period = period

    def load(self, period):
        self.period = period

    def jsondict(self, tz, cscore):
        start = self.period.start if tz == 'UTC' else TimeAgent.utc2est(self.period.start)
        w = self.period.get_window()
        js =   {"id"           : self.period.id
              , "session"      : SessionHttpAdapter(self.period.session).jsondict()
              , "session_name" : self.period.session.name
              , "handle"       : self.period.toHandle()
              , "stype"        : self.period.session.session_type.type[0].swapcase()
              , "date"         : d2str(start)
              , "time"         : t2str(start)
              , "lst"          : str(TimeAgent.dt2tlst(self.period.start))
              , "duration"     : self.period.duration
              , "sscore"       : self.period.score       # scheduling score
              , "cscore"       : cscore           # current score
              , "forecast"     : dt2str(self.period.forecast)
              , "backup"       : self.period.backup
              , "moc_ack"      : self.period.moc_ack if self.period.moc_ack is not None else False
              , "state"        : self.period.state.abbreviation if self.period.state is not None else ""
              , "windowed"     : True if w is not None else False
              , "wdefault"     : self.period.is_windowed_default() \
                                     if w is not None else None
              , "wstart"       : d2str(w.start_date) if w is not None else None
              , "wend"         : d2str(w.last_date()) if w is not None else None
              , "receivers"    : self.period.get_rcvrs_json()
                }
        # include the accounting but keep the dict flat
        if self.period.accounting is not None:
            accounting_js = self.period.accounting.jsondict()
            # make sure the final jsondict has only one 'id'
            accounting_id = accounting_js.pop('id')
            accounting_js.update({'accounting_id' : accounting_id})
            js.update(accounting_js)
        return js

    def init_from_post(self, fdata, tz):
        self.from_post(fdata, tz)

    def update_from_post(self, fdata, tz):
        self.from_post(fdata, tz)
        # TBF: should we do this?
        if self.period.accounting is not None:
            self.period.accounting.update_from_post(fdata)

    def from_post(self, fdata, tz):

        # only update the score if something in the period has changed
        update_score = False
        if not update_score:
            update_score = self.period.id is None
        # if newly created then start with a default of zero
        if update_score:
            self.period.score = 0.0
            self.period.forecast = TimeAgent.quarter(datetime.utcnow())
        handle = fdata.get("handle", "")
        if handle:
            new_session = self.handle2session(handle)
            if not update_score:
                update_score = self.period.session != new_session
            self.period.session = new_session
        else:
            try:
                maintenance = first(Project.objects.filter(pcode='Maintenance'))
                self.period.session = first(Sesshun.objects.filter(project=maintenance))
            except:
                self.period.session  = Sesshun.objects.get(id=fdata.get("session", 1))
        now           = TimeAgent.quarter(datetime.utcnow())
        date          = fdata.get("date", None)
        time          = fdata.get("time", "00:00")
        if date is None:
            self.period.start = now
        else:
            new_start = TimeAgent.quarter(strStr2dt(date, time + ':00'))
            if tz == 'ET':
                new_start = TimeAgent.est2utc(self.period.start)
            if not update_score:
                update_score = self.period.start != new_start
            self.period.start = new_start
        new_duration = TimeAgent.rndHr2Qtr(float(fdata.get("duration", "1.0")))
        if not update_score:
            update_score = self.period.duration != new_duration
        self.period.duration = new_duration
        scorer = Score()
        if update_score and now < self.period.start:
            self.period.score = scorer.session(self.period.session.id
                                       , self.period.start
                                       , self.period.duration)
            self.period.forecast = TimeAgent.quarter(datetime.utcnow())
        else:
            scorer.clear()
        self.period.backup   = True if fdata.get("backup", None) == 'true' else False
        stateAbbr = fdata.get("state", "P")
        self.period.state = first(Period_State.objects.filter(abbreviation=stateAbbr))
        self.period.moc_ack = fdata.get("moc_ack", self.period.moc_ack)

        # how to initialize scheduled time? when they get published!
        # so, only create an accounting object if it needs it.
        if self.period.accounting is None:
            pa = Period_Accounting(scheduled = 0.0)
            pa.save()
            self.period.accounting = pa

        self.period.save()

        # now that we have an id (from saving), we can specify the relation
        # between this period and assocaited rcvrs
        self.update_rcvrs_from_post(fdata)

    def update_rcvrs_from_post(self, fdata):

        # clear them out
        rps = Period_Receiver.objects.filter(period = self.period)
        for rp in rps:
            rp.delete()

        # insert the new ones: what are they?
        rcvrStr = fdata.get("receivers", "")
        if rcvrStr == "":
            # use the sessions receivers - this will happen on init
            if self.period.session is not None:
                rcvrAbbrs = self.period.session.rcvrs_specified()
            else:
                rcvrAbbrs = []
        else:    
            rcvrAbbrs = rcvrStr.split(",")

        # now that we have their names, put them in the DB    
        for r in rcvrAbbrs:
            rcvr = first(Receiver.objects.filter(abbreviation = r.strip()))
            if rcvr is not None:
                rp = Period_Receiver(receiver = rcvr, period = self.period)
                rp.save()
            
    def handle2session(self, h):
        n, p = h.rsplit('(', 1)
        name = n.strip()
        pcode, _ = p.split(')', 1)
        return Sesshun.objects.filter(project__pcode__exact=pcode).get(name=name)

