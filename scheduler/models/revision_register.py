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

from django.conf               import settings
import reversion

from Allotment              import Allotment
from Blackout               import Blackout
from Investigator           import Investigator
from Observing_Parameter    import Observing_Parameter
from Observing_Type         import Observing_Type
from Parameter              import Parameter
from Period_Accounting      import Period_Accounting
from Period                 import Period
from Period_Receiver        import Period_Receiver
from Period_State           import Period_State
from Project_Blackout_09B   import Project_Blackout_09B
from Project                import Project
from Project_Allotment      import Project_Allotment
from Project_Type           import Project_Type
from Receiver               import Receiver
from Receiver_Group         import Receiver_Group
from Receiver_Schedule      import Receiver_Schedule
from Receiver_Temperature   import Receiver_Temperature
from Repeat                 import Repeat
from Reservation            import Reservation
from Role                   import Role
from Semester               import Semester
from Sesshun                import Sesshun
from Session_Type           import Session_Type
from Status                 import Status
from System                 import System
from Target                 import Target
from TimeZone               import TimeZone
from User                   import User
from Window                 import Window
from Elective               import Elective

def register_for_revision():
    register_model(Role)
    register_model(User, follow=['role'])
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
    register_model(Receiver_Temperature)
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
    register_model(Elective)
    #Reservation

def register_model(model, follow = None):
    if not reversion.is_registered(model) and settings.USE_REVERSION:
        #print "registering model with reversion: ", model
        if follow is None:
            reversion.register(model)
        else:
            reversion.register(model, follow = follow)

register_for_revision()    
