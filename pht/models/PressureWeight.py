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

from django.db          import models
from django.core.validators import MinValueValidator, MaxValueValidator

from Semester   import Semester
from PressureWeightCategory import PressureWeightCategory

class PressureWeight(models.Model):

    lst      = models.IntegerField(validators = [MinValueValidator(0), MaxValueValidator(23)])
    value    = models.FloatField()
    category = models.ForeignKey(PressureWeightCategory)
    semester = models.ForeignKey(Semester)

    class Meta:
        db_table  = "pht_pressure_weights"
        app_label = "pht"

    def __str__(self):
        return "Semester: %s Cat.:%s LST: %s Value: %s" % (self.semester.semester, self.category.name, self.lst, self.value)

    @staticmethod
    def GetWeights(semester, category):
        return [pw.value for pw in PressureWeight.objects.filter(semester__semester = semester
                                                               , category__name     = category
                                                               ).order_by('lst')]
    @staticmethod
    def LoadWeights(semester, category, values):
        cat, _ = PressureWeightCategory.objects.get_or_create(name = category)
        sem, _ = Semester.objects.get_or_create(semester = semester)
        for i, v in enumerate(values):
            PressureWeight.objects.create(lst = i, value = v, category = cat, semester = sem)
