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

from django.db  import models
from sets       import Set
from datetime   import datetime, timedelta

from Receiver import Receiver

class Receiver_Schedule(models.Model):
    receiver   = models.ForeignKey(Receiver)
    start_date = models.DateTimeField(null = True, blank = True)

    def __unicode__(self):
        return "%s on %s" % \
          ( self.receiver.name
          , self.start_date)

    class Meta:
        db_table  = "receiver_schedule"
        app_label = "scheduler"

    @staticmethod
    def jsondict(schedule):
        jschedule = {}
        for d in schedule:
            jd = None if d is None else d.strftime("%m/%d/%Y")
            jschedule[jd] = [r.jsondict() for r in schedule[d]]
        return jschedule

    @staticmethod
    def jsondict_diff(schedule):
        jsonlist = []
        for day, up, down in schedule:
            jd = None if day is None else day.strftime("%m/%d/%Y")
            jup   = [r.jsondict() for r in up]
            jdown = [r.jsondict() for r in down]
            jsonlist.append(dict(day = jd, up = jup, down = jdown))
        return dict(diff_schedule = jsonlist)    

    @staticmethod
    def diff_schedule(schedule):
        """
        Given a schedule (produced from 'extract_schedule') produces a 
        logically equivalent schedule, but in the form of deltas: it shows
        for each listed date, what rcvrs are coming up and going down.
        """
        diff = []
        # sort the schedule
        sch = sorted(schedule.items())
        prevRcvrs = []
        for day, rcvrs in sch:
            up = [r for r in rcvrs if r not in prevRcvrs]
            down = [r for r in prevRcvrs if r not in rcvrs]
            prevRcvrs = rcvrs
            diff.append((day, up, down))
        return diff

    @staticmethod
    def extract_diff_schedule(startdate = None, days = None):
        sch = Receiver_Schedule.extract_schedule(startdate, days)
        return Receiver_Schedule.diff_schedule(sch)

    @staticmethod
    def extract_schedule(startdate = None, days = None):
        """
        Returns the entire receiver schedule starting at 'startdate' and
        ending 'days' after the 'startdate'.  The schedule is of the form:
        {
           start_date : [<receivers available>]
        }
        where start_date is a datetime object and [<receivers available>] is
        a list of Receiver objects.
        """
        startdate = startdate or datetime(2009, 10, 1, 0, 0, 0)
        schedule  = dict()
        prev      = Receiver_Schedule.previousDate(startdate)

        if prev is None:
            schedule[startdate] = [] # Empty schedule on/before this date
            prev = startdate

        if days is not None:
            enddate = startdate + timedelta(days = days)
            rs = Receiver_Schedule.objects.filter(
                                          start_date__gte = prev
                                                 ).filter(
                                          start_date__lte = enddate).order_by("receiver")
        else:
            rs = Receiver_Schedule.objects.filter(start_date__gte = prev).order_by("receiver")

        for s in rs:
            schedule.setdefault(s.start_date, []).append(s.receiver)

        return schedule

    @staticmethod
    def previousDate(date):
        try:
            prev = Receiver_Schedule.objects.filter(start_date__lt = date).order_by('-start_date')[0].start_date
        except IndexError:
            prev = None

        return prev
 
    @staticmethod
    def mostRecentDate(date):
        "Identical to previous date, but includes given date"
        try:
            prev = Receiver_Schedule.objects.filter(start_date__lte = date).order_by('-start_date')[0].start_date
        except IndexError:
            prev = None

        return prev

    @staticmethod
    def available_rcvrs_end_of_day(date):
        dt = Receiver_Schedule.mostRecentDate(date)
        return Receiver_Schedule.available_receivers(dt)

    @staticmethod
    def available_rcvrs_start_of_day(date):
        dt = Receiver_Schedule.previousDate(date)
        return Receiver_Schedule.available_receivers(dt)
        
    @staticmethod
    def available_receivers(date):
        "Returns rcvrs given rcvr change date"

        if date is not None:
            schd = Receiver_Schedule.objects.filter(start_date = date)
            rcvrs = [p.receiver for p in schd]
        else:
            rcvrs = []
        return rcvrs    

    @staticmethod
    def toggle_rcvr(startDt, rcvr, endDt = None):
        """
        Toggles the state of a receiver in the given time range:
        If a receiver has an entry in the given date range, it's removed,
        if not, it's put in.
        """

        endDt = endDt if endDt is not None else startDt

        # first check that the date range is in the schedule (be lazy)
        for dt in [startDt, endDt]:
            rs = Receiver_Schedule.objects.filter(start_date = dt)
            if len(rs) == 0:
                return (False, "Date not in Receiver Schedule: %s" % dt)

        # get the schedule that just covers this time range
        days = (endDt - startDt).days + 1
        schd = Receiver_Schedule.extract_schedule(startdate = startDt
                                                , days = days)
        dates = schd.keys()
        dates.sort()
        for dt in dates:
            if dt >= startDt and dt <= endDt:
                # toggle the given rcvr:
                if rcvr in schd[dt]:
                    # remove it
                    rs = Receiver_Schedule.objects.get(start_date = dt, receiver = rcvr)
                    rs.delete()                                    
                else:
                    # add it
                    rs = Receiver_Schedule(start_date = dt, receiver = rcvr)
                    rs.save()

        return (True, None)

    @staticmethod
    def add_date(date):
        "Adds new date to the schedule, inited off the previous date"

         # first check that this date is NOT in the schedule
        rs = Receiver_Schedule.objects.filter(start_date = date)
        if len(rs) > 0:
            return (False, "Date is already in Receiver Schedule: %s" % date)

        prevDate = Receiver_Schedule.previousDate(date)
        if prevDate is None:
            return (False, "Cannot add date earlier then 2009")

        # the new date in the schedule is identical to the previous one
        schd = Receiver_Schedule.extract_schedule(startdate=prevDate)
        rcvrs = schd[prevDate]
        for r in rcvrs:
            rs = Receiver_Schedule(start_date = date, receiver = r)
            rs.save()

        return (True, None)   

    @staticmethod
    def delete_date(date):
        "Remove all entries for the given date, and change subsequent schedule"
 
        # first check that this date is in the schedule
        rs = Receiver_Schedule.objects.filter(start_date = date)
        if len(rs) == 0:
            return (False, "Date is not in Receiver Schedule: %s" % date)

        # now we can clean up
        rs = Receiver_Schedule.objects.filter(start_date = date)
        for r in rs:
            r.delete()

        return (True, None)    

    @staticmethod
    def shift_date(from_date, to_date):
        "Move all entries for the given date to a new date"

        # make sure the dates given are valid: you aren't allowed to shift
        # a date beyond the neighboring dates
        # NOTE: ensure you get all dates you need by explicity starting way back
        start = from_date - timedelta(days = 365)
        schedule = Receiver_Schedule.extract_schedule(startdate = start)
        dates = sorted(schedule.keys())
        if from_date not in dates:
            return (False, "Original date not in Receiver Schedule")
        from_index = dates.index(from_date)
        prev_date = dates[from_index-1] if from_index != 0 else None
        next_date = dates[from_index+1] if from_index != len(dates)-1 else None
        if prev_date is None or next_date is None or to_date >= next_date or to_date <= prev_date:
            return (False, "Cannot shift date to or past other dates")

        # we must be clear to shift the date    
        rs = Receiver_Schedule.objects.filter(start_date = from_date)
        for r in rs:
            r.start_date = to_date
            r.save()
        
        return (True, None)

    @staticmethod
    def get_receiver_blackout_ranges(required, start, end):
        """
        Returns a list of tuples of the form (start, end) where
        start and end are datetime objects that denote the 
        beginning and ending of a period where no receivers are available
        for the required receivers of sessions.  
        If there is a receiver available
        at all times for any session, an empty list is returned. 
        """

        schedule = Receiver_Schedule.extract_schedule(start, (end - start).days)
        if schedule == {}: # No receiver schedule present!
           return [(start, None)]
    
        # Go through the schedule and determine blackout ranges.
        ranges = []
        for date, receivers in sorted(schedule.items()):
            receivers = Set(receivers)
            if not any(all(Set(g.receivers.all()).intersection(receivers) \
                        for g in set) for set in required):
                # No session has receivers available. Begin drought.
                if not ranges or ranges[-1][1] is not None:
                    ranges.append((date, None))
            else:
                # A session has receivers available. End drought, if present.
                if ranges and ranges[-1][1] is None:
                    start, _ = ranges.pop(-1)
                    ranges.append((start, date))
        return ranges
            
