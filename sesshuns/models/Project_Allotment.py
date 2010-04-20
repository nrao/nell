from django.db  import models

from Project   import Project
from Allotment import Allotment

class Project_Allotment(models.Model):
    project = models.ForeignKey(Project)
    allotment = models.ForeignKey(Allotment)

    class Meta:
        db_table  = "projects_allotments"
        app_label = "sesshuns"

