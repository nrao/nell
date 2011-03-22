from django.db   import models

class Period_State(models.Model):
    name         = models.CharField(max_length = 32)
    abbreviation = models.CharField(max_length = 32)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table  = "period_states"
        app_label = "scheduler"

    def jsondict(self):
        return self.abbreviation

    @staticmethod
    def get_abbreviations():
        return [s.abbreviation for s in Period_State.objects.all()]

    @staticmethod
    def get_names():
        return [s.name for s in Period_State.objects.all()]

    @staticmethod
    def get_state(abbr):
        "Short hand for getting state by abbreviation"
        return Period_State.objects.get(abbreviation = abbr)


