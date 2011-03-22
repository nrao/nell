from django.db  import models

class Allotment(models.Model):
    psc_time          = models.FloatField(help_text = "Hours")
    total_time        = models.FloatField(help_text = "Hours")
    max_semester_time = models.FloatField(help_text = "Hours")
    grade             = models.FloatField(help_text = "0.0 - 4.0")
    ignore_grade      = models.NullBooleanField(null = True, default = False, blank = True)

    base_url = "/sesshuns/allotment/"

    def __unicode__(self):
        return "(%d) Total: %5.2f, Grade: %5.2f, PSC: %5.2f, Max: %5.2f" % \
                                       (self.id
                                      , float(self.total_time)
                                      , float(self.grade)
                                      , float(self.psc_time)
                                      , float(self.max_semester_time)) 

    def get_absolute_url(self):
        return "/sesshuns/allotment/%i/" % self.id

    class Meta:
        db_table  = "allotment"
        app_label = "scheduler"
        
