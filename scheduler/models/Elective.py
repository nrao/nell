from django.db         import models
from Sesshun           import Sesshun
from Period_State      import Period_State
from Period            import Period

class Elective(models.Model):
    session  = models.ForeignKey(Sesshun)
    complete = models.BooleanField(default = False)

    class Meta:
        db_table  = "electives"
        app_label = "scheduler"

    def __str__(self):
        cmp = "Cmp." if self.complete else "Not Cmp."
        return "Elective for Session %s with %d periods. Cmp: %s, Grntd: %s" % (self.session.name, self.periods.count(), self.complete, self.guaranteed())

    def toHandle(self):
        if self.session is None:
            return ""
        return self.session.toHandle()

    def guaranteed(self):
        "Does the parent session have this flag set?"
        return self.session.guaranteed()

    def publish(self):
        """
        This completes the process of electing one of a group of periods
        to run.  We assume that one of the Elective's periods is no longer
        in the pending state, and all the others get moved to the deleted
        state.  Then this elective is marked as complete.
        """

        for p in self.pendingPeriods():
            # Note: anything we need to check before doing this?
            p.move_to_deleted_state()

        self.setComplete(True)

    def hasPeriodsAfter(self, dt):
        return self.periods.filter(start__gt=dt).exists()

    def periodDateRange(self):
        "Returns the earliest & latest start times of all its periods"
        try:
            min = self.periods.order_by('start')[0].start
        except IndexError:
            min = None
        try:
            max = self.periods.order_by('-start')[0].start
        except IndexError:
            max = None
        return (min, max)

    def periodsOrderByDate(self):
        return Period.objects.filter(elective = self).order_by("start")

    def periodsByState(self, s):    
        "get periods by their state, which is one of ['P', 'D', 'S']"
        state = Period_State.get_state(s)
        return self.periods.filter(state=state)

    def deletedPeriods(self):
        return self.periodsByState("D")

    def scheduledPeriods(self):
        return self.periodsByState("S")

    def pendingPeriods(self):
        return self.periodsByState("P")
        
    def setComplete(self, complete):
        """
        The setting of the complete flag will automatically delete all 
        associated Pending periods; conversely clearing the flag will 
        restore all future opportunities to Pending.
        """
        
        # if we haven't initilized yet, get out of town
        if self.complete is None:
            self.complete = complete
            self.save()
            return

        # only make changes on *transitions* of state
        if complete and not self.complete:
            # False -> True:  delete all pending
            for p in self.pendingPeriods():
                p.move_to_deleted_state()

        elif not complete and self.complete:
            # True -> False:  resurrect all deleted
            for p in self.deletedPeriods():
                p.state = Period_State.get_state("P")        
                p.save()

        self.complete = complete
        self.save()

    def getRange(self):
        state = Period_State.get_state('D')
        ps = self.periods.exclude(state=state).order_by('start')
        periods = list(ps)
        if periods:
            return [periods[0].start, periods[-1].end()]
        else:
            return []

    def getBlackedOutSchedulablePeriods(self):
        """
        Of the periods for this elective overlapping in the time range
        that are not deleted or completed, which schedulable ones have
        been blacked out?  Returns a list of offending periods.
        """
        state = Period_State.get_state('D')
        ps = self.periods.exclude(state=state).order_by('start')
        periods = list(ps)
        if not periods:
            return []
        pranges = [(p.start, p.end(), p) for p in periods]
        _, _, _, brs = \
            self.session.getBlackedOutSchedulableTime(pranges[0][0]
                                                    , pranges[-1][1])
        branges = [r for sublist in brs for r in sublist] # flatten lists

        retval = []
        for p in pranges:
            for b in branges:
                if p[0] < b[1] and b[0] < p[1]:
                    retval.append(p[2])
                    break
        return retval
