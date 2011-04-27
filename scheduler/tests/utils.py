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
    fdata = {"total_time": "3"
           , "req_max": "6"
           , "name": "Maintenance"
           , "grade": 4.0
           , "science": "maintenance"
           , "orig_ID": "0"
           , "between": "0"
           , "proj_code": "Maintenance"
           , "PSC_time": "2"
           , "sem_time": 0.0
           , "req_min": "2"
           , "freq": 6.0
           , "type": "fixed"
           , "source" : "blah"
           , "enabled" : True
           , "authorized" : True
           , "complete" : False
           , "backup" : False
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
