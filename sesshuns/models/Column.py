from django.db             import models
from ExplorerConfiguration import ExplorerConfiguration

class Column(models.Model):
    name = models.CharField(max_length = 256)
    explorer_configuration = models.ForeignKey(ExplorerConfiguration)

    class Meta:
        db_table  = "columns"
        app_label = "sesshuns"
