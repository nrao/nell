from django.db         import models
from Sesshun           import Sesshun
from Period_State      import Period_State
from Period            import Period

class Elective(models.Model):
    session  = models.ForeignKey(Sesshun)
    complete = models.BooleanField(default = False)

    class Meta:
        db_table  = "electives"
        app_label = "sesshuns"

    def __str__(self):
        cmp = "Cmp." if self.complete else "Not Cmp."
        return "Elective for Session %s with %d periods. Cmp: %s, Grntd: %s" % (self.session.name, self.periods.count(), self.complete, self.guaranteed())

    # TBF: cut & past from Window model
    def toHandle(self):
        if self.session is None:
            return ""
        if self.session.original_id is None:
            original_id = ""
        else:
            original_id = str(self.session.original_id)
        return "%s (%s) %s" % (self.session.name
                             , self.session.project.pcode
                             , original_id)

    # TBF: cut & past from Window model
    def handle2session(self, h):
        n, p = h.rsplit('(', 1)
        name = n.strip()
        pcode, _ = p.split(')', 1)
        return Sesshun.objects.filter(project__pcode__exact=pcode).get(name=name)

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
            # TBF: anything we need to check before doing this?
            p.move_to_deleted_state()

        self.setComplete(True)

    def hasPeriodsAfter(self, dt):
        return len([p for p in self.periods.all() if p.start > dt]) > 0

    def periodDateRange(self):
        "Returns the earliest & latest start times of all its periods"
        min = max = None
        for p in self.periods.all():
            if min is None or p.start <= min:
                min = p.start
            if max is None or p.start >= max:
                max = p.start
        return (min, max)

    def periodsOrderByDate(self):
        return Period.objects.filter(elective = self).order_by("start")

    def periodsByState(self, s):    
        "get periods by their state, which is one of ['P', 'D', 'S']"
        state = Period_State.get_state(s)
        return [p for p in self.periods.all() if p.state == state]

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
            # True -> False:  resurect all deleted
            for p in self.deletedPeriods():
                p.state = Period_State.get_state("P")        
                p.save()

        self.complete = complete
        self.save()
