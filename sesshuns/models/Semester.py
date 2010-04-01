from django.db  import models
from datetime   import datetime
import calendar

class Semester(models.Model):
    semester = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.semester

    def start(self):
        # A starts in February, B in June, C in October
        start_months = {"A": 2, "B": 6, "C": 10}

        year  = 2000 + int(self.semester[:2])
        month = start_months[self.semester[-1]]

        return datetime(year, month, 1)

    def end(self):
        # A ends in May, B in September, C in January
        end_months = {"A": 5, "B": 9, "C": 1}

        year   = 2000 + int(self.semester[:2])
        if self.semester[-1] == "C":
            year += 1
        month  = end_months[self.semester[-1]]
        _, day = calendar.monthrange(year, month)

        return datetime(year, month, day)

    def eventjson(self, id):
        return {
            "id"   : id
          , "title": "".join(["Start of ", self.semester])
          , "start": self.start().isoformat()
        }

    @staticmethod
    def getFutureSemesters(today = datetime.today()):
        "Returns a list of Semesters that start on or after the given date."
        return sorted([s for s in Semester.objects.all() if s.start() >= today]
                     , lambda x, y: cmp(x.start(), y.start()))

    @staticmethod
    def getPreviousSemesters(today = datetime.today()):
        """
        Returns a list of Semesters that occur prior to the given date
        not including the current semester as defined by the given date.
        """
        return sorted([s for s in Semester.objects.all() if s.start() <= today]
                     , lambda x, y: cmp(x.start(), y.start()))

    @staticmethod
    def getCurrentSemester(today = datetime.today()):
        "Returns the current Semester."
        return Semester.getPreviousSemesters(today)[-1]

    class Meta:
        db_table  = "semesters"
        app_label = "sesshuns"

