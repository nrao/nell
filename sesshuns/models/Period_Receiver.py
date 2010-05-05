from django.db import models
from Period    import Period
from Receiver  import Receiver

class Period_Receiver(models.Model):
    period   = models.ForeignKey(Period)
    receiver = models.ForeignKey(Receiver)

    class Meta:
        db_table  = "periods_receivers"
        app_label = "sesshuns"
