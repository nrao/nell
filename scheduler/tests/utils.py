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

from datetime                      import datetime, timedelta
from scheduler.httpadapters        import *
from scheduler.models              import *
from nell.utilities                import TimeAgent

# Test field data
fdata = {"total_time": "3"
       , "req_max": "6"
       , "name": "Low Frequency With No RFI"
       , "grade": 4.0
       , "science": "pulsar"
       , "orig_ID": "0"
       , "between": "0"
       , "proj_code": "GBT09A-001"
       , "PSC_time": "2"
       , "sem_time": 0.0
       , "req_min": "2"
       , "freq": 6.0
       , "type": "open"
       , "source" : "blah"
       , "enabled" : False
       , "authorized" : False
       , "complete" : False
       , "backup" : False
       , "lst_ex" : ""
       , "el_limit" : 25.0
         }

def create_sesshun():
    "Utility method for creating a Sesshun to test."

    s = Sesshun()
    s_adapter = SessionHttpAdapter(s)
    s_adapter.set_base_fields(fdata)
    allot = Allotment(psc_time          = float(fdata.get("PSC_time", 0.0))
                    , total_time        = float(fdata.get("total_time", 0.0))
                    , max_semester_time = float(fdata.get("sem_time", 0.0))
                    , grade             = 4.0
                      )
    allot.save()
    s.allotment        = allot
    status = Status(
               enabled    = True
             , authorized = True
             , complete   = False
             , backup     = False
                        )
    status.save()
    s.status = status
    s.save()

    t = Target(session    = s
             , system     = System.objects.get(name = "J2000")
             , source     = "test source"
             , vertical   = 2.3
             , horizontal = 1.0
               )
    t.save()
    return s

def create_users():
    users = []
    users.append(User.objects.create(original_id = 0
                , pst_id      = 0
                , sanctioned  = False
                , first_name  = 'Foo'
                , last_name   = 'Bar'
                , contact_instructions = ""
                , role  = Role.objects.all()[0]
                 ))
    users.append(User.objects.create(original_id = 0
                , pst_id      = 0
                , sanctioned  = True
                , first_name  = 'Mike'
                , last_name   = 'McCarty'
                , contact_instructions = ""
                , role  = Role.objects.all()[0]
                 ))
    users.append(User.objects.create(original_id = 0
                , pst_id      = 0
                , sanctioned  = True
                , first_name  = 'Doless'
                , last_name   = 'NoProject'
                , contact_instructions = ""
                , role  = Role.objects.all()[0]
                 ))
    return users

def create_maintenance_sesshun():
    # Test field data
    fdata = {"req_max": "6"
           , "req_min": "2"
           , "proj_code": "Maintenance"
           , "name": "Maintenance"
           , "science": "maintenance"
           , "orig_ID": "0"
           , "between": "0"
           , "freq": 6.0
           , "type": "fixed"
             }

    s = Sesshun()
    s_adapter = SessionHttpAdapter(s)
    s_adapter.set_base_fields(fdata)
    allot = Allotment(psc_time          = float(fdata.get("PSC_time", 0.0))
                    , total_time        = float(fdata.get("total_time", 0.0))
                    , max_semester_time = float(fdata.get("sem_time", 0.0))
                    , grade             = 4.0
                      )
    allot.save()
    s.allotment        = allot
    status = Status(
               enabled    = True
             , authorized = True
             , complete   = False
             , backup     = False
                        )
    status.save()
    s.status = status
    s.save()

    return s

    
def create_maintenance_period(start, duration, state = 'Scheduled'):
    s = create_maintenance_sesshun()
    state = Period_State.objects.get(name = state)
    pa = Period_Accounting(scheduled = 0.0)
    pa.save()
    p = Period(start = TimeAgent.est2utc(start),
               duration = duration,
               session = s,
               state   = state,
               accounting = pa
              )
    p.save()
    return p

def create_maintenance_elective(periods):
    """
    Creates an elective belonging to a maintenance session.  This
    elective will have as many periods as there are items in the
    'periods' parameter.  This is a tuple of tuples: ((date,
    duration), (date, duration), ...).  Because this is a maintenance
    period the dates given are assumed to be ET, and are converted to
    UT before storing in the database.
    """
    s = create_maintenance_sesshun()
    ste = Session_Type.objects.get(type = 'elective')
    s.session_type = ste
    s.save()
    e = Elective(session = s, complete = False)
    pend = Period_State.objects.get(name = 'Pending')
    e.save()

    for p in periods:
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        per = Period(session = s,
                     start = TimeAgent.est2utc(p[0]),
                     duration = p[1],
                     state = pend,
                     accounting = pa,
                     elective = e
                     )
        per.save()    

    return e

def setupElectives(f):
    def setup(self, *args):
        if f.__name__ == "setUp":
            f(self, *args)
        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("elective")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        dur = 5.0
        self.deleted   = Period_State.get_state("D")
        self.pending   = Period_State.get_state("P")
        self.scheduled = Period_State.get_state("S")

        # create an elective to group the periods by
        self.elec = Elective(session = self.sesshun, complete = False)
        self.elec.save()
        
        # create 3 periods separated by a week
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period1 = Period(session = self.sesshun
                            , start = dt 
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period1.save()    

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period2 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 7)
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period2.save() 

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period3 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 2*7)
                            , duration = dur
                            , state = self.pending
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period3.save() 

        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.period4 = Period(session = self.sesshun
                            , start = dt + timedelta(days = 3*7)
                            , duration = dur
                            , state = self.deleted
                            , accounting = pa
                            , elective = self.elec
                              )
        self.period4.save() 

        if f.__name__ != "setUp":
            f(self, *args)
    return setup

def setupWindows(f):

    def setup(self, *args):
        if f.__name__ == "setUp":
            f(self, *args)
        self.deleted   = Period_State.get_state("D")
        self.pending   = Period_State.get_state("P")
        self.scheduled = Period_State.get_state("S")

        self.sesshun = create_sesshun()
        self.sesshun.session_type = Session_Type.get_type("windowed")
        self.sesshun.save()
        dt = datetime(2009, 6, 1, 12, 15)
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        self.default_period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = self.pending
                                   , accounting = pa
                                   )
        self.default_period.save()    

        start = datetime(2009, 6, 1)
        dur   = 7 # days
        
        # create window
        self.w = Window()
        #self.w.start_date = start
        #self.w.duration = dur
        self.w.session = self.sesshun
        self.w.total_time = self.default_period.duration
        self.w.save()
        wr = WindowRange(window = self.w
                       , start_date = start
                       , duration = dur
                        )
        wr.save() 
        self.wr1 = wr

        # window & default period must both ref. eachother
        self.w.default_period = self.default_period
        self.w.save()
        self.default_period.window = self.w
        self.default_period.save()
        self.w_id = self.w.id

        # a chosen period
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()
        dt = self.default_period.start - timedelta(days = 2)
        self.period = Period(session = self.sesshun
                                   , start = dt
                                   , duration = 5.0
                                   , state = self.pending
                                   , accounting = pa
                                   )
        self.period.save()    

        pjson = PeriodHttpAdapter(self.default_period).jsondict('UTC', 1.1)
        self.fdata = {"session":  1
                    #, "start":    "2009-06-01"
                    #, "duration": 7
                    , "num_periods": 0
                    , "default_date" : pjson['date'] 
                    , "default_time" : pjson['time'] 
                    , "default_duration" : pjson['duration'] 
                    , "default_state" : pjson['state'] 
                    }
        if f.__name__ != "setUp":
            f(self, *args)
    return setup

