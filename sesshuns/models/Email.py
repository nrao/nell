from django.db  import models
from User       import User

# TBF: Remove this when we are sure we don't need this local email
#      table anymore.
class Email(models.Model):
    user  = models.ForeignKey(User)
    email = models.CharField(max_length = 255)

    class Meta:
        db_table  = "emails"
        app_label = "sesshuns"

