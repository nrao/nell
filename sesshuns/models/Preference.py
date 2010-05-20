from django.db   import models
from User        import User
from TimeZone    import TimeZone

class Preference(models.Model):

    user     = models.OneToOneField(User)
    timeZone = models.CharField(max_length = 256)

    def __str__(self):
        return "%s (%s)" % (self.user.last_name, self.timeZone)

    class Meta:
        db_table  = "preferences"
        app_label = "sesshuns"
