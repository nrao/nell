from django.db  import models
from sesshuns.models.common     import first

class Receiver(models.Model):
    name         = models.CharField(max_length = 32)
    abbreviation = models.CharField(max_length = 32)
    freq_low     = models.FloatField(help_text = "GHz")
    freq_hi      = models.FloatField(help_text = "GHz")

    class Meta:
        db_table  = "receivers"
        app_label = "scheduler"

    def __unicode__(self):
        return self.name

    def full_description(self):
        return "(%s) %s: %5.2f - %5.2f" % (self.abbreviation
                                         , self.name
                                         , self.freq_low
                                         , self.freq_hi)

    def jsondict(self):
        return self.abbreviation

    def in_band(self, frequency):
        "Does the given freq fall into this rcvr's freq range?"
        return self.freq_low <= frequency <= self.freq_hi

    @staticmethod
    def get_abbreviations():
        return [r.abbreviation for r in Receiver.objects.all()]

    @staticmethod
    def get_rcvr(abbreviation):
        "Convenience method for getting a receiver object by abbreviation"
        return first(Receiver.objects.filter(abbreviation = abbreviation))

    #@staticmethod
    #def get_rcvr_by_name(name):
    #    "Convenience method for getting a receiver object by abbreviation"
    #    return first(Receiver.objects.filter(name = name))


