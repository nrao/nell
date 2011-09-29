from django.core.management import setup_environ
import settings
setup_environ(settings)

from scheduler.models import *
from datetime import datetime
from utilities                 import AnalogSet

class ResolveOverlaps:

    def __init__(self):
        self.output = open('resolve_overlaps.txt', 'w')

    def __del__(self):
        self.output.close()

    def findOverlaps(self, periods):
        values = []
        overlap = []
        for p1 in periods:
            start1, end1 = p1.start, p1.end()
            for p2 in periods:
                start2, end2 = p2.start, p2.end()
                if p1 != p2 and p1 not in overlap and p2 not in overlap:
                    if AnalogSet.overlaps((start1, end1), (start2, end2)):
                        values.append((p1, p2))
                        overlap.extend([p1, p2])
        return (overlap, values)
    
    def showPeriod(self, p):
    
        guaranteed = "" 
        if p.session.isElective():
            guaranteed = "(Guar.)" if p.session.guaranteed() else "(Not Guar.)"
        return "%s (%s) %s - %s for %5.2f hours." % (p.session.name
                                               , p.session.session_type.type.upper()[0]
                                               , guaranteed
                                               , p.start
                                               , p.duration
                                                 )
    
    def annotate(self, subject):
        print "%s" % subject
        self.output.write("%s" % subject + '\n')

    def electivesResolvable(self, p1, p2):
    
        # must be electives
        if not p1.session.isElective() or not p2.session.isElective():
            self.annotate( "Not electives: %s %s" % (p1, p2))
            return False
    
        # one of their elective groups must have another period we can choose
        p1total = len(p1.elective.periods.all())
        p2total = len(p2.elective.periods.all())
        if p1total + p2total < 3:
            # no options!
            self.annotate( "Not enough periods in elective groups: %s %s" % (p1, p2))
            return False
    
        # Okay, so, one of the elective groups must choose it's first period,
        # and the other elective group must choose it's second period.
        # But make sure you choose periods that actually exist
        p1choosen, p2choosen = (0, 1) if p2total > 1 else (1, 0)
        ep1 = p1.elective.periods.all().order_by('start')[p1choosen]
        ep2 = p2.elective.periods.all().order_by('start')[p2choosen]
    
        # if these don't overlap, we're good
        return AnalogSet.overlaps((ep1.start, ep1.end())
                                , (ep2.start, ep2.end())
                                 )
    
    def hasOptions(self, p):
        """
        If we remove this period, is there a chance that it's session
        will be completed at all?
        Ex: if it's a fixed period, it has NO options
        Ex: if it's a guaranteed elective with just one period, it has NO options
        Ex: if it's an elective session, with > 1 period, it has options
        """
    
        if not p.session.isElective():
            return False
    
        if p.session.isElective() and p.elective is None:
            return False
    
        numPs = len(p.elective.periods.all())
        
        if numPs > 1:
           return True
        elif p.session.guaranteed(): # must have just one period
           return False
        else:
           return True 
            
    def overlapResolvable(self, p1, p2):
        """
        There may be no good resolution for the two pairs (ex: both are fixed),
        so, return which one has been deleted, and flag stating whether this 
        represents an actual resolution, or just desperation.
        """
    
        opt1 = self.hasOptions(p1)
        opt2 = self.hasOptions(p2)
    
        # if neither has any options, then arbitrarly nuke the second one
        if not opt1 and not opt2:
            return (p1, None, False)
    
        # if one of them has options, we can do something
        if opt1 and not opt2:
            return (None, p2, True)
    
        if opt2 and not opt1:
            return (p1, None, True)
    
        # if they both have options, then arbitrarly nuke the second one
        if opt1 and opt2:
            return (p1, None, True)
            
            
    def showPair(self, p1, p2):
        #self.annotate( "Overlap between %s and %s" % (p1, p2))
        self.annotate( "\n%s" % self.showPeriod(p1))
        if p1.session.isElective() and p1.elective is not None:
            for ep in p1.elective.periods.all().order_by("start"):
                if ep.id != p1.id:
                    self.annotate( "    %s" % self.showPeriod(ep))
        self.annotate( "%s" % self.showPeriod(p2))
        if p2.session.isElective() and p2.elective is not None:
            for ep in p2.elective.periods.all().order_by("start"):
                if ep.id != p2.id:
                    self.annotate( "    %s" % self.showPeriod(ep))
    
    def resolve(self, period):
        if not self.hasOptions(period):
            # nothing to be done!
            period.move_to_deleted_state()
            period.save()
        else:
            # by how we defined 'options', this is an elective w/ more then
            # one period, so delete *this* period, and arbitrarly choose another
            period.move_to_deleted_state()
            period.save()
            others = [p for p in period.elective.periods.all() if p.id != period.id]
            if len(others) > 0:
                choosen = others[0]
                choosen.publish()
                choosen.save()
    

    def resolveOverlaps(self):    
        def printPairs(pairs):
            self.annotate( "Overlaps: ")
            for p1, p2 in pairs:
                self.showPair(p1, p2)
        
        now             = datetime.now()
        overlaps, pairs = self.findOverlaps(
            [p for p in Period.objects.filter(start__gt = now).exclude(state__abbreviation = "D")])
        numOverlaps     = len(pairs)

        self.annotate( "Number of overlapping pairs: %s" % numOverlaps)
        printPairs(pairs)

        elec_pairs = [self.electivesResolvable(p1, p2) for p1, p2 in pairs if p1.session.isElective() and p2.session.isElective()]

        self.annotate( "Number of overlapping elective pairs: %s" % len(elec_pairs))
        self.annotate( elec_pairs)
        
        # resolve overlaps!  After each resolution, we should query DB
        # again, to make sure the resolution's affects are taken into account
        removed = []
        while numOverlaps > 0:
            self.annotate( "Number of overlaps: %s" % numOverlaps)
            # resolve the first pair
            p1, p2 = pairs[0]
            newP1, newP2, resolvable = self.overlapResolvable(p1, p2)
            resolvePeriod = p1 if newP1 is None else p2
            chosenPeriod  = p1 if newP1 is not None else p2
            assert resolvePeriod.id != chosenPeriod.id
            if resolvable:
               self.annotate("Found resolution using %s" % self.showPeriod(resolvePeriod))
            else:
               self.annotate("NO resolutin found, deleting %s" % self.showPeriod(resolvePeriod))
            removed.append((resolvePeriod, resolvable))
            # publish one
            chosenPeriod.publish()
            # and move the other out of they way, choosing one of it's options
            # to publish
            self.resolve(resolvePeriod)

            # then find overlaps again
            overlaps, pairs = self.findOverlaps(
                [p for p in Period.objects.filter(start__gt = now).exclude(state__abbreviation = "D")])
            printPairs(pairs)

            prevNum     = numOverlaps    
            numOverlaps = len(pairs)
            # avoid an infinite loop
            assert numOverlaps < prevNum

        self.annotate( "Overlaps resolved!!!")
        
        for rm, problem in removed:
            self.annotate( "Period %s deleted; %s" % (self.showPeriod(rm), problem))

if __name__ == "__main__":
    ResolveOverlaps().resolveOverlaps()
