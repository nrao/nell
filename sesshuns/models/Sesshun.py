from django.db import models

from Allotment      import Allotment
from common         import *
from Observing_Type import Observing_Type
from Parameter      import Parameter
from Project        import Project
from Receiver       import Receiver
from Receiver_Schedule import Receiver_Schedule
from Session_Type   import Session_Type
from Status         import Status
from System         import System

class Sesshun(models.Model):
    
    project            = models.ForeignKey(Project)
    session_type       = models.ForeignKey(Session_Type)
    observing_type     = models.ForeignKey(Observing_Type)
    allotment          = models.ForeignKey(Allotment)
    status             = models.ForeignKey(Status)
    original_id        = models.IntegerField(null = True, blank = True)
    name               = models.CharField(null = True
                                        , max_length = 64
                                        , blank = True)
    frequency          = models.FloatField(null = True, help_text = "GHz", blank = True)
    max_duration       = models.FloatField(null = True, help_text = "Hours", blank = True)
    min_duration       = models.FloatField(null = True, help_text = "Hours", blank = True)
    time_between       = models.FloatField(null = True, help_text = "Hours", blank = True)
    accounting_notes   = models.TextField(null = True, blank = True)
    notes              = models.TextField(null = True, blank = True)

    restrictions = "Unrestricted" # TBF Do we still need restrictions?

    base_url = "/sesshuns/sesshun/"

    def __unicode__(self):
        return "(%d) %s : %5.2f GHz, %5.2f Hrs, Rcvrs: %s, status: %s" % (
                  self.id
                , self.name if self.name is not None else ""
                , float(self.frequency) if self.frequency is not None else float(0.0)
                , float(self.allotment.total_time)
                      if self.allotment.total_time is not None else float(0.0)
                , self.receiver_list()
                , self.status)

    def get_absolute_url(self):
        return "/sesshuns/sesshun/%i/" % self.id

    def isOpen(self):
        return self.session_type.type == "open"

    def isWindowed(self):
        return self.session_type.type == "windowed"

    def isFixed(self):
        return self.session_type.type == "fixed"

    def isScience(self):
        return self.observing_type.type not in ("commissioning", "testing", "calibration", "maintenance")

    def isShutdown(self):
        return self.project.name == 'Shutdown'

    def isMaintenance(self):
        return self.observing_type.type == 'maintenance'

    def isTest(self):
        return self.observing_type.type == 'testing' 

    def isCommissioning(self):
        return self.observing_type.type == 'commissioning' 

    def isCalibration(self):
        return self.observing_type.type == 'calibration' 

    @staticmethod
    def getCategories():
        "Return all possible categories of interest to Operations."
        return ["Un-assigned", "Astronomy", "Maintenance", "Shutdown"
              , "Tests", "Calibration", "Commissioning"]

    def getCategory(self):
        "Categorize this project in a meaningful way for Operations."
        category = "Un-assigned"
        if self.isScience():
            category = "Astronomy"
        elif self.isShutdown():
            category = "Shutdown"
        elif self.isMaintenance():
            category = "Maintenance"
        elif self.isTest():
            category = "Tests"
        elif self.isCommissioning():
            category = "Commissioning"
        elif self.isCalibration():
            category = "Calibration"

        return category

    def receiver_list(self):
        "Returns a string representation of the rcvr logic."
        return " AND ".join([rg.__str__() for rg in self.receiver_group_set.all()])

    def receiver_list_simple(self):
        "Returns a string representation of the rcvr logic, simplified"
        # ignore rcvr groups that have no rcvrs!  TBF: shouldn't happen!
        rgs = [ rg for rg in self.receiver_group_set.all() if len(rg.receivers.all()) != 0]
        if len(rgs) == 1:
            # no parens needed
            ls = " OR ".join([r.abbreviation for r in rgs[0].receivers.all()])
        else:
            # we can't simplify this anymore
            ls = self.receiver_list()
        return ls

    def rcvrs_specified(self):
        "Returns an array of rcvrs for this sesshun, w/ out their relations"
        # For use in recreating Carl's reports
        rcvrs = []
        for rg in self.receiver_group_set.all():
            rs = [r.abbreviation for r in rg.receivers.all()]
            for r in rs:
                if r not in rcvrs:
                    rcvrs.append(r)
        return rcvrs        

    def grade(self):
        return self.allotment.grade

    def num_rcvr_groups(self):
        return len(self.receiver_group_set.all())

    def schedulable(self):
        "A simple check for all explicit flags"
        return (self.status.enabled) and \
               (self.status.authorized) and \
               (not self.status.complete) and \
               (not self.project.complete)

    def delete(self):
        self.allotment.delete()
        super(Sesshun, self).delete()

    def get_LST_exclusion_string(self):
        "Converts pair of observing parameters into low-high string"
        lowParam = first(Parameter.objects.filter(name="LST Exclude Low"))
        hiParam  = first(Parameter.objects.filter(name="LST Exclude Hi"))
        lows  = self.observing_parameter_set.filter(parameter=lowParam)
        highs = self.observing_parameter_set.filter(parameter=hiParam)
        # make sure there aren't more then 1
        assert len(lows) < 2
        assert len(highs) < 2
        # make sure they make a pair, or none at all
        assert len(lows) == len(highs)
        # LST Exlcusion isn't set?
        if len(lows) == 0 and len(highs) == 0:
            return ""
        low = first(lows)
        high = first(highs)
        return "%.2f-%.2f" % (low.float_value, high.float_value)

    def get_ra_dec(self):
        target = first(self.target_set.all())
        if target is None:
            return None, None
        return target.vertical, target.horizontal

    def set_dec(self, new_dec):
        target = first(self.target_set.all())
        if target is None:
            return
        target.horizontal = new_dec
        target.save()

    def get_ignore_ha(self):
        # TBF:  Need specification of ignore_ha
        return False
        
    def get_receiver_req(self):
        rcvrs = [[r.abbreviation \
                     for r in rg.receivers.all().order_by('id')] \
                         for rg in self.receiver_group_set.all().order_by('id')]
        rc = ReceiverCompile(Receiver.get_abbreviations())
        return rc.denormalize(rcvrs)

    def get_ha_limit_blackouts(self, startdate, days):
        # TBF: Not complete or even correct yet.

        targets = [(t.horizontal, t.vertical) for t in self.target_set.all()]

        # startdate, days, self.frequency, targets
        #url       = "?"
        #blackouts = json.load(urlllib.urlopen(url))['blackouts']

        #return consolidate_events(find_intersections(blackouts))

    def get_min_eff_tsys_factor(self):
        """
        Returns factor if has 'Min Eff TSys' observing parameter,
        else None.
        """
        return self.has_float_obs_param("Min Eff TSys")

    def get_elevation_limit(self):
        """
        Returns factor if has 'El Limit' observing parameter,
        else None.
        """
        return self.has_float_obs_param("El Limit")

    def transit(self):
        """
        Returns True or False if has 'Transit' observing parameter,
        else None if not.
        """
        return self.has_bool_obs_param("Transit")

    def nighttime(self):
        """
        Returns True or False if has 'Night-time Flag' observing parameter,
        else None if not.
        """
        return self.has_bool_obs_param("Night-time Flag")

    def not_guaranteed(self):
        """
        Returns True or False if it does have the 'Not Gaurenteed'
        observing parameter, else None if not.
        Only applies to windowed and elective sessions: if 'Not
        Gaurentted' is set True, then the window or elective is not 
        guaranteed to observe.
        """
        return self.has_bool_obs_param("Not Guaranteed")

    def guaranteed(self):
        "True if 'Not Gaurenteed' param is set to F, or None"
        ng = self.not_guaranteed()
        if ng is None or not ng:
            return True
        else:
            return False

    def has_bool_obs_param(self, name):
        tp = Parameter.objects.filter(name=name)[0]
        top = self.observing_parameter_set.filter(parameter=tp)
        return top[0].boolean_value if top else None

    def has_float_obs_param(self, name):
        try:
            tp = Parameter.objects.filter(name=name)[0]
            top = self.observing_parameter_set.filter(parameter=tp)
            return top[0].float_value
        except IndexError:
            return None

    def get_receiver_blackout_ranges(self, start, end):
        """
        Returns a list of tuples of the form (start, end) where
        start and end are datetime objects that denote the 
        beginning and ending of a period where no receivers are available
        for this session.  If there is a receiver available
        at all times an empty list is returned. 
        """

        # Find all the required receiver sets for this project and schedule.
        # E.g. for one session:
        #     [[a, b, c], [x, y, z]] = (a OR b OR c) AND (x OR y OR z)
        required = [self.receiver_group_set.all()]
        if required == []:
            return [] 
        return Receiver_Schedule.get_receiver_blackout_ranges(required, start, end)

    def get_receiver_blackout_dates(self, start, end):
        # Change date ranges into individual days.
        blackouts = []
        for rstart, rend in self.get_receiver_blackout_ranges(start, end):
            counter = rstart.replace(hour = 0)
            while counter < (rend or end):
                blackouts.append(counter)
                counter = counter + timedelta(days = 1)
 
        return blackouts

    def get_time_not_schedulable(self, start, end, blackouts = True):
        """
        What is the set of time ([(start, end)]) in the given time window
        where this session is not schedulable?
        Here we consolidate all events so that we can use them to make
        calculations of the percentage of time available.
        """
    
        # WTF?
        if self.project is None:
            return []
    
        dts = Set([])
        dts = dts.union(self.get_receiver_blackout_ranges(start, end))
        dts = dts.union(self.project.get_prescheduled_times(start, end))
        if blackouts:
            dts = dts.union(self.project.get_blackout_times(start, end))
        
        # the call to consolidate_events won't accept the None used
        # sometimes by get_receiver_blackout_range, so substitue in
        # the given boundries for these
        newDts = []
        for (s, e) in list(dts):
            if s is None:
                s = start
            if e is None:
                e = end
            newDts.append((s,e))
            
        return consolidate_events(sorted(newDts))

    def getBlackedOutSchedulableTime(self, start, end):
        """
        Of the hours in the given range that are schedulable,
        how many have been blacked out?
        Returns tuple of hours (scheduble but ignoring blackouts
                              , scheduable but blacked out)
        """

        nss1 = self.get_time_not_schedulable( start
                                           , end
                                           , blackouts = False)

        nss = trim_events(nss1, start, end)

        # now convert the non-schedulable time ranges to the 
        # time that IS schedulable:
        schedulable = compliment_events(nss, start, end)
 
        # how much time is that?
        hrsSchedulable = sum([TimeAgent.timedelta2minutes(s[1] - s[0])/60.0 \
            for s in schedulable])

        # now, for each chunk of schedulable time, how much is
        # blacked out?
        hrsBlackedOut = 0.0
        bss = []
        for s in schedulable:
            bs = self.project.get_blackout_times(s[0], s[1])
            # but these blackout times might not match to the schedulable
            # end points, so we may need to truncate them
            bs = trim_events(bs, s[0], s[1])
            if len(bs) != 0:
                bss.append(bs)
            bsTime = sum([TimeAgent.timedelta2minutes(b[1] - b[0])/60.0 \
                for b in bs])
            hrsBlackedOut += bsTime

        # return a summary of what we've found
        return (hrsSchedulable
              , hrsBlackedOut
              , schedulable
              , bss)           

    class Meta:
        db_table  = "sessions"
        app_label = "sesshuns"

