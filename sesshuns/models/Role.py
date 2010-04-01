from django.db                 import models

class Role(models.Model):
    role = models.CharField(max_length = 32)

    class Meta:
        db_table  = "roles"
        app_label = "sesshuns"

    def __unicode__(self):
        return self.role

