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

from django.db         import models

from datetime          import datetime, timedelta

from scheduler.models  import Observing_Type
from Allotment         import Allotment
from Backend           import Backend
from Monitoring        import Monitoring
from ObservingType     import ObservingType
from Period            import Period
from Proposal          import Proposal
from Receiver          import Receiver
from SessionSeparation import SessionSeparation
from SessionType       import SessionType
from Semester          import Semester
from SessionFlags      import SessionFlags
from SessionGrade      import SessionGrade
from Source            import Source
from Target            import Target
from WeatherType       import WeatherType

from pht.utilities import *

class Session(models.Model):

    proposal                = models.ForeignKey(Proposal)
    sources                 = models.ManyToManyField(Source)
    receivers               = models.ManyToManyField(Receiver, related_name = 'sessions')
    backends                = models.ManyToManyField(Backend)
    allotment               = models.ForeignKey(Allotment, null = True)
    target                  = models.ForeignKey(Target, null = True)
    session_type            = models.ForeignKey(SessionType, null = True)
    observing_type          = models.ForeignKey(Observing_Type, null = True)
    weather_type            = models.ForeignKey(WeatherType, null = True)
    semester                = models.ForeignKey(Semester, null = True)
    grade                   = models.ForeignKey(SessionGrade, null = True)
    flags                   = models.ForeignKey(SessionFlags, null = True)
    monitoring              = models.ForeignKey(Monitoring, null = True)
    receivers_granted       = models.ManyToManyField(Receiver) 
    pst_session_id          = models.IntegerField()
    name                    = models.CharField(max_length = 2000)
    
    # TBF: should separation and interval_time be in allotment?
    separation              = models.ForeignKey(SessionSeparation, null = True)
    interval_time           = models.IntegerField(null = True, ) # TBF: units of separation?
    constraint_field        = models.CharField(null = True, max_length = 2000)
    comments                = models.CharField(null = True, max_length = 2000)
    scheduler_notes         = models.TextField(null = True, blank = True)
    session_time_calculated = models.BooleanField(default = False)

    class Meta:
        db_table  = "pht_sessions"
        app_label = "pht"

    def __str__(self):
        return "%s (%d)" % (self.name, self.id)

    def get_lst_parameters(self):
        """
        Returns a dictionary of LST Exclusion and Inclusion
        params, each entry in the dict is a list of (low, high) LST float pairs.
        """
        params = {'LST Exclude' : [], 'LST Include' : []}
        for lst_type in params.keys():
            lows = [sp.float_value for sp in self.sessionparameter_set.filter(
              parameter__name = '%s Low' % lst_type).order_by('id')]
            highs = [sp.float_value for sp in self.sessionparameter_set.filter(
              parameter__name = '%s Hi' % lst_type).order_by('id')]
            params[lst_type] = zip(lows, highs)
        return params

    def get_lst_string(self):
        "Converts pair of LST Exclude/Include observing parameters into low-high string"
        lst   = self.get_lst_parameters()
        types = ['LST Include', 'LST Exclude']
        return [', '.join(
          ["%.2f-%.2f" % (low, hi) for low, hi in lst[t]]) for t in types]

    # Calling get_lst_parameters twice (for each lst_type) causes a performance drop
    # when load all the sessions.
    # I was able to shave off 4 seconds to the load time for sessions by using the 
    # method above.
    """
    def get_lst_string(self, lst_type):
        "Converts pair of LST Exclude/Include observing parameters into low-high string"
        return ', '.join(
          ["%.2f-%.2f" % (low, hi) for low, hi in self.get_lst_parameters()[lst_type]])
    """

    def get_receivers_granted(self):
        "Returns comma-separated string of rcvrs granted."
        return ','.join([r.abbreviation \
            for r in self.receivers_granted.all().order_by('freq_low')])

    def get_receivers(self):
        "Returns comma-separated string of rcvrs."
        return ','.join([r.abbreviation \
            for r in self.receivers.all().order_by('freq_low')])

    def get_highest_receiver(self):
        rcvrs = list(self.receivers.all().order_by('freq_low'))
        return rcvrs[-1] if len(rcvrs) > 0 else None

    def get_backends(self):
        "Returns comma-separated string of backends."
        return ','.join([r.abbreviation \
            for r in self.backends.all().order_by('name')])

    def determineSessionType(self):
        """
        What might you think this session's type should be 
        according to how it is currently setup?
        """

        type = None

        # TBF: i'm sure this algo needs refining.

        # First, all vlba or vlbi should be typed Fixed.
        pcode = self.proposal.pcode.lower()
        if 'vlba' in pcode or 'vlbi' in pcode:
            return SessionType.get_type('F')

        # Otherwise, use the proposal's observing types to determine
        # if this might be Windowed or Fixed.
        radar = ObservingType.objects.get(type = "Radar")
        monitoring = ObservingType.objects.get(type = "Monitoring")
        if radar in self.proposal.observing_types.all():
            return SessionType.get_type('F') # Fixed
        if monitoring in self.proposal.observing_types.all():
            return SessionType.get_type('W') # Windowed

        # Well, it must b some kind of of Open, so use the highest receiver
        # to determin it's category.
        highFreq2 = ['MBA', 'W', 'KFPA']
        highFreq1 = ['X', 'Ku', 'Ka', 'Q']
        r = self.get_highest_receiver()
        if r is not None:
            if r.abbreviation in highFreq2:
                type = SessionType.get_type('HF2')
            elif r.abbreviation in highFreq1:    
                type = SessionType.get_type('HF1')
            else:
                type = SessionType.get_type('LF')
    
        return type    

    def periodGenerationFrom(self):
        """
        Examines the monitor related parameters, and determines
        if and what kind of periods can be generated.
        """

        if self.canUseCustomSequence():
            return "custom_sequence"

        if self.canUseInnerLoop():
            if self.canUseOuterLoop():
                return "outer_loop"
            else:
                return "inner_loop"
        else:
            return None

    def canUseCustomSequence(self):
        "Does the session have sufficient info for this?"
        if (self.monitoring is not None) and (self.allotment.period_time is not None):
            seq = self.monitoring.custom_sequence
            return (seq is not None) and (seq != '') \
                and self.allotment.period_time is not None \
                and self.monitoring.start_time is not None
        else:
            return False

    def canUseInnerLoop(self):
        "Does the session have sufficient info for this?"
        return self.monitoring is not None \
            and self.allotment is not None \
            and self.monitoring.start_time is not None \
            and self.allotment.repeats is not None \
            and self.allotment.period_time is not None \
            and self.separation is not None \
            and self.interval_time is not None
    
    def canUseOuterLoop(self):
        "Does the session have sufficient info for this?"
        return self.monitoring is not None \
            and self.allotment is not None \
            and self.monitoring.outer_repeats is not None \
            and self.monitoring.outer_separation is not None \
            and self.monitoring.outer_interval is not None \
            and self.allotment.period_time is not None

    def genPeriods(self):
        "Generate periods, if possible, from monitoring params."

        oldPeriods = self.period_set.all()

        source = self.periodGenerationFrom()
        if source == "custom_sequence":
            r = self.genPeriodsFromCustomSequence()
        elif source == "inner_loop":
            r = self.genPeriodsFromInnerLoop()
        elif source == "outer_loop":
            r = self.genPeriodsFromOuterLoop()
        else:
            r = 0

        # if we created any, delete the old ones
        if r > 0:
            for p in oldPeriods:
                p.delete()

        return r    

    def genPeriodsFromCustomSequence(self):
        """
        Generate periods from the start time, period length, 
        and comma separated list of separations (1,30,60).
        """

        if not self.canUseCustomSequence():
            return 0 

        days = [int(d.strip()) \
            for d in self.monitoring.custom_sequence.split(',')]

        # first day must always be 1
        assert days[0] == 1
        # but the subsequent one's aren't separations, but days.
        # so, NOT x days after the last one, but day x.
        dts = genDateTimesFromDays(self.monitoring.start_time, days)
        ps = self.genPeriodsFromDates(dts, self.allotment.period_time)
        return len(ps)    

    def deletePeriods(self):
        for p in self.period_set.all():
            p.delete()

    def genPeriodsFromInnerLoop(self):
        "Uses session montitoring params to generate list of periods"
        days = self.genDaysFromInnerLoop()
        if len(days) > 0:
            dts = genDateTimesFromDaySeparations(self.monitoring.start_time, days)
            ps = self.genPeriodsFromDates(dts, self.allotment.period_time)
            return len(ps)
        else:
            return 0

    def genDaysFromInnerLoop(self):
        "Uses session montitoring params to generate list of days"
        if not self.canUseInnerLoop():
            return [] 

        # gather what we need
        start = self.monitoring.start_time 
        repeats = self.allotment.repeats 
        duration = self.allotment.period_time 
        interval = self.interval_time
        sep = 1 if self.separation.separation == 'day' else 7
            
        days = [1]
        for i in range(repeats - 1):
            days.append(interval*sep)
        return days

    def genPeriodsFromOuterLoop(self):
        "Uses session montitoring params to generate list of periods"
        days = self.genDaysFromOuterLoop()
        if len(days) > 0:
            dts = genDateTimesFromDaySeparations(self.monitoring.start_time
                                               , days)
            ps = self.genPeriodsFromDates(dts, self.allotment.period_time)
            return len(ps)
        else:
            return 0

    def genDaysFromOuterLoop(self):
        "Uses session montitoring params to generate list of days"
        if not self.canUseInnerLoop() or not self.canUseOuterLoop():
            return [] 

        # gather what we need - inner
        start = self.monitoring.start_time 
        repeats = self.allotment.repeats 
        duration = self.allotment.period_time 
        interval = self.interval_time
        sep = 1 if self.separation.separation == 'day' else 7
            
        # gather what we need - outer
        outerRepeats = self.monitoring.outer_repeats
        outerInterval = self.monitoring.outer_interval
        outerSep = 1 if self.monitoring.outer_separation.separation == 'day' else 7
        
        days = [1]
        for i in range(outerRepeats):
            for j in range(repeats - 1):
                days.append(interval*sep)
            if i < outerRepeats - 1:    
                days.append(outerInterval*outerSep)    
        return days        

    def genPeriodsFromDates(self, dts, duration):
        "Generates list of periods based of given start times and duration."
        ps = []
        for dt in dts:
            p = Period(session = self
                     , start = dt
                     , duration = duration 
                      )
            p.save()
            ps.append(p)
        return ps    

    @staticmethod
    def createFromSqlResult(proposal_id, result):
        """
        Creates a new Session instance initialized using the request from
        an SQL query.
        """

        separation = SessionSeparation.objects.get(separation = result['SEPARATION'].strip())
        session = Session(pst_session_id = result['session_id']
                          # Don't use result's because that's for the
                          # PST, not our GB PHT DB!
                        , proposal_id = proposal_id #result['PROPOSAL_ID']
                        , name = result['SESSION_NAME']
                        , separation = separation 
                        , interval_time = result['INTERVAL_TIME']
                        , constraint_field = result['CONSTRAINT_FIELD']
                        , comments = result['COMMENTS']
                        , session_time_calculated = result['SESSION_TIME_CALCULATED']
                        )

        session.save()
        return session
        
