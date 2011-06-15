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

from django.db   import models

class Period_State(models.Model):
    name         = models.CharField(max_length = 32)
    abbreviation = models.CharField(max_length = 32)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table  = "period_states"
        app_label = "scheduler"

    def jsondict(self):
        return self.abbreviation

    @staticmethod
    def get_abbreviations():
        return [s.abbreviation for s in Period_State.objects.all()]

    @staticmethod
    def get_names():
        return [s.name for s in Period_State.objects.all()]

    @staticmethod
    def get_state(abbr):
        "Short hand for getting state by abbreviation"
        return Period_State.objects.get(abbreviation = abbr)


