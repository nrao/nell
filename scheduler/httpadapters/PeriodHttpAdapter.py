# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from datetime               import datetime
from nell.utilities         import TimeAgent, Score
from scheduler.models        import Period, Period_Accounting, Period_Receiver, \
                                   Period_State, Project, Receiver, Sesshun
from utilities.TimeAgent import d2str, dt2str, strStr2dt, t2str
from SessionHttpAdapter     import SessionHttpAdapter

class PeriodHttpAdapter (object):

    def __init__(self, period):
        self.period = period

    def load(self, period):
        self.period = period

    def jsondict(self, tz, cscore):
        start = self.period.start if tz == 'UTC' else TimeAgent.utc2est(self.period.start)
        end   = self.period.end() if tz == 'UTC' else TimeAgent.utc2est(self.period.end())
        w = self.period.window
        js =   {"id"           : self.period.id
              , "session"      : SessionHttpAdapter(self.period.session).jsondict()
              , "session_name" : self.period.session.name
              , "handle"       : self.period.toHandle()
              , "stype"        : self.period.session.session_type.type[0].swapcase()
              , "end_date"     : d2str(end)
              , "end_time"     : t2str(end)
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
              , "wstart"       : d2str(w.start_date()) if w is not None else None
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
            new_session = Sesshun.handle2session(handle)
            if not update_score:
                update_score = self.period.session != new_session
            self.period.session = new_session
        else:
            try:
                maintenance = Project.objects.get(pcode='Maintenance')
                self.period.session = Sesshun.objects.get(project=maintenance)
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
        self.period.state = Period_State.objects.get(abbreviation=stateAbbr)
        self.period.moc_ack = fdata.get("moc_ack", self.period.moc_ack)

        # elective? 
        eId = fdata.get("elective_id", None)
        if eId is not None:
            self.period.elective_id = eId

        # window?    
        wId = fdata.get("window_id", None)
        if wId is not None:
            self.period.window_id = wId
        elif self.period.session.isWindowed() and self.period.window_id is None:
            # just because the window id wasn't specified doesn't mean
            # we don't want to assign this a window:
            # for instance, if this period was created outside of the 
            # Windowed Period Explorer, we'll have to assign a window
            self.period.assign_a_window()

        # is this period a default period for a window?
        default = fdata.get("wdefault", None)
        if default is not None: #
            if default == "true" and self.period.window is not None:
                # assign this period as a default
                self.period.window.default_period = self.period
                self.period.window.save()
            elif default == "false" and self.period.window is not None:
                # unassign this period as a default
                self.period.window.default_period = None
                self.period.window.save()
            
        # how to initialize scheduled time? when they get published!
        # so, only create an accounting object if it needs it.
        if self.period.accounting is None:
            pa = Period_Accounting(scheduled = 0.0)
            pa.save()
            self.period.accounting = pa

        self.period.accounting.update_from_post(fdata)

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
            rcvr = Receiver.objects.get(abbreviation = r.strip())
            if rcvr is not None:
                rp = Period_Receiver(receiver = rcvr, period = self.period)
                rp.save()
