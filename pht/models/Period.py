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

from django.db              import models
from django.core.exceptions import ObjectDoesNotExist
from datetime               import datetime, timedelta

from utilities            import AnalogSet
from utilities.TimeAgent  import range_to_days
from utilities.TimeAgent  import timedelta2minutes
from utilities.TimeAgent  import adjustDateTimeTz
from utilities.AnalogSet  import overlaps

#from Session              import Session

class Period(models.Model):
    session    = models.ForeignKey("Session")
    start      = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm")
    duration   = models.FloatField(help_text = "Hours")
    #window     = models.ForeignKey("Window", blank=True, null=True, related_name = "per

    class Meta:
        db_table  = "pht_periods"
        app_label = "pht"
    
    def end(self):
        "The period ends at start + duration"
        return self.start + timedelta(hours = self.duration)

    def on_day(self, day):
        "Does this period ever take place on the specified day (a datetime)?"
        next_day = day + timedelta(days = 1)
        return (self.end() > day) and (self.start < next_day)

    def __unicode__(self):
        return "Period (%d) for Session (%d): %s for %5.2f Hrs" % \
            (self.id, self.session.id, self.start, self.duration)

    def __str__(self):
        return "%s: %s for %5.2f Hrs" % \
            (self.session.name, self.start, self.duration)

    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def display_name(self):
        return self.__str__()
                
