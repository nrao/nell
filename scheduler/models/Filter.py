from django.db             import models
from ExplorerConfiguration import ExplorerConfiguration

class Filter(models.Model):
    name  = models.CharField(max_length = 256)
    value = models.CharField(max_length = 256)
    explorer_configuration = models.ForeignKey(ExplorerConfiguration)

    class Meta:
        db_table  = "filters"
        app_label = "scheduler"
