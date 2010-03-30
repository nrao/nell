from django.db   import models

class Project_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type

    class Meta:
        db_table  = "project_types"
        app_label = "sesshuns"

