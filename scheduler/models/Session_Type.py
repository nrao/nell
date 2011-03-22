from django.db  import models

class Session_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type
    
    class Meta:
        db_table  = "session_types"
        app_label = "scheduler"

    @staticmethod
    def get_type(type):
        return Session_Type.objects.get(type = type)

