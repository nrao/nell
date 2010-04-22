from django.db  import models

from Sesshun   import Sesshun
from Parameter import Parameter

class Observing_Parameter(models.Model):
    session        = models.ForeignKey(Sesshun)
    parameter      = models.ForeignKey(Parameter)
    string_value   = models.CharField(null = True, max_length = 64, blank = True)
    integer_value  = models.IntegerField(null = True, blank = True)
    float_value    = models.FloatField(null = True, blank = True)
    boolean_value  = models.NullBooleanField(null = True, blank = True)
    datetime_value = models.DateTimeField(null = True, blank = True)

    class Meta:
        db_table        = "observing_parameters"
        unique_together = ("session", "parameter")
        app_label       = "sesshuns"

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

    def __unicode__(self):
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
        return "%s with value %s for Sesshun (%d)" % (self.parameter
                                                    , value
                                                    , self.session.id)

