from sesshuns.httpadapters                 import *
from sesshuns.models                       import *
from sesshuns.utilities           import *

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
             , system     = first(System.objects.filter(name = "J2000"))
             , source     = "test source"
             , vertical   = 2.3
             , horizontal = 1.0
               )
    t.save()
    return s

