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

class Allotment(models.Model):
    psc_time          = models.FloatField(help_text = "Hours")
    total_time        = models.FloatField(help_text = "Hours")
    max_semester_time = models.FloatField(help_text = "Hours")
    grade             = models.FloatField(help_text = "0.0 - 4.0")

    base_url = "/sesshuns/allotment/"

    def __unicode__(self):
        return "(%d) Total: %5.2f, Grade: %5.2f, PSC: %5.2f, Max: %5.2f" % \
                                       (self.id
                                      , float(self.total_time)
                                      , float(self.grade)
                                      , float(self.psc_time)
                                      , float(self.max_semester_time)) 

    def get_absolute_url(self):
        return "/sesshuns/allotment/%i/" % self.id

    class Meta:
        db_table  = "allotment"
        app_label = "scheduler"
        
