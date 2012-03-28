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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from pht.models import *

class MissingFields(object):

    """
    Class for keeping track of how many sessions
    have a given field missing.
    """

    def __init__(self
               , grade = 0
               , allocated = 0
               , min_lst = 0
               , max_lst = 0
               , weather_type = 0
                ):
        self.grade = grade            
        self.allocated = allocated            
        self.min_lst = min_lst
        self.max_lst = max_lst
        self.weather_type = weather_type

    def __str__(self):
        return "Missing: \n  Grade: %d\n  Allocated: %d\n  Min LST: %d\n  Max LST: %d\n  Weather: %d\n" % \
            (self.grade
           , self.allocated
           , self.min_lst
           , self.max_lst
           , self.weather_type
            )

    def __add__(self, other):
        return MissingFields(grade = self.grade + other.grade
                           , allocated = self.allocated + other.allocated
                           , min_lst = self.min_lst + other.min_lst
                           , max_lst = self.max_lst + other.max_lst
                           , weather_type = self.weather_type + other.weather_type
                             )


class StatusReport(object):

    """
    Informal report for finding problems and objects
    that my still be incomplete.
    """

    def __init__(self, semester = '12'):

        if semester is not None:
            self.semester = Semester.objects.get(semester = semester)


    def reportMissingFields(self, semester = None):

        if semester is not None:
            self.semester = Semester.objects.get(semester = semester)

        self.currentSessions = Session.objects.filter(proposal__semester = self.semester)
        self.pastSessions = Session.objects.all().exclude(proposal__semester = self.semester)

        self.current = MissingFields()
        self.past = MissingFields()

        for s in self.currentSessions:
            m = self.findMissingFields(s)
            self.current += m #self.findMissingFields(s)
        for s in self.pastSessions:
            self.past += self.findMissingFields(s)

        print "%d sessions belonging to proposals in %s" % \
            (len(self.currentSessions), self.semester.semester)
        print "%d sessions belonging to past semesters." % \
            len(self.pastSessions)

        print "Missing Fields for current sessions: "
        print self.current
        print "Missing Fields for past sessions: "
        print self.past
                                                            

    def findMissingFields(self, session):
        return MissingFields(
            grade = self.isNone(session.grade)
          , allocated = self.isNoneOrZero(session.allotment.allocated_time)
          , min_lst = self.isNone(session.target.min_lst)
          , max_lst = self.isNone(session.target.max_lst)
          , weather_type = self.isNone(session.weather_type)
        )

    def isNone(self, v):
        return 1 if v is None else 0

    def isNoneOrZero(self, v):
        return 1 if v is None or v == 0 else 0
     
if __name__ == '__main__':
    st = StatusReport(semester = '12B')
    st.reportMissingFields()


