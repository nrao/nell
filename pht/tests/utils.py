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

from pht.models import Semester
from pht.httpadapters import SessionHttpAdapter

def createSession(p):
    "Create a new session for the tests"
    sem = Semester.objects.get(semester = '12A')
    data  = {
        'name' : 'nextSemesterSession'
      , 'pcode' : p.pcode
      , 'grade' : 'A'  
      , 'semester' : sem
      , 'requested_time' : 3.5  
      , 'allocated_time' : 3.5  
      , 'session_type' : 'Open - Low Freq'
      , 'observing_type' : 'continuum' 
      , 'weather_type' : 'Poor'
      , 'repeats' : 2 
      , 'min_lst' : '10:00:00.0' 
      , 'max_lst' : '20:00:00.0' 
      , 'elevation_min' : '00:00:00.0' 
      , 'next_sem_complete' : False
      , 'next_sem_time' : 1.0
      , 'receivers' : 'L'
    }

    adapter = SessionHttpAdapter()
    adapter.initFromPost(data)
    # just so that is HAS a DSS session.
    #adapter.session.dss_session = self.maintProj.sesshun_set.all()[0]
    adapter.session.save()
    return adapter.session
