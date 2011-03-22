from django.db                 import models

class ExplorerConfiguration(models.Model):
    name    = models.CharField(max_length = 256)
    type    = models.IntegerField()
    tab     = models.CharField(max_length = 256)

    class Meta:
        db_table  = "explorer_configurations"
        app_label = "scheduler"

EXPLORER_CONFIG_TYPE_COLUMN = 0
EXPLORER_CONFIG_TYPE_FILTER = 1
