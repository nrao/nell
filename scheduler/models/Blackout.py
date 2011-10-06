# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from django.core.exceptions   import ObjectDoesNotExist
from django.db   import models
from datetime    import datetime, timedelta

from utilities.TimeAgent import adjustDateTimeTz, dst_boundaries, truncateDt, tz_to_tz
from User        import User
from Project     import Project
from Blackout_Sequence import Blackout_Sequence

class Blackout(models.Model):
    user        = models.ForeignKey(User, null = True)
    project     = models.ForeignKey(Project, null = True)
    description = models.CharField(null = True, max_length = 1024, blank = True)
    timeZone    = models.CharField(null = True, max_length = 256, blank = True)

    def __unicode__(self):
        return "%i: %s Blackout for %s: %s - %s" % \
               (self.id, self.getRepeat(), self.forName(), self.getStartDate(), self.getEndDate())

    def get_next_period(self, start, end, periodicity):
        """
        given 'start', 'end', 'periodicity' returns the next 'start'
        and 'end' according to the periodicity.
        """
        
        def dealWithYearlyWrapAround(dt):
            if dt.month == 12: # Yearly wrap around
                month = 1; year = dt.year + 1
            else:
                month = dt.month + 1
                year  = dt.year
                return month, year

        if periodicity == "Weekly":
            start = start + timedelta(days = 7)
            end   = end   + timedelta(days = 7)
            return (start, end)
        elif periodicity == "Monthly":
            month, year = dealWithYearlyWrapAround(start)
            start = datetime(year   = year
                             , month  = month
                             , day    = start.day
                             , hour   = start.hour
                             , minute = start.minute)
            month, year = dealWithYearlyWrapAround(end)
            end   = datetime(year   = year
                             , month  = month
                             , day    = end.day
                             , hour   = end.hour
                             , minute = end.minute)
            return (start, end)

    
    def clear_sequences(self):
        seq = [s for s in self.blackout_sequence_set.all()]
        self.blackout_sequence_set.clear()

        for s in seq:
            s.delete()

    def initialize(self, tz, start, end, repeat = None, until = None, description = None):
        """
        Initializes a new or current blackout object to the given values.
        tz          : string; time zone for the blackout
        start       : datetime; start date/time, *in UTC*
        end         : datetime; end date/time, *in UTC*
        repeat      : Repeat object; repeat interval.
        until       : datetime; end date for repeat, if used
        description : string; A brief description of the blackout.
        """

        self.save() # the Blackout entry in the database needs an ID
                    # so that blackout sequences can be added.

        # This is where the magic happens.  The date/time sequence is
        # given in UTC, but we have a local timezone.  We will use
        # this to split (if necessary) this sequence into two or more
        # as it crosses over DST boundaries, according to the local
        # timezone.

        if description:
            self.description = description

        self.clear_sequences()
        self.timeZone = tz

        # cant' really do a timedelta (localend - localstart) to
        # determine end of repeated blackouts, as any one of these may
        # straddle a DST transition and the end would be an hour off.
        # Instead, capture the intent of the user: 'end is that day at
        # 20:00'; 'end is 2 weeks from now at 8:00", etc. and recreate
        # those on the repeats.  Keep the timedelta idea at the day
        # granularity; preserve the actual local end time.
        localstart = tz_to_tz(start, 'UTC', tz)
        localend = tz_to_tz(end, 'UTC', tz)
        days = truncateDt(localend) - truncateDt(localstart)

        if repeat and until:
            dates = [start] + dst_boundaries(tz, start, until) + [until]
        else:
            dates = [start, until]

        # now we go from start to first dst bound, first dst to second
        # dst bound, second dst to 'until', etc., creating as many
        # blackout sequences as necessary.  For this we keep the local
        # start time--which is the user intent--changing the dates as
        # needed for each sequence, then converting the resulting
        # datetimes back to UTC.  When combining the new sequence
        # dates with the local start & end time we must ensure we use
        # the *local* representation of the date, not UTC date. This
        # should keep any ambiguities from arising if the local time
        # is such that the UTC date is the next day.  But we keep the
        # local *time* as specified by the user for all sequences!  If
        # we don't do this the UT time will not vary, the local time
        # will.

        for i in range(0, len(dates) - 1):
            bs = Blackout_Sequence()
            loc_date = tz_to_tz(dates[i], 'UTC', tz)
            i_start_date = datetime(loc_date.year, loc_date.month, loc_date.day,
                                    localstart.hour, localstart.minute)
            i_end_date = (truncateDt(i_start_date) + days)\
                .replace(hour = localend.hour, minute = localend.minute)
             # Now go back to UTC to save the sequences in the database:
            bs.start_date = tz_to_tz(i_start_date, tz, 'UTC', naive = True)
            bs.end_date = tz_to_tz(i_end_date, tz, 'UTC', naive = True)
            bs.repeat = repeat
            bs.until = dates[i + 1]
            self.blackout_sequence_set.add(bs)

        self.save()

    def checkValidUser(self):
        assert ((self.project is not None) or (self.user is not None))
        assert (not ((self.project is None) and (self.user is None)))

    def forUser(self):
        "Assumes one of [user,project] is NULL"
        self.checkValidUser()
        return self.project is None

    def forUrlId(self):
        "Returns the url id for whom this blackout is for"
        return self.user.id if self.forUser() else self.project.pcode

    def forName(self):
        """
        Returns the name for whom this blackout is for:
           * user - display name
           * project - pcode
        """
        return self.user.display_name() if self.forUser() else self.project.pcode

    def isActive(self, date = datetime.utcnow()):
        """
        Takes a UTC datetime object and returns a Boolean indicating whether
        this blackout's effective date range is effective on this date.
        """

        if self.getStartDate() is None:
            return False # Never started, not active

        if self.getRepeat() == "Once" and self.getEndDate() and self.getEndDate() <= date:
            return False # Done

        if self.getStartDate() >= date:
            return True # Happens in the future

        if not self.getEndDate() and self.getStartDate() <= date:
            return True # Started on/before date, never ends

        if self.getStartDate() <= date and self.getEndDate() >= date:
            return True # Starts on/before date, ends on/after date

        if self.getRepeat() != "Once":
            if not self.getUntil() and self.getStartDate() <= date:
                return True # Started on/before date, repeats forever

            if self.getUntil() and self.getUntil() >= date and self.getStartDate() <= date:
                return True # Started on/before date, repeats on/after date

        return False

    def getStartDate(self):
        return self.blackout_sequence_set.order_by("start_date")[0].start_date

    def getStartDateTZ(self, tz = None):
        if not tz:
            tz = self.timeZone
        return tz_to_tz(self.getStartDate(), 'UTC', tz)

    def getEndDate(self):
        return self.blackout_sequence_set.order_by("start_date")[0].end_date

    def getEndDateTZ(self, tz = None):
        if not tz:
            tz = self.timeZone
        return tz_to_tz(self.getEndDate(), 'UTC', tz)

    def getUntil(self):
        c = self.blackout_sequence_set.count()
        return self.blackout_sequence_set.order_by("start_date")[c - 1].until

    def getUntilTZ(self, tz = None):
        if not tz:
            tz = self.timeZone
        return tz_to_tz(self.getUntil(), 'UTC', tz)

    def getRepeat(self):
        return self.blackout_sequence_set.order_by("start_date")[0].repeat.repeat

    def getDescription(self):
        return self.description

    def generateDates(self, calstart, calend, local_timezone = False):
        """
        Takes two UTC datetimes representing a period of time on the calendar.
        Returns a list of (datetime, datetime) tuples representing all the
        events generated by this blackout in that period.
        calstart       : the start datetime
        calend         : the end datetime
        local_timezone : boolean, if True results are in the local timezone;
                         if False, in UTC.
        """

        dates = []

        for seq in self.blackout_sequence_set.order_by("start_date"):
            start       = seq.start_date
            end         = seq.end_date
            until       = min(seq.until, calend) if seq.until else calend
            periodicity = seq.repeat.repeat

            # take care of simple scenarios first
            if start is None or end is None:
                return [] # What does it mean to have None in start or end?

            # see what other conditions we can reject
            if periodicity == "Once":
                if (start > calend or end < calstart):
                    return [] # Outside time period - hasn't started or already done
            else:
                if (start > calend or end < calstart) and until < calstart:
                    return [] # Outside time period - hasn't started or already done

            # def dealWithYearlyWrapAround(dt):
            #     if dt.month == 12: # Yearly wrap around
            #         month = 1; year = dt.year + 1
            #     else:
            #         month = dt.month + 1
            #         year  = dt.year
            #     return month, year

            if periodicity == "Once":
                dates.append((start, end))

            while start <= until:
                if start >= calstart:
                    dates.append((start, end))

                    start, end = self.get_next_period(start, end, periodicity)
            # elif periodicity == "Weekly":
            #     while start <= until:
            #         if start >= calstart:
            #             dates.append((start, end))

            #         start = start + timedelta(days = 7)
            #         end   = end   + timedelta(days = 7)
            # elif periodicity == "Monthly":
            #     while start <= until:
            #         if start >= calstart:
            #             dates.append((start, end))

            #         month, year = dealWithYearlyWrapAround(start)
            #         start = datetime(year   = year
            #                        , month  = month
            #                        , day    = start.day
            #                        , hour   = start.hour
            #                        , minute = start.minute)
            #         month, year = dealWithYearlyWrapAround(end)
            #         end   = datetime(year   = year
            #                        , month  = month
            #                        , day    = end.day
            #                        , hour   = end.hour
            #                        , minute = end.minute)

        if local_timezone:
            return map(lambda x: (tz_to_tz(x[0], 'UTC', self.timeZone, True),\
                                      tz_to_tz(x[1], 'UTC', self.timeZone, True)), dates)
        else:
            return dates

    def eventjson(self, calstart, calend, id = None, tz = None):
        calstart = datetime.fromtimestamp(float(calstart))
        calend   = datetime.fromtimestamp(float(calend))
        dates    = self.generateDates(calstart, calend)
        if tz is not None:
            dates = [(adjustDateTimeTz(tz, s), adjustDateTimeTz(tz, e)) for s, e in dates]
        title    = "%s: %s" % (self.forName() #self.user.name()
                             , self.getDescription() or "blackout")
        return [{
            "id"   :      self.id
          , "title":      title
          , "start":      d[0].isoformat() if d[0] else None
          , "end"  :      d[1].isoformat() if d[1] else None
          , "className": 'blackout'
        } for d in dates]

    class Meta:
        db_table  = "blackouts"
        app_label = "scheduler"
