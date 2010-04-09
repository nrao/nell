from django.db import models
from math      import modf
from utilities import TimeAgent

from Allotment      import Allotment
from common         import *
from Observing_Type import Observing_Type
from Parameter      import Parameter
from Project        import Project
from Receiver       import Receiver
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

    def set_base_fields(self, fdata):
        fsestype = fdata.get("type", "open")
        fobstype = fdata.get("science", "testing")
        proj_code = fdata.get("pcode", "GBT09A-001")

        p  = first(Project.objects.filter(pcode = proj_code).all()
                 , Project.objects.all()[0])
        st = first(Session_Type.objects.filter(type = fsestype).all()
                 , Session_Type.objects.all()[0])
        ot = first(Observing_Type.objects.filter(type = fobstype).all()
                 , Observing_Type.objects.all()[0])

        self.project          = p
        self.session_type     = st
        self.observing_type   = ot
        self.original_id      = \
            self.get_field(fdata, "orig_ID", None, lambda x: int(float(x)))
        self.name             = fdata.get("name", None)
        self.frequency        = fdata.get("freq", None)
        self.max_duration     = TimeAgent.rndHr2Qtr(float(fdata.get("req_max", 12.0)))
        self.min_duration     = TimeAgent.rndHr2Qtr(float(fdata.get("req_min",  3.0)))
        self.time_between     = fdata.get("between", None)

    def get_field(self, fdata, key, defaultValue, cast):
        "Some values from the JSON dict we know we need to type cast"
        value = fdata.get(key, defaultValue)
        if cast != bool:
            return value if value is None else cast(value)
        else:
            return value == "true"

    def init_from_post(self, fdata):
        self.set_base_fields(fdata)

        allot = Allotment(psc_time          = fdata.get("PSC_time", 0.0)
                        , total_time        = fdata.get("total_time", 0.0)
                        , max_semester_time = fdata.get("sem_time", 0.0)
                        , grade             = fdata.get("grade", 4.0)
                          )
        allot.save()
        self.allotment        = allot

        status = Status(
                   enabled    = self.get_field(fdata, "enabled", True, bool)
                 , authorized = self.get_field(fdata, "authorized", True, bool)
                 , complete   = self.get_field(fdata, "complete", True, bool) 
                 , backup     = self.get_field(fdata, "backup", True, bool) 
                        )
        status.save()
        self.status = status
        self.save()
        
        proposition = fdata.get("receiver")
        self.save_receivers(proposition)
        
        system = first(System.objects.filter(name = "J2000").all()
                     , System.objects.all()[0])

        v_axis = fdata.get("source_v", None)
        h_axis = fdata.get("source_h", None)
        
        target = Target(session    = self
                      , system     = system
                      , source     = fdata.get("source", None)
                      , vertical   = v_axis
                      , horizontal = h_axis
                        )
        target.save()
        self.save()

    def save_receivers(self, proposition):
        abbreviations = [r.abbreviation for r in Receiver.objects.all()]
        # TBF catch errors and report to user
        rc = ReceiverCompile(abbreviations)
        ands = rc.normalize(proposition)
        for ors in ands:
            # TBF:  Caused recursive import during model separation
            rg = Receiver_Group(session = self)
            rg.save()
            for rcvr in ors:
                rcvrId = Receiver.objects.filter(abbreviation = rcvr)[0]
                rg.receivers.add(rcvrId)
                rg.save()

    def update_from_post(self, fdata):
        self.set_base_fields(fdata)
        self.save()

        self.allotment.psc_time          = fdata.get("PSC_time", 0.0)
        self.allotment.total_time        = fdata.get("total_time", 0.0)
        self.allotment.max_semester_time = fdata.get("sem_time", 0.0)
        self.allotment.grade             = fdata.get("grade", 4.0)
        self.allotment.save()
        self.save()

        self.status.enabled    = self.get_field(fdata, "enabled", True, bool) 
        self.status.authorized = self.get_field(fdata, "authorized", True, bool)
        self.status.complete   = self.get_field(fdata, "complete", True, bool) 
        self.status.backup     = self.get_field(fdata, "backup", True, bool) 
        self.status.save()
        self.save()

        self.update_bool_obs_param(fdata, "transit", "Transit", self.transit())
        self.update_bool_obs_param(fdata, "nighttime", "Night-time Flag", \
            self.nighttime())
        self.update_lst_exclusion(fdata)    
        self.update_xi_obs_param(fdata, self.get_min_eff_tsys_factor())

        proposition = fdata.get("receiver", None)
        if proposition is not None:
            self.receiver_group_set.all().delete()
            self.save_receivers(proposition)

        system = first(System.objects.filter(name = "J2000").all()
                     , System.objects.all()[0])

        v_axis = fdata.get("source_v", None)
        h_axis = fdata.get("source_h", None)

        t            = first(self.target_set.all())
        t.system     = system
        t.source     = fdata.get("source", None)
        t.vertical   = v_axis if v_axis is not None else t.vertical
        t.horizontal = h_axis if h_axis is not None else t.horizontal
        t.save()

        self.save()

    def update_xi_obs_param(self, fdata, old_value):
        """
        For taking a json dict and converting its given
        xi float field into a 'Min Eff TSys' float observing parameter.
        """
        new_value = self.get_field(fdata, "xi_factor", 1.0, float)
        tp = Parameter.objects.filter(name="Min Eff TSys")[0]
        if old_value is None:
            if new_value and new_value != 1.0:
                obs_param =  Observing_Parameter(session = self
                                               , parameter = tp
                                               , float_value = new_value
                                                )
                obs_param.save()
        else:
            obs_param = self.observing_parameter_set.filter(parameter=tp)[0]
            if new_value and new_value != 1.0:
                obs_param.float_value = new_value
                obs_param.save()
            else:
                obs_param.delete()

    def update_bool_obs_param(self, fdata, json_name, name, old_value):
        """
        Generic method for taking a json dict and converting its given
        boolean field into a boolean observing parameter.
        """

        new_value = self.get_field(fdata, json_name, False, bool)
        tp = Parameter.objects.filter(name=name)[0]
        if old_value is None:
            if new_value:
                # TBF:  Caused recursion
                obs_param =  Observing_Parameter(session = self
                                               , parameter = tp
                                               , boolean_value = True
                                                )
                obs_param.save()
        else:
            obs_param = self.observing_parameter_set.filter(parameter=tp)[0]
            if new_value:
                obs_param.boolean_value = True
                obs_param.save()
            else:
                obs_param.delete()

    def update_lst_exclusion(self, fdata):
        """
        Converts the json representation of the LST exclude flag
        to the model representation.
        """
        lowParam = first(Parameter.objects.filter(name="LST Exclude Low"))
        hiParam  = first(Parameter.objects.filter(name="LST Exclude Hi"))
        
        # json dict string representation
        lst_ex_string = fdata.get("lst_ex", None)
        if lst_ex_string:
            # unwrap and get the float values
            lowStr, highStr = lst_ex_string.split("-")
            low = float(lowStr)
            high = float(highStr)
            assert low <= high

        # get the model's string representation
        current_lst_ex_string = self.get_LST_exclusion_string()

        if current_lst_ex_string == "":
            if lst_ex_string:
                # create a new LST Exlusion range
                obs_param =  Observing_Parameter(session = self
                                               , parameter = lowParam
                                               , float_value = low 
                                                )
                obs_param.save()
                obs_param =  Observing_Parameter(session = self
                                               , parameter = hiParam
                                               , float_value = high 
                                                )
                obs_param.save()
            else:
                # they are both none, nothing to do
                pass
        else:
            # get the current model representation (NOT the string) 
            lowObsParam = \
                first(self.observing_parameter_set.filter(parameter=lowParam))
            highObsParam = \
                first(self.observing_parameter_set.filter(parameter=hiParam))
            if lst_ex_string:
                lowObsParam.float_value = low
                lowObsParam.save()
                highObsParam.float_value = high
                highObsParam.save()
            else:
                lowObsParam.delete()
                highObsParam.delete()


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
        nn = Receiver.get_abbreviations()
        rc = ReceiverCompile(nn)

        rcvrs = [[r.abbreviation \
                     for r in rg.receivers.all()] \
                         for rg in self.receiver_group_set.all()]
        return rc.denormalize(rcvrs)

    def get_ha_limit_blackouts(self, startdate, days):
        # TBF: Not complete or even correct yet.

        targets = [(t.horizontal, t.vertical) for t in self.target_set.all()]

        # startdate, days, self.frequency, targets
        #url       = "?"
        #blackouts = json.load(urlllib.urlopen(url))['blackouts']

        #return consolidate_events(find_intersections(blackouts))

    def getObservedTime(self):
        return TimeAccounting().getTime("observed", self)

    def getTimeBilled(self):
        return TimeAccounting().getTime("time_billed", self)

    def getTimeRemaining(self):
        return TimeAccounting().getTimeRemaining(self)

    def jsondict(self):
        d = {"id"         : self.id
           , "pcode"      : self.project.pcode
           , "type"       : self.session_type.type
           , "science"    : self.observing_type.type
           , "total_time" : self.allotment.total_time
           , "PSC_time"   : self.allotment.psc_time
           , "sem_time"   : self.allotment.max_semester_time
           , "remaining"  : self.getTimeRemaining()
           , "grade"      : self.allotment.grade
           , "orig_ID"    : self.original_id
           , "name"       : self.name
           , "freq"       : self.frequency
           , "req_max"    : self.max_duration
           , "req_min"    : self.min_duration
           , "between"    : self.time_between
           , "enabled"    : self.status.enabled
           , "authorized" : self.status.authorized
           , "complete"   : self.status.complete
           , "backup"     : self.status.backup
           , "transit"    : self.transit() or False
           , "nighttime"  : self.nighttime() or False
           , "lst_ex"     : self.get_LST_exclusion_string() or ""
           , "receiver"   : self.get_receiver_req()
           , "project_complete" : "Yes" if self.project.complete else "No"
           , "xi_factor"  : self.get_min_eff_tsys_factor() or 1.0
            }

        target = first(self.target_set.all())
        if target is not None:
            d.update({"source"     : target.source
                    , "coord_mode" : target.system.name
                    , "source_h"   : target.horizontal
                    , "source_v"   : target.vertical
                      })

        #  Remove all None values
        for k, v in d.items():
            if v is None:
                _ = d.pop(k)

        return d

    def transit(self):
        """
        Returns True or False if has 'Transit' observing parameter,
        else None if not.
        """
        return self.has_bool_obs_param("Transit")

    def get_min_eff_tsys_factor(self):
        """
        Returns factor if has 'Min Eff TSys' observing parameter,
        else None.
        """
        return self.has_float_obs_param("Min Eff TSys")

    def nighttime(self):
        """
        Returns True or False if has 'Night-time Flag' observing parameter,
        else None if not.
        """
        return self.has_bool_obs_param("Night-time Flag")

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

    class Meta:
        db_table  = "sessions"
        app_label = "sesshuns"

class Target(models.Model):
    session    = models.ForeignKey(Sesshun)
    system     = models.ForeignKey(System)
    source     = models.CharField(null = True, max_length = 32, blank = True)
    vertical   = models.FloatField(null = True, blank = True)
    horizontal = models.FloatField(null = True, blank = True)

    def __str__(self):
        return "%s at %s : %s" % (self.source
                                , self.horizontal
                                , self.vertical
                                  )

    def __unicode__(self):
        return "%s @ (%5.2f, %5.2f), Sys: %s" % \
            (self.source
           , float(self.horizontal)
           , float(self.vertical)
           , self.system)

    def get_horizontal(self):
        "Returns the horizontal component in sexigesimal form."
        if self.horizontal is None:
            return ""

        horz = TimeAgent.rad2hr(self.horizontal)
        mins = (horz - int(horz)) * 60
        secs = (mins - int(mins)) * 60
        if abs(secs - 60.) < 0.1:
            mins = int(mins) + 1
            if abs(mins - 60.) < 0.1:
                mins = 0.0
                horz = int(horz) + 1
            secs = 0.0
        return "%02i:%02i:%04.1f" % (int(horz), int(mins), secs)

    def get_vertical(self):
        if self.vertical is None:
            return ""

        degs = TimeAgent.rad2deg(self.vertical)

        if degs < 0:
            degs = abs(degs)
            sign = "-"
        else:
            sign = " "

        fpart, ddegs = modf(degs)
        fpart, dmins = modf(fpart * 60)
        dsecs = round(fpart * 60, 1)

        if dsecs > 59.9:
            dmins = dmins + 1
            dsecs = 0.0
        if dmins > 59.9:
            ddegs = ddegs + 1
            dmins = 0.0

        return "%s%02i:%02i:%04.1f" % (sign, int(ddegs), int(dmins), dsecs)

    class Meta:
        db_table  = "targets"
        app_label = "sesshuns"

class Receiver_Group(models.Model):
    session        = models.ForeignKey(Sesshun)
    receivers      = models.ManyToManyField(
                                  Receiver
                                , db_table = "receiver_groups_receivers")

    class Meta:
        db_table  = "receiver_groups"
        app_label = "sesshuns"

    def __unicode__(self):
        return "Rcvr Group for Sess: (%s): %s" % \
               (self.session.id,
                " ".join([r.abbreviation for r in self.receivers.all()]))

    def __str__(self):
        return "(%s)" % \
               " OR ".join([r.abbreviation for r in self.receivers.all()])

class Observing_Parameter(models.Model):
    session        = models.ForeignKey(Sesshun)
    parameter      = models.ForeignKey(Parameter)
    string_value   = models.CharField(null = True, max_length = 64, blank = True)
    integer_value  = models.IntegerField(null = True, blank = True)
    float_value    = models.FloatField(null = True, blank = True)
    boolean_value  = models.NullBooleanField(null = True, blank = True)
    datetime_value = models.DateTimeField(null = True, blank = True)

    class Meta:
        db_table        = "observing_parameters"
        unique_together = ("session", "parameter")
        app_label       = "sesshuns"

    def value(self):
        if self.parameter.type == "string":
            return self.string_value
        elif self.parameter.type == "integer":
            return self.integer_value
        elif self.parameter.type == "float":
            return self.float_value
        elif self.parameter.type == "boolean":
            return self.boolean_value
        elif self.parameter.type == "datetime":
            return self.datetime_value
        else:
            return None

    def __unicode__(self):
        if self.string_value is not None:
            value = self.string_value
        elif self.integer_value is not None:
            value = str(self.integer_value)
        elif self.float_value is not None:
            value = str(self.float_value)
        elif self.boolean_value is not None:
            value = str(self.boolean_value)
        elif self.datetime_value is not None:
            value = str(self.datetime_value)
        else:
            value = ""
        return "%s with value %s for Sesshun (%d)" % (self.parameter
                                                    , value
                                                    , self.session.id)

