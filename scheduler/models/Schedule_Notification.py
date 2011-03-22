from django.db  import models

class Schedule_Notification(models.Model):
    date   = models.DateTimeField(null = True, blank = True)

    class Meta:
        db_table  = "schedule_notifications"
        app_label = "scheduler"

