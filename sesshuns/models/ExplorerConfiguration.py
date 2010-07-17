from django.db                 import models

class ExplorerConfiguration(models.Model):
    name    = models.CharField(max_length = 256)
    tab     = models.CharField(max_length = 256)

    class Meta:
        db_table  = "explorer_configurations"
        app_label = "sesshuns"
