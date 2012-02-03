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

from Parameter import Parameter
from Session   import Session

class SessionParameter(models.Model):

    session        = models.ForeignKey(Session)
    parameter      = models.ForeignKey(Parameter)
    string_value   = models.CharField(null = True, blank = True, max_length = 2000)
    integer_value  = models.IntegerField(null = True, blank = True)
    float_value    = models.FloatField(null = True, blank = True)
    boolean_value  = models.NullBooleanField(null = True, blank = True)
    datetime_value = models.DateTimeField(null = True, blank = True)

    class Meta:
        db_table  = "pht_session_parameters"
        app_label = "pht"

    def value(self):
        if self.parameter.type == "string":
            return self.string_value
        elif self.parameter.type == "integer":
            return self.integer_value
        elif self.parameter.type == "float":
            return self.float_value
        elif self.parameter.type == "boolean":
            return self.boolean_value
        elif self.parameter.type == "datetime":
            return self.datetime_value
        else:
            return None

    def __str__(self):
        if self.string_value is not None:
            value = self.string_value
        elif self.integer_value is not None:
            value = str(self.integer_value)
        elif self.float_value is not None:
            value = str(self.float_value)
        elif self.boolean_value is not None:
            value = str(self.boolean_value)
        elif self.datetime_value is not None:
            value = str(self.datetime_value)
        else:
            value = ""
        return "%s with value %s for Session (%d)" % (self.parameter
                                                    , value
                                                    , self.session.id)

    def setValue(self, v):
        if self.parameter.type == "string":
            self.string_value = v
        elif self.parameter.type == "integer":
            self.integer_value = v
        elif self.parameter.type == "float":
            self.float_value = v
        elif self.parameter.type == "boolean":
            self.boolean_value = v
        elif self.parameter.type == "datetime":
            self.datetime_value = v
        self.save()
        
