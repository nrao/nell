
from Allotment              import Allotment
from Blackout               import Blackout
from common                 import *
from Email                  import Email
from Investigator           import Investigator
from Observing_Type         import Observing_Type
from Parameter              import Parameter
from Period_Accounting      import Period_Accounting
from Period                 import Period
from Period_Receiver        import Period_Receiver
from Period_State           import Period_State
from Project_Blackout_09B   import Project_Blackout_09B
from Project                import Project, Project_Allotment
from Project_Type           import Project_Type
from Receiver               import Receiver
from Receiver_Schedule      import Receiver_Schedule
from Repeat                 import Repeat
from Reservation            import Reservation
from Role                   import Role
from Semester               import Semester
from Sesshun                import Sesshun, Target, Receiver_Group, Observing_Parameter  # <--BAD
from Session_Type           import Session_Type
from Status                 import Status
from System                 import System
from TimeZone               import TimeZone
from User                   import User
from Window                 import Window

def register_for_revision():
    register_model(Role)
    register_model(User, follow=['role'])
    register_model(Email, follow=['user'])
    register_model(Semester)
    register_model(Project_Type)
    register_model(Allotment)
    register_model(Project, follow=['semester', 'project_type', 'friend', 'allotments', 'investigator_set'])
    register_model(Project_Allotment, follow=['project', 'allotment'])
    register_model(Repeat)
    register_model(TimeZone)
    register_model(Blackout, follow=['user','repeat'] )
    register_model(Investigator)
    register_model(Session_Type)
    register_model(Observing_Type)
    register_model(Receiver)
    register_model(Receiver_Schedule)
    register_model(Parameter)
    register_model(Status)
    register_model(Sesshun, follow=['target_set','allotment'])
    register_model(Receiver_Group, follow=['receivers'])
    register_model(Observing_Parameter)
    register_model(System)
    register_model(Target)
    register_model(Period_Accounting)
    register_model(Period_State)
    register_model(Period, follow=['accounting', 'state', 'receivers'])
    register_model(Period_Receiver, follow=['period', 'receiver'])
    #Project_Blackout_09B
    register_model(Window)
    #Reservation

def register_model(model, follow = None):
    if not reversion.is_registered(model) and settings.USE_REVERSION:
        #print "registering model with reversion: ", model
        if follow is None:
            reversion.register(model)
        else:
            reversion.register(model, follow = follow)

register_for_revision()    
