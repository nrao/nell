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

from django.db                 import models

class SessionGrade(models.Model):

    grade = models.CharField(max_length = 32)

    class Meta:
        db_table  = "pht_session_grades"
        app_label = "pht"

    def __str__(self):
        return "%s" % self.grade

    def jsonDict(self):
        return {'id'   : self.id
              , 'grade' : self.grade
               }

    def isPassing(self):
        "Only A, B, C is a passing grade"
        return self.grade in ['A', 'B', 'C']

    @staticmethod
    def jsonDictOptions():
        return [ot.jsonDict() for ot in SessionGrade.objects.all()]

