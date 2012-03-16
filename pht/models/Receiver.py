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

# NOTE: this whole class was *initially* copied from Nell

class Receiver(models.Model):
    name         = models.CharField(max_length = 32)
    abbreviation = models.CharField(max_length = 32)
    code         = models.CharField(max_length = 2)
    freq_low     = models.FloatField(help_text = "GHz")
    freq_hi      = models.FloatField(help_text = "GHz")
    #available    = models.BooleanField(default = True)
    #deleted      = models.BooleanField(default = False)

    class Meta:
        db_table  = "pht_receivers"
        app_label = "pht"

    def __unicode__(self):
        return self.name

    def full_description(self):
        return "(%s) %s: %5.2f - %5.2f" % (self.abbreviation
                                         , self.name
                                         , self.freq_low
                                         , self.freq_hi)

    def in_band(self, frequency):
        "Does the given freq fall into this rcvr's freq range?"
        return self.freq_low <= frequency <= self.freq_hi

    def jsonDict(self):
        return {'id'           : self.id
              , 'abbreviation' : self.abbreviation
              , 'name'         : self.name
               }

    @staticmethod
    def jsonDictOptions():
        return [s.jsonDict() for s in Receiver.objects.all().order_by('freq_low')]

    @staticmethod
    def get_abbreviations():
        return [r.abbreviation for r in Receiver.objects.all().order_by('freq_low')]

    @staticmethod
    def get_rcvr(abbreviation):
        "Convenience method for getting a receiver object by abbreviation"
        return Receiver.objects.get(abbreviation = abbreviation)

