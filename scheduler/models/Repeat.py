from django.db   import models

class Repeat(models.Model):
    repeat = models.CharField(max_length = 32)

    def __str__(self):
        return self.repeat

    class Meta:
        db_table  = "repeats"
        app_label = "scheduler"
        
