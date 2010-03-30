from django.db  import models

from Project import Project
from User    import User

# TBF: temporary table/class for scheduling just 09B.  We can safely
# dispose of this after 09B is complete.  Delete Me!
class Project_Blackout_09B(models.Model):
    project      = models.ForeignKey(Project)
    requester    = models.ForeignKey(User)
    start_date   = models.DateTimeField(null = True, blank = True)
    end_date     = models.DateTimeField(null = True, blank = True)
    description  = models.CharField(null = True, max_length = 512, blank = True)

    def __unicode__(self):
        return "Blackout for %s: %s - %s" % (self.project.pcode, self.start_date, self.end_date)

    class Meta:
        # Note: using upper case B at the end of this name causes
        # problems with postrgreSQL
        db_table  = "project_blackouts_09b"
        app_label = "sesshuns"

