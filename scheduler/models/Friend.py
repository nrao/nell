from django.db import models
from sesshuns.models.common    import *
from Project   import Project
from User      import User

class Friend(models.Model):
    project                = models.ForeignKey(Project)
    user                   = models.ForeignKey(User)
    required               = models.BooleanField(default = False)

    def __unicode__(self):
        return "Friend %s (%d) for %s; required : %s" % \
            ( self.user
            , self.user.id
            , self.project.pcode
            , self.required )

    def name(self):
        return self.user

    def project_name(self):
        return self.project.pcode

    def projectBlackouts(self):
        return sorted([b for b in self.user.blackout_set.all()
                       if b.isActive()])
    
    class Meta:
        db_table  = "friends"
        app_label = "scheduler"

