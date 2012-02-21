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

# for proposals
from Author             import Author
from ObservingType      import ObservingType
from ScientificCategory import ScientificCategory
from Semester           import Semester
from Status             import Status
from ProposalType       import ProposalType
from Proposal           import Proposal

# for sessions
from Allotment         import Allotment
from Backend           import Backend
from Monitoring        import Monitoring
#from ObservingType     import ObservingType
from Receiver          import Receiver
from SessionSeparation import SessionSeparation
from SessionType       import SessionType
from SessionFlags      import SessionFlags
from SessionGrade      import SessionGrade
from Source            import Source
from Target            import Target
from WeatherType       import WeatherType
from Session           import Session

def register_for_revision():

    # for proposals
    register_model(Author)
    register_model(ObservingType)
    register_model(ScientificCategory)
    register_model(Semester)
    register_model(Status)
    register_model(ProposalType)
    register_model(Proposal, follow=['semester'
                                   , 'proposal_type'
                                   , 'status'
                                   , 'pi'
                                   , 'investigators'
                                   , 'sci_categories'
                                   , 'observing_types'
                                   ])

    # for sessions
    register_model(Allotment)
    register_model(Backend)
    register_model(Monitoring)
    register_model(Receiver)
    register_model(SessionSeparation)
    register_model(SessionType)
    register_model(SessionFlags)
    register_model(SessionGrade)
    register_model(Source)
    register_model(Target)
    register_model(WeatherType)
    register_model(Session, follow=['proposal'
                                  , 'sources'
                                  , 'receivers'
                                  , 'backends'
                                  , 'allotment'
                                  , 'target'
                                  , 'session_type'
                                  , 'observing_type'
                                  , 'weather_type'
                                  , 'semester'
                                  , 'grade'
                                  , 'flags'
                                  , 'monitoring'
                                  , 'receivers_granted'
                                  , 'separation'
                                  ])

def register_model(model, follow = None):
    if not reversion.is_registered(model) and settings.USE_REVERSION:
        #print "registering model with reversion: ", model
        if follow is None:
            reversion.register(model)
        else:
            reversion.register(model, follow = follow)

register_for_revision()    
