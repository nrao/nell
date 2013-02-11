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

from django.core.exceptions import ObjectDoesNotExist
from django.db              import models
from datetime               import datetime, timedelta

from utilities.TimeAgent    import adjustDateTimeTz, dst_boundaries, truncateDt, tz_to_tz
from User                   import User
from Project                import Project
from Blackout_Sequence      import Blackout_Sequence
from Repeat                 import Repeat

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
                month = 1;
                year = dt.year + 1
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

        self.description = description

        self.clear_sequences()
        self.timeZone = tz

        # Simple case: 'Once'
        if not repeat or repeat.repeat == 'Once':
            if repeat == None:
                repeat = Repeat.objects.get(repeat = 'Once')

            # NOTE: Strip out TZ info, just in case the database has
            # not been altered to use timestamp without time zone.
            # The tzinfo is UTC, as these times are provided as UTC
            # representations of the user's desired local time, and
            # that is what we want.  However, if the tzinfo is not set
            # to None and the database has not been altered then these
            # get set to the local time by the time it is saved to a
            # sequence
            start = start.replace(tzinfo = None)
            end = end.replace(tzinfo = None)
            
            bs = Blackout_Sequence(start_date = start, end_date = end,
                                   repeat = repeat, until = until)
            self.blackout_sequence_set.add(bs)
        else:
            # We're looking at a series of blackouts that may continue
            # past a DST boundary.  In addition, one of the blackouts
            # may itself straddle the DST bound.  The blackout
            # sequences must be represented in the DB as UTC values,
            # since Antioch doesn't have the timezone libraries Python
            # has.  But since blackouts are a user concept, they must
            # be continuous in the local time zone (i.e. 8:00 AM local
            # time, before or after DST starts).  Thus the UTC values
            # will change as the series crosses DST bounds.  In
            # addition we are looking at the possibility that one of
            # the blackout instances itself will cross the DST
            # bound. Through all this we wish to maintain the proper
            # phase and spacing of the repeating blackouts. This
            # diagram represents this idea:
            #
            #                    DST                             DST
            # |---|---------------|-|=|=======================|===|=|----------------|
            # S   E    ...        S   E      ...              S   E         ...      U
            #
            #     Sequence 1
            # |---|---------------|
            # S   E               U
            #                     Seq 2
            #                     |---|
            #                     S   E
            #                        Rep.
            #                     |-------|    Sequence 3
            #                             |---|-------------------|
            #                             S   E   ...             U
            #                                                    Rep.
            #                                                 |-------|   Sequence 4
            #                                                         |---|----------|
            #                                                         S   E   ...    U
            #
            # Naive algorithm:
            #
            # 1) Get DST bounds over desired time range
            # 2) Map blackout instances (SE) over entire range
            # 3) Iterate over SEs and check:
            #    a) Has S crossed over a DST?
            #       i) If so, previous E becomes U of last sequence; save sequence,
            #          start another working sequence, and go to next iteration.
            #    b) Has E crossed over a DST?
            #       i) If so, previous E can become U of last sequence, as above, but:
            #          Create and save a 'Once' sequence with current S and E; next SE
            #          becomes working sequence, and go to next iteration
            #    c) if we got this far, until of current SE becomes until of working
            #       sequence

            dstb =  dst_boundaries(tz, start, until)
            dst_date = None

            if len(dstb):
                dstb.reverse()
                dst_date = tz_to_tz(dstb.pop(), 'UTC', tz, naive = True)

            localstart = tz_to_tz(start, 'UTC', tz, naive = True)
            localend = tz_to_tz(end, 'UTC', tz, naive = True)
            localuntil = tz_to_tz(until, 'UTC', tz, naive = True)
            days = truncateDt(localend) - truncateDt(localstart)
            periodicity = repeat.repeat
            bls = []

            while localstart <= localuntil:
                bls.append([localstart, localend, periodicity, localuntil])
                localstart, localend = self.get_next_period(localstart, localend, periodicity)

            seq = bls[0]
            seqs = []

            for i in range(0, len(bls)):
                if dst_date:  # if we are contending with a DST boundary...
                    # keep DST boundary date current
                    if seq[0] > dst_date:
                        if len(dstb):
                            dst_date = tz_to_tz(dstb.pop(), 'UTC', tz, naive = True)
                        else:
                            dst_date = None
                            continue

                    if bls[i][0] > dst_date:      # start crosses dst_date
                        seq[3] = bls[i - 1][1]    # set until to previous instance's end
                        seqs.append(seq)          # save
                        seq = bls[i]
                        continue
                    if bls[i][1] > dst_date:      # start hasn't, but end has crossed
                        seq[3] = bls[i - 1][1]    # dst_date; set until to previous end
                        seqs.append(seq)
                        seq = bls[i]
                        seq[2] = 'Once'
                        seqs.append(seq)

                        if i < len(bls):
                            seq = bls[i + 1]
                        continue

                seq[3] = bls[i][3]

            seqs.append(seq) # get the last sequence

            for i in seqs:
                bs = Blackout_Sequence(start_date = tz_to_tz(i[0], tz, 'UTC', True),
                                       end_date = tz_to_tz(i[1], tz, 'UTC', True),
                                       repeat = Repeat.objects.get(repeat = i[2]),
                                       until = tz_to_tz(i[3], tz, 'UTC', True))
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
        bs = self.blackout_sequence_set.order_by("start_date") 
        return bs[0].start_date if len(bs) > 0 else None

    def getStartDateTZ(self, tz = None):
        if not tz:
            tz = self.timeZone
        return tz_to_tz(self.getStartDate(), 'UTC', tz)

    def getEndDate(self):
        bs = self.blackout_sequence_set.order_by("start_date") 
        return bs[0].end_date if len(bs) > 0 else None

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
        until = self.getUntil()
        return tz_to_tz(until, 'UTC', tz) if until is not None else until

    def getRepeat(self):
        bs = self.blackout_sequence_set.order_by("start_date") 
        if len(bs) > 0:
            repeat = bs[0].repeat.repeat
        else: 
            return None

        # 'repeat' should now have the proper repeat.  However, if
        # this is a non-'Once' repeating sequence, and there are more
        # than one sequence, it is possible that the first one is a
        # 'Once' sequence if the initial blackout straddles the DST
        # boundary.  In this case, use the next sequence to get the
        # repeat information.
        if repeat == 'Once' and self.blackout_sequence_set.count() > 1:
            repeat = self.blackout_sequence_set.order_by("start_date")[1].repeat.repeat

        return repeat

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

        # short-circuit if calstart-calend outside of range
        start = self.getStartDate()
        end = self.getEndDate() if self.getRepeat() == 'Once' else self.getUntil()

        if end < calstart or start > calend:
            return []

        dates = []

        for seq in self.blackout_sequence_set.order_by("start_date"):
            start       = seq.start_date
            end         = seq.end_date
            until       = min(seq.until, calend) if seq.until else calend
            periodicity = seq.repeat.repeat

            # take care of simple scenarios first
            if start is None or end is None:
                continue  # ignore this sequence

            if periodicity == "Once":
                # A 'Once' sequence may belong to a 'Once' blackout,
                # or may be a DST transition sequence in a repeat
                # blackout.  The date test is for the latter, but will
                # work in either case.
                if not (end < calstart or start > calend):
                    dates.append((start, end))                    
            else:
                # Check to see if this *sequence* (not the entire
                # blackout) is outside the calstart-calend range.  If
                # so, skip to next sequence.
                if until < calstart or start > calend:
                    continue
                # Otherwise, get the dates that are within the range.
                while start <= until:
                    if start >= calstart:
                        dates.append((start, end))

                    start, end = self.get_next_period(start, end, periodicity)

        if local_timezone:
            return map(lambda x: (tz_to_tz(x[0], 'UTC', self.timeZone, True),\
                                      tz_to_tz(x[1], 'UTC', self.timeZone, True)), dates)
        else:
            return dates

    class Meta:
        db_table  = "blackouts"
        app_label = "scheduler"
