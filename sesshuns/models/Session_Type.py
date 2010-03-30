from django.db  import models
from common     import first

class Session_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type
    
    class Meta:
        db_table  = "session_types"
        app_label = "sesshuns"

    @staticmethod
    def get_type(type):
        return first(Session_Type.objects.filter(type = type))

