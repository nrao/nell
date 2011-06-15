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

from django.db                import models
from django.db.models         import Q
from sets                     import Set

from nell.utilities           import TimeAgent, AnalogSet
from nell.utilities.receiver  import ReceiverCompile
from Allotment         import Allotment
from Observing_Type    import Observing_Type
from Parameter         import Parameter
from Project           import Project
from Receiver          import Receiver
from Receiver_Schedule import Receiver_Schedule
from Period_State      import Period_State
from Session_Type      import Session_Type
from Status            import Status
from System            import System

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

    def toHandle(self):
        if self.original_id is None:
            original_id = ""
        else:
            original_id = str(self.original_id)
        return "%s (%s) %s" % (self.name
                             , self.project.pcode
                             , original_id)

    @staticmethod
    def handle2session(h):
        n, p = h.rsplit('(', 1)
        name = n.strip()
        pcode, _ = p.split(')', 1)
        return Sesshun.objects.filter(project__pcode__exact=pcode).get(name=name)

    def isOpen(self):
        return self.session_type.type == "open"

    def isWindowed(self):
        return self.session_type.type == "windowed"

    def isElective(self):
        return self.session_type.type == "elective"

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
        rgs = [rg for rg in self.receiver_group_set.all() if rg.receivers.exists()]
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
        return self.receiver_group_set.count()

    def schedulable(self):
        "A simple check for all explicit flags"
        return (self.status.enabled) and \
               (self.status.authorized) and \
               (not self.status.complete) and \
               (not self.project.complete)

    def delete(self):
        self.allotment.delete()
        super(Sesshun, self).delete()

    def get_lst_parameters(self):
        params = {'LST Exclude' : [], 'LST Include' : []}
        for lst_type in params.keys():
            for op in self.observing_parameter_set.filter(
              parameter__name = '%s Low' % lst_type).order_by('id'):
               params[op.parameter.name.replace(' Low', '')].append([op.float_value])
            for i, op in enumerate(self.observing_parameter_set.filter(
              parameter__name = '%s Hi' % lst_type).order_by('id')):
               params[op.parameter.name.replace(' Hi', '')][i].append(op.float_value)
        return params

    def get_lst_string(self, lst_type):
        "Converts pair of LST Exclude/Include observing parameters into low-high string"
        return ', '.join(
          ["%.2f-%.2f" % (low, hi) for low, hi in self.get_lst_parameters()[lst_type]])

    def getTarget(self):
        try:
            return self.target
        except Target.DoesNotExist:
            return None

    def get_ra_dec(self):
        target = self.getTarget()
        if target is None:
            return None, None
        return target.vertical, target.horizontal

    def set_dec(self, new_dec):
        target = self.getTarget()
        if target is None:
            return
        target.horizontal = new_dec
        target.save()

    def get_receiver_req(self):
        rcvrs = [[r.abbreviation \
                     for r in rg.receivers.all().order_by('id')] \
                         for rg in self.receiver_group_set.all().order_by('id')]
        rc = ReceiverCompile(Receiver.get_abbreviations())
        return rc.denormalize(rcvrs)

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
        
        # the call to unions won't accept the None used
        # sometimes by get_receiver_blackout_range, so substitue in
        # the given boundries for these
        newDts = []
        for (s, e) in list(dts):
            if s is None:
                s = start
            if e is None:
                e = end
            newDts.append((s,e))
            
        return sorted(AnalogSet.unions(newDts))

    def trim_events(self, events, start, end):
        """
        Events is a list of datetime tuples [(start, end)].
        Many of the functions that return these events will return 
        events that overlap with the given start, end boundries.  Here
        we trim any of these overlaps so that no events returned go beyond
        the given start, end.
        """
        if len(events) == 0:
            return []

        if events[0][0] < start:
            events[0] = (start, events[0][1])
        if events[-1][1] > end:
            events[-1] = (events[-1][0], end)
        return events    

    def compliment_events(self, events, start, end):
        """
        For a given set of datetime tuples of the form (start, end) which
        falls in the range of the given start, end, what is the
        complimentary set of events.  That is, what are the other events,
        togethor with the given events, which completely cover the given
        start, end range?
        """
        return AnalogSet.diffs([(start, end)], events)
    
    def getBlackedOutSchedulableTime(self, start, end):
        """
        Of the hours in the given range that are schedulable,
        how many have been blacked out?
        Returns tuple of hours (scheduble but ignoring blackouts
                              , scheduable but blacked out)
        Returns tuple of (scheduable but ignoring blackouts total
                        , scheduable but blacked out total
                        , [2-tuple of scheduable-but-ignoring-blackouts range)]
                        , [[2-tuple of scheduable-but-blacked-out-range]])
        """
        nss1 = self.get_time_not_schedulable(start
                                           , end
                                           , blackouts = False)

        nss = self.trim_events(nss1, start, end)

        # now convert the non-schedulable time ranges to the 
        # time that IS schedulable:
        schedulable = self.compliment_events(nss, start, end)
 
        # how much time is that?
        hrsSchedulable = sum([TimeAgent.timedelta2minutes(s[1] - s[0])/60.0 \
            for s in schedulable])

        # now, for each chunk of schedulable time, how much is
        # blacked out?
        hrsBlackedOut = 0.0
        bss = []
        #print "schedulable loop:"
        for s in schedulable:
            bs = self.project.get_blackout_times(s[0], s[1])
            # but these blackout times might not match to the schedulable
            # end points, so we may need to truncate them
            bs = self.trim_events(bs, s[0], s[1])
            if len(bs) != 0:
                bss.append(bs)
            bsTime = sum([TimeAgent.timedelta2minutes(b[1] - b[0])/60.0
                          for b in bs])
            hrsBlackedOut += bsTime

        # return a summary of what we've found
        return (hrsSchedulable
              , hrsBlackedOut
              , schedulable
              , bss)           

    class Meta:
        db_table  = "sessions"
        app_label = "scheduler"

    def getBlackedOutSchedulablePeriods(self, now):
        """
        Of the future periods for this session overlapping in the time
        range that are not deleted or completed, which schedulable ones
        have been blacked out?  Returns a list of offending periods.
        """
        state = Period_State.get_state('D')
        ps = self.period_set.exclude(state=state).filter(start__gte=now).order_by('start')
        periods = list(ps)
        if not periods:
            return []
        pranges = [(p.start, p.end(), p) for p in periods]
        start = max(now, pranges[0][0])
        _, _, _, brs = \
            self.getBlackedOutSchedulableTime(start
                                            , pranges[-1][1])
        branges = [r for sublist in brs for r in sublist] # flatten lists

        retval = []
        for p in pranges:
            for b in branges:
                if p[0] < b[1] and b[0] < p[1]:
                    retval.append(p[2])
                    break
        return retval

    def getPeriodRange(self):
        state = Period_State.get_state('D')
        ps = self.period_set.exclude(state=state).order_by('start')
        periods = list(ps)
        if periods:
            return [periods[0].start, periods[-1].end()]
        else:
            return []
