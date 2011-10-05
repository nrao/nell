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

from django.db  import models
from datetime   import datetime
import calendar

class Semester(models.Model):
    semester = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.semester

    def start(self):
        """
        # start and end dates for semesters follow a simple pattern:
        # before 11A:
        # yyA : (yy,  2, 1) to (yy,   5, 31) # 4 months 
        # yyB : (yy,  6, 1) to (yy,   9, 30) # 4 months
        # yyC : (yy, 10, 1) to (yy+1, 1, 31) # 4 months
        # 11A and 11B are fucked up:
        # 11A : (2011, 2, 1) to (2011, 6, 30) # 5 months 
        # 11B : (2011, 7, 1) to (2012, 1, 31) # 7 months
        # after 11B:
        # yyA : (yy,  2, 1) to (yy,   7, 31) # 6 months
        # yyB : (yy,  8, 1) to (yy+1, 1, 31) # 6 months
        """
        # special transition cases from trimesters (prior to '11) to
        # semesters (during '11):

        if self.semester == "11A":
            return datetime(2011,2,1)

        if self.semester == "11B":
            return datetime(2011,7,1)

        year = 2000 + int(self.semester[:2])

        if year <= 2010: # old trimesters; some db objects will have these
            # A starts in February, B in June, C in October
            start_months = {"A": 2, "B": 6, "C": 10}
        else:          # new semesters
            # A starts in February, B in August.
            start_months = {"A": 2, "B": 8}

        month = start_months[self.semester[-1]]
        return datetime(year, month, 1)

    def end(self):
        # special transition cases from trimesters (prior to '11) to
        # semesters (during '11):

        if self.semester == "11A":
            return datetime(2011,6,30)

        if self.semester == "11B":
            return datetime(2012,1,31)

        # ex: 09A -> 2009
        year = 2000 + int(self.semester[:2])

        # how to compute the month and year from the semester letter?
        if year <= 2010: # old trimesters; some db objects will have these
            end_months = {"A": 5, "B": 9, "C": 1}
            years = {"A": year, "B": year, "C": year+1}
        else:          # new semesters
            end_months = {"A": 7, "B": 1}
            years = {"A": year, "B": year+1}
        
        # now actually compute the date
        letter = self.semester[-1]
        year = years[letter]
        month  = end_months[letter]
        _, day = calendar.monthrange(year, month)

        return datetime(year, month, day)

    def eventjson(self, id):
        return {
            "id"   :     id
          , "title":     "".join(["Start of ", self.semester])
          , "start":     self.start().isoformat()
          , "className": 'semester'
        }

    @staticmethod
    def getFutureSemesters(today = datetime.today()):
        "Returns a list of Semesters that start on or after the given date."
        return sorted([s for s in Semester.objects.all() if s.start() >= today]
                     , lambda x, y: cmp(x.start(), y.start()))

    @staticmethod
    def getPreviousSemesters(today = datetime.today()):
        """
        Returns a list of Semesters that occur prior to the given date
        not including the current semester as defined by the given date.
        """
        return sorted([s for s in Semester.objects.all() if s.start() <= today]
                     , lambda x, y: cmp(x.start(), y.start()))

    @staticmethod
    def getCurrentSemester(today = datetime.today()):
        "Returns the current Semester."
        return Semester.getPreviousSemesters(today)[-1]

    class Meta:
        db_table  = "semesters"
        app_label = "scheduler"

