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

from django.db     import models
from datetime      import datetime, timedelta

from utilities     import TimeAgent, AnalogSet

from Sesshun                 import Sesshun
from Period                  import Period
from Period_State            import Period_State

class Window(models.Model):
    session        = models.ForeignKey(Sesshun)
    default_period = models.OneToOneField(Period, null = True, related_name = "default_window")
    complete      = models.BooleanField(default = False)
    total_time     = models.FloatField(help_text = "Hours", null = True, default = 0.0)

    def __unicode__(self):
        return "Window (%d) for Sess (%d)" % \
            (self.id
           , self.session.id)

    def __str__(self):
        name = self.session.name if self.session is not None else "None"
        start = self.start_date().strftime("%Y-%m-%d") if self.start_date() is not None else "?"
        duration = self.duration() if self.duration() is not None else "?"
        return "Window for %s, from %s for %s days, default: %s, # periods: %d" % \
            (name
           , start
           , duration
           , self.default_period
           , self.periods.count()) 

    
    def isContigious(self):
        """
        A non-contigious Window has more then one window range, with 
        gaps between them.
        """
        wrs = self.ranges()
        if len(wrs) > 1:
            # if any one end isn't at the next start, then non-cont.
            for i in range(len(wrs)-1):
                end = wrs[i].start_date + timedelta(days = wrs[i].duration)
                nextStart = wrs[i+1].start_date
                if nextStart != end:
                    return False
            # if we get to here, it's contigious
            return True
        else:
            return True

    def ranges(self):
        return self.windowrange_set.all().order_by("start_date")

    def first_range(self):
        wrs = self.ranges()
        return wrs[0] if len(wrs) > 0 else None

    def last_range(self):
        wrs = self.ranges() 
        return wrs[len(wrs)-1] if len(wrs) > 0 else None

    # ****** This group of methods below can be used if gaps between
    # ****** window ranges can be ignored or Window is contigious.

    def start(self):
        if len(self.ranges()) > 0:
            return self.first_range().start_date
        else:
            None

    def start_date(self):
        return self.start()

    def end(self):
        return self.last_date()

    def last_date(self):
        "Ex: start = 1/10, duration = 2 days, last_date = 1/11"
        if len(self.ranges()) > 0:
            return self.last_range().last_date()
        else:
            None

    def start_datetime(self):
        return TimeAgent.date2datetime(self.start()) if self.start() is not None else None

    def end_datetime(self):
        "We want this to go up to the last second of the last_date"
        return self.last_range().end_datetime() if self.last_range() is not None else None

    def duration(self):
        last = self.last_date() 
        start = self.start()
        if last is not None and start is not None:
            return (self.last_date() - self.start()).days + 1
        else:
            return None

    def inWindow(self, date):
        return (self.start() <= date) and (date <= self.last_date())

    def isInWindow(self, period):
        "Does the given period overlap at all in window (endpoints)"
        return AnalogSet.overlaps((self.start_datetime(), self.end_datetime())
                                , (period.start, period.end()))

    def isInRanges(self, period):
        """
        Does the given period overlap with any of the window ranges?
        This is more rigourous then isInWindow.
        """
        for wr in self.windowrange_set.all():
            if AnalogSet.overlaps((wr.start_datetime(), wr.end_datetime())
                                , (period.start, period.end())):
                return True
        return False # no overlaps at all!        

    # ****** end of group above that ignores window ranges ***

    def timeRemaining(self):
        "Total - Billed"
        return self.total_time - self.timeBilled()

    def timeBilled(self):
        """
        Simply the sum of all the periods' time billed, regardless of
        state.  Remember that, in a healthy systme, pending and deleted
        periods should have no time billed.
        """
        return sum(p.accounting.time_billed() for p in self.periods.all())

    def publish(self): 
        "A period was just published, see if we can complete this."

        timeRemaining = self.timeRemaining()

        if timeRemaining == 0:
            # this window is complete!
            self.complete = True
            if self.default_period.isPending():
                self.default_period.move_to_deleted_state()
        else:    
            # window is not complete, but default gets adjusted
            self.default_period.duration = timeRemaining
            self.default_period.save()
        
    def setComplete(self, complete):
        """
        When a window is set as not complete, the default period
        comes back.
        """
        remaining = self.timeRemaining()
        if not complete and self.complete and \
          remaining != 0 and self.default_period is not None:
            self.default_period.duration = remaining
            self.default_period.state = Period_State.get_state("P")
            self.default_period.save()
        self.complete = complete
        self.save()

    def nonDefaultPeriods(self):
        return [p for p in self.periods.all() if p != self.default_period]

    def periodStates(self):
        return [p.state for p in self.periods.all().order_by("start")]

    def periodsByState(self, s):    
        "get periods by their state, which is one of ['P', 'D', 'S']"
        state = Period_State.get_state(s)
        return self.periods.filter(state=state)

    def scheduledPeriods(self):
        return self.periodsByState("S")

    def pendingPeriods(self):
        return self.periodsByState("P")

    def toHandle(self):
        if self.session is None:
            return ""
        return self.session.toHandle()

    def eventjson(self, id):
        """
        This is just a summary: if the window is non contigious
        then this will not include gaps.
        """

        return {
                "id"   :     id
              , "title":     "".join(["Window ", self.session.name])
              , "start":     self.start_date().isoformat()
              , "end"  :     self.end().isoformat()
              , "className": 'window'
        }
 
    def getWindowTimeNotSchedulable(self, blackouts = True):
        "How many hours in this window are not schedulable?"
        ns = []
        for wr in self.ranges():
            ns.extend(self.session.get_time_not_schedulable( \
                wr.start_datetime()
              , wr.end_datetime()
              , blackouts = blackouts))
        return sum([TimeAgent.timedelta2minutes(n[1] - n[0])/60.0 \
            for n in ns])
        
    def getWindowTimeBlackedOut(self):
        "How many hours in this window have been blacked out?"
        bs = []
        for wr in self.ranges():
            bstart = wr.start_datetime()
            bend   = wr.end_datetime()
            bs.extend(self.session.project.get_blackout_times(bstart, bend))
        return sum([TimeAgent.timedelta2minutes(b[1] - b[0])/60.0 \
            for b in bs])

    def getBlackedOutSchedulableTime(self):
        """
        Of the hours in this window that are schedulable, how
        many have been blacked out?
        Returns for this window the tuple:
            (
             total schedulable time ignoring blacked out
           , total schedulable time but blacked out
           , [schedulable ranges ignoring blacked out]
           , [schedulable ranges but blacked out]
            )
        """
        hrsSchedulable = hrsBlackedOut = 0.0
        schedulable = []
        blackouts = []
        for wr in self.ranges():
            hs, hb, schd, bs = self.session.getBlackedOutSchedulableTime(\
                wr.start_datetime()
              , wr.end_datetime())
            hrsSchedulable += hs  
            hrsBlackedOut += hb  
            schedulable.extend(schd)
            blackouts.extend(bs)
        return (hrsSchedulable
              , hrsBlackedOut
              , schedulable
              , blackouts)     

    def defaultPeriodBlackedOut(self):
        """
        Do any of the times that are not schedulable for this 
        session due to blackouts overlapping with the default
        period?
        """

        # no default, no problem
        if self.default_period is None:
            return False

        bs = self.session.project.get_blackout_times(\
            self.default_period.start
          , self.default_period.end())

        return len(bs) > 0  

    def lstOutOfRange(self):
        """
        Are any of the window ranges just one day, with the
        LST such that the session can't be scheduled?
        """
        lst = TimeAgent.rad2hr(self.session.target.horizontal)

        # how close can the lst be to the edges of the range?
        buffer = (self.session.min_duration + self.session.max_duration) / 2.0

        return [wr for wr in self.windowrange_set.all() \
            if wr.duration == 1 and \
                not wr.lstInRange(lst, buffer = buffer)]

    def hasLstOutOfRange(self):
        return len(self.lstOutOfRange()) > 0

    def hasNoLstInRange(self):
        numBadRanges = len(self.lstOutOfRange())
        numRanges = self.windowrange_set.count()
        return numBadRanges == numRanges and numRanges > 0 

    def hasOverlappingRanges(self):
        "Window Ranges shouldn't overlap."
        return True if len(self.overlappingRanges()) > 0 else False
            
    def overlappingRanges(self):
        "What ranges are overlapping?"

        wrs = self.ranges()
        if len(wrs) <= 1:
            return []

        overlap = []
        for i in range(0, len(wrs)):
            for j in range(i+1, len(wrs)):
                w1s = wrs[i].start_date
                w1e = wrs[i].last_date()
                w2s = wrs[j].start_date
                w2e = wrs[j].last_date()
                if w1s <= w2e and w2s <= w1e:
                    overlap.append((wrs[i], wrs[j]))
        return overlap

    def overlappingWindows(self):
        "Does this window overlap with any other windows of same session?"
        wins = self.session.window_set.all().exclude(id = self.id)
        w1s = self.start()
        w1e = self.end()
        overlapping = []
        if w1s is None or w1e is None:
            return overlapping
        for w in wins:
            w2s = w.start()
            w2e = w.end()
            if w2s is None or w2e is None:
                continue
            if w1s <= w2e and w2s <= w1e:
                overlapping.append(w)
        return overlapping       

    def bufferDays(self):
        "How many days need to separate windows of same session?"
        return 2

    def tooCloseWindows(self):
        "Is this window too close to other windows of the same session?"
        w1s = self.start()
        w1e = self.end()
        if w1s is None or w1e is None:
            return []
        wins = self.session.window_set.all().exclude(id = self.id)
        tooClose = []
        for w in wins:
            w2s = w.start()
            w2e = w.end()
            if w2s is None or w2e is None:
                continue
            if w1s < w2s:
                delta = w2s - w1e
            else:
                delta = w1s - w2e
            if delta.days < self.bufferDays():
                tooClose.append(w)
        return tooClose       

    def outOfRangePeriods(self, deleted = False):
        "What periods lie totally outside of ranges?"
        if deleted:
            ps = self.periods.all()
        else:
            ps = self.periods.exclude(state__abbreviation = "D")
        return [p for p in ps if not self.isInRanges(p)]

    def lacksMandatoryDefaultPeriod(self):
        """
        Windowed Sessions that are guaranteed need default periods.
        Non-guaranteed can do without a default period, because if
        a window doesn't get scheduled, oh well, it wasn't guaranteed.
        """
        return self.session.guaranteed() and self.default_period is None 
        
    def errors(self):
        """
        Collect all possible problems with this window, and put them
        in a list of strings meant for the scheduler.
        """
        err = []
        if self.hasLstOutOfRange() and not self.hasNoLstInRange():
            wrs = [("%s - %s" % (wr.start_date, wr.end())) for wr in self.lstOutOfRange()]
            ranges = ",".join(wrs)
            err.append("Window Range(s) %s have out of range LST." % ranges)
        if self.hasNoLstInRange():
            err.append("All Window Ranges have out of range LST.")
        if self.hasOverlappingRanges():
            err.append("Overlapping Window Ranges.")
        if self.lacksMandatoryDefaultPeriod():
            err.append("Default Period mandatory for non-guaranteed Sessions.")
        if len(self.ranges()) == 0:
            err.append("Window must have at least one Window Range.")
        # out of range periods    
        outOfRanges = self.outOfRangePeriods()
        if len(outOfRanges) != 0:
            ps = ",".join(["%s for %5.2f" % (p.start, p.duration) for p in outOfRanges])
            err.append("Window has out of range Period(s): %s" % ps)
            
        # check for overlaps, if none, check that they're separated enough 
        overlapping = self.overlappingWindows()
        if len(overlapping) != 0:
            wids = ",".join([str(w.id) for w in overlapping])
            err.append("Window is overlapping with window ID(s): %s" % wids)
        else:
            tooClose = self.tooCloseWindows()
            if len(tooClose) != 0:
                wids = ",".join([str(w.id) for w in tooClose])
                err.append("Window is within %d days of window ID(s): %s" % (self.bufferDays(), wids))
            
        return err    

    class Meta:
        db_table  = "windows"
        app_label = "scheduler"

