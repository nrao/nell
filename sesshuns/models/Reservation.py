from django.db import models

from User import User

class Reservation(models.Model):
    user       = models.ForeignKey(User)
    start_date = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")
    end_date   = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")

    class Meta:
        db_table  = "reservations"
        app_label = "sesshuns"

