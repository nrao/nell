from django.db  import models
from datetime   import timedelta

class TimeZone(models.Model):
    timeZone = models.CharField(max_length = 128)

    def __str__(self):
        return self.timeZone
        
    def utcOffset(self):
        "Returns a timedelta representing the offset from UTC."
        offset = int(self.timeZone[4:]) if self.timeZone != "UTC" else 0
        return timedelta(hours = offset)
 
    class Meta:
        db_table  = "timezones"
        app_label = "sesshuns"
        
