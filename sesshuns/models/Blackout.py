from django.db   import models
from datetime    import datetime, timedelta

from User        import User
from Repeat      import Repeat

class Blackout(models.Model):
    user         = models.ForeignKey(User)
    start_date   = models.DateTimeField(null = True, blank = True)
    end_date     = models.DateTimeField(null = True, blank = True)
    repeat       = models.ForeignKey(Repeat)
    until        = models.DateTimeField(null = True, blank = True)
    description  = models.CharField(null = True, max_length = 1024, blank = True)

    def __unicode__(self):
        return "%s Blackout for %s: %s - %s" % \
               (self.repeat.repeat, self.user, self.start_date, self.end_date)

    def isActive(self, date = datetime.utcnow()):
        """
        Takes a UTC datetime object and returns a Boolean indicating whether
        this blackout's effective date range is effective on this date.
        """

        if self.start_date is None:
            return False # Never started, not active
        
        if self.start_date >= date:
            return True # Happens in the future

        if not self.end_date and self.start_date <= date:
            return True # Started on/before date, never ends

        if self.start_date <= date and self.end_date >= date:
            return True # Starts on/before date, ends on/after date

        if self.repeat.repeat != "Once":
            if not self.until and self.start_date <= date:
                return True # Started on/before date, repeats forever

            if self.until and self.until >= date and self.start_date <= date:
                return True # Started on/before date, repeats on/after date

        return False

    def generateDates(self, calstart, calend):
        """
        Takes two UTC datetimes representing a period of time on the calendar.
        Returns a list of (datetime, datetime) tuples representing all the
        events generated by this blackout in that period.
        """

        # take care of simple scenarios first
        if self.start_date is None or self.end_date is None:
            return [] # What does it mean to have None in start or end?

        if self.start_date > calend:
            return [] # Outside this time period - hasn't started yet

        start       = self.start_date
        end         = self.end_date
        until       = min(self.until, calend) if self.until else calend
        periodicity = self.repeat.repeat
        dates       = []
        
        if periodicity == "Once":
            dates.append((start, end))
        elif periodicity == "Weekly":
            while start <= until:
                if start >= calstart:
                    dates.append((start, end))

                start = start + timedelta(days = 7)
                end   = end   + timedelta(days = 7)
        elif periodicity == "Monthly":
            while start <= until:
                if start >= calstart:
                    dates.append((start, end))

                if start.month == 12: # Yearly wrap around
                    start.month = 0; start.year = start.year + 1

                start = datetime(year   = start.year
                               , month  = start.month + 1
                               , day    = start.day
                               , hour   = start.hour
                               , minute = start.minute)
                end   = datetime(year   = end.year
                               , month  = end.month + 1
                               , day    = end.day
                               , hour   = end.hour
                               , minute = end.minute)
        return dates

    def eventjson(self, calstart, calend, id = None):
        calstart = datetime.fromtimestamp(float(calstart))
        calend   = datetime.fromtimestamp(float(calend))
        dates    = self.generateDates(calstart, calend)
        title    = "%s: %s" % (self.user.name()
                             , self.description or "blackout")
        return [{
            "id"   : self.id
          , "title": title
          , "start": d[0].isoformat() if d[0] else None
          , "end"  : d[1].isoformat() if d[1] else None
        } for d in dates]

    class Meta:
        db_table  = "blackouts"
        app_label = "sesshuns"
