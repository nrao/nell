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

from django.db                 import models

class Allotment(models.Model):

    repeats        = models.IntegerField(null = True)
    requested_time = models.FloatField(null = True) # hrs
    allocated_time = models.FloatField(null = True) # hrs
    allocated_repeats = models.IntegerField(null = True, default = 1) # hrs
    semester_time  = models.FloatField(null = True) # hrs
    period_time    = models.FloatField(null = True) # hrs
    low_freq_time  = models.FloatField(null = True) # hrs
    hi_freq_1_time = models.FloatField(null = True) # hrs
    hi_freq_2_time = models.FloatField(null = True) # hrs

    class Meta:
        db_table  = "pht_allotements"
        app_label = "pht"

    @staticmethod
    def createFromSqlResult(result):
        """
        Creates a new Allotment instance initialized using the request from
        an SQL query.
        """

        allotment = Allotment(requested_time = result['SESSION_TIME']
                            , repeats = result['REPEATS']
                             )
        allotment.save()
        return allotment
