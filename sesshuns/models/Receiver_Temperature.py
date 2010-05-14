from django.db  import models

from Receiver import Receiver
from common            import *

class Receiver_Temperature(models.Model):
    receiver    = models.ForeignKey(Receiver)
    frequency   = models.FloatField(help_text = "GHz")
    temperature = models.FloatField(help_text = "K")

    def __unicode__(self):
        return "%s at %f is %f" % \
          ( self.receiver.name
          , self.frequency
          , self.temperature)

    class Meta:
        db_table  = "receiver_temperatures"
        app_label = "sesshuns"

    def jsondict(self):
        return {"id"            : self.id
              , "receiver"      : self.receiver.name
              , "frequency"     : self.frequency
              , "temperature"   : self.temperature
               }

