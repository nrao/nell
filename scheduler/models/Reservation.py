from django.db import models

from User import User

class Reservation(models.Model):
    user       = models.ForeignKey(User)
    start_date = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")
    end_date   = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")

    def __str__(self):
        return "Reservation for %s: %s to %s" % (self.user
                                             , self.start_date
                                             , self.end_date)

    class Meta:
        db_table  = "reservations"
        app_label = "scheduler"

