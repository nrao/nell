from django.db  import models

from Receiver import Receiver
from common            import *

class Receiver_Schedule(models.Model):
    receiver   = models.ForeignKey(Receiver)
    start_date = models.DateTimeField(null = True, blank = True)

    def __unicode__(self):
        return "%s on %s" % \
          ( self.receiver.name
          , self.start_date)

    class Meta:
        db_table  = "receiver_schedule"
        app_label = "sesshuns"

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
                                          start_date__lte = enddate)
        else:
            rs = Receiver_Schedule.objects.filter(start_date__gte = prev)

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
    def change_schedule(date, up, down, end_of_day = False):
        """
        Here we change the receiver schedule according to the given rcvrs
        that go up and down on the given date.  Uses extract schedule to 
        determine what rcvrs are up on this given date so that the rcvr 
        schedule can be changed using these deltas.  Raises errors if rcvrs are
        specified to go up that are already up, or down that aren't up.
        """
       
        # TBF: how to error check before creating new RS entry?
        # TBF: this code is twice as long as it should be - there
        # are patterns for up & down params that can be refactored out
        # TBF: won't remove the commented out prints until we know we're done

        # is this a new date?
        rss = Receiver_Schedule.objects.filter(start_date = date)
        if len(rss) == 0:
            # make a copy of the previous date
            prev = Receiver_Schedule.previousDate(date)
            prev_rs = Receiver_Schedule.objects.filter(start_date = prev)
            for p in prev_rs:
                rs = Receiver_Schedule(start_date = date
                                     , receiver   = p.receiver)
                rs.save()                     
            rss = Receiver_Schedule.objects.filter(start_date = date)

        # compare old diff to new diff (up and down params)
        diffs = Receiver_Schedule.extract_diff_schedule(startdate = date)
        dt, old_ups, old_downs = first([d for d in diffs if d[0] == date])
        #print "original diff: ", old_ups, old_downs

        # what used to go up, that no longer does?
        remove_ups = Set(old_ups).difference(Set(up))
        # what is going up that didn't before?
        add_ups = Set(up).difference(Set(old_ups))
        #print "UP Sets: ", remove_ups, add_ups

        # what used to go down, that no longer does?
        remove_downs = Set(old_downs).difference(Set(down))
        # what is going down that didn't before?
        add_downs = Set(down).difference(Set(old_downs))
        #print "DOWN Sets: ", remove_downs, add_downs

        # convert the sets to two lists of rcvrs: ups & downs
        ups = [u for u in add_ups]
        for d in remove_downs:
            if d not in ups:
                ups.append(d)
        #print "UP list: ", ups        
        downs = [d for d in add_downs]
        for u in remove_ups:
            if u not in downs:
                downs.append(u)
        #print "DOWN list: ", downs        


        # TBF: should we even error check?
        #for u in up:
        #    if u in available:
        #        return (False, "Receiver %s is already up on %s" % (u, date))
        #for d in down:
        #    if d not in available:
        #        return (False
        #        , "Receiver %s cannot come down on %s, is not up." % (d, date))

 
        # now alter the subsequent dates on the schedule:
        schedule = Receiver_Schedule.extract_schedule(date)
        dates = sorted(schedule.keys())
        # remove the rcvr(s) we just took down from all subsequent dates, 
        # until they dissappear on their own
        for d in downs:
            #print "d in down: ", d
            for dt in dates:
                if dt >= date:
                    #print "down schd date: ", dt
                    #, [r.abbreviation for r in schedule[dt]]
                    if d in schedule[dt]:
                        # shouldn't be there anymore!
                        gone =Receiver_Schedule.objects.filter(start_date = dt
                                                             , receiver = d)
                        for g in gone:
                            #print "deleting: ", g
                            g.delete()
                    else:
                        break
        # add the rcvr(s) we just put up to all subsequent dates, 
        # until they show up on their own
        for u in ups:
            #print "u in up: ", u
            for dt in dates:
                if dt >= date:
                    #print "up schd date: ", dt
                    #, [r.abbreviation for r in schedule[dt]]
                    if u not in schedule[dt]:
                        # should be there now!
                        new = Receiver_Schedule(start_date = dt, receiver = u)
                        new.save()
                        #print "new: ", new
                    else:
                        break

        # return success 
        return (True, None)

    @staticmethod
    def delete_date(date):
        "Remove all entries for the given date, and change subsequent schedule"
 
        # first check that this date is in the schedule
        rs = Receiver_Schedule.objects.filter(start_date = date)
        if len(rs) == 0:
            return (False, "Date is not in Receiver Schedule: %s" % date)

        # we first reconcile the schedule to this change by reversing all
        # the changes that were meant to happen on this day:
        diff_schedule = Receiver_Schedule.extract_diff_schedule(startdate = date)
        day, ups, downs = first([d for d in diff_schedule if d[0] == date])
        
        # reverse it!
        s, msg = Receiver_Schedule.change_schedule(day, downs, ups, end_of_day = True)
        if not s:
            return (False, msg)

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
            if not any([all([Set(g.receivers.all()).intersection(receivers) \
                        for g in set]) for set in required]):
                # No session has receivers available. Begin drought.
                if not ranges or ranges[-1][1] is not None:
                    ranges.append((date, None))
            else:
                # A session has receivers available. End drought, if present.
                if ranges and ranges[-1][1] is None:
                    start, _ = ranges.pop(-1)
                    ranges.append((start, date))
        return ranges
            
