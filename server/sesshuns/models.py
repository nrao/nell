from datetime                  import datetime, timedelta
from math                      import asin, acos, cos, sin
from django.db                 import models
from django.http               import QueryDict

from server.utilities          import OpportunityGenerator, TimeAgent
from server.utilities.receiver import ReceiverCompile

import sys

def first(results, default = None):
    return default if len(results) == 0 else results[0]

def str2dt(str):
    if str is None:
        return None

    if ' ' in str:
        d, t      = str.split(' ')
        m, d, y  = map(int, d.split('/'))
        time      = t.split(':')
        h, mm, ss = map(int, map(float, time))
        return datetime(y, m, d, h, mm, ss)
    m, d, y   = map(int, str.split('/'))
    return datetime(y, m, d)

jsonMap = {"authorized"     : "status__authorized"
         , "between"        : "time_between"
         , "backup"         : "status__backup"
         , "pcode"          : "project__pcode"
         , "cad_start_date" : "cadence__start_date"
         , "cad_repeats"    : "cadence__repeats"
         , "cad_intervals"  : "cadence__intervals"
         , "cad_duration"   : "cadence__full_size"
         , "complete"       : "status__complete"
         , "coord_mode"     : "target__system__name"
         , "enabled"        : "status__enabled"
         , "freq"           : "frequency"
         , "grade"          : "allotment__grade"
         , "id"             : "id"
         , "name"           : "name"
         , "orig_ID"        : "original_id"
# TBF         , "receiver"   : "rcvrs"
         , "PSC_time"       : "allotment__psc_time"
         , "req_max"        : "max_duration"
         , "req_min"        : "min_duration"
         , "science"        : "observing_type__type"
         , "selected"       : "selected"
         , "sem_time"       : "allotment__max_semester_time"
         , "source"         : "target__source"
         , "source_h"       : "target__horizontal"
         , "source_v"       : "target__vertical"
         , "total_time"     : "allotment__total_time"
         , "type"           : "session_type__type"
               }

class User(models.Model):
    original_id = models.IntegerField()
    pst_id      = models.IntegerField(null = True)
    username    = models.CharField(max_length = 32, null = True)
    sancioned   = models.BooleanField()
    first_name  = models.CharField(max_length = 32)
    last_name   = models.CharField(max_length = 150)

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    class Meta:
        db_table = "users"

class Email(models.Model):
    user  = models.ForeignKey(User)
    email = models.CharField(max_length = 255)

class Semester(models.Model):
    semester = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.semester

    class Meta:
        db_table = "semesters"

class Project_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type

    class Meta:
        db_table = "project_types"

class Allotment(models.Model):
    psc_time          = models.FloatField()
    total_time        = models.FloatField()
    max_semester_time = models.FloatField()
    grade             = models.FloatField()

    def __unicode__(self):
        return "Total: %5.2f, Grade: %5.2f, PSC: %5.2f, Max: %5.2f" % \
                                       (self.total_time
                                      , self.grade
                                      , self.psc_time
                                      , self.max_semester_time) 

    class Meta:
        db_table = "allotment"
        
class Project(models.Model):
    semester     = models.ForeignKey(Semester)
    project_type = models.ForeignKey(Project_Type)
    allotments   = models.ManyToManyField(Allotment)
    pcode        = models.CharField(max_length = 32)
    name         = models.CharField(max_length = 150)
    thesis       = models.BooleanField()
    complete     = models.BooleanField()
    ignore_grade = models.BooleanField()
    start_date   = models.DateTimeField(null = True)
    end_date     = models.DateTimeField(null = True)

    def __unicode__(self):
        return "%s, %s, %s" % (self.name, self.semester, self.pcode)

    def __str__(self):
        return self.pcode
    
    def principal_contact(self):
        "Who is the principal contact for this Project?"
        pc = None
        for inv in self.investigators_set.all():
            # if more then one, it's arbitrary
            if inv.principal_contact:
                pc = inv.user
        return pc        

    def rcvrs_specified(self):
        "Returns an array of rcvrs for this project, w/ out their relations"
        # For use in recreating Carl's reports
        rcvrs = []
        for s in self.sesshun_set.all():
            rs = s.rcvrs_specified()
            for r in rs:
                if r not in rcvrs:
                    rcvrs.append(r)
        return rcvrs            

    class Meta:
        db_table = "projects"

class Investigators(models.Model):
    project           = models.ForeignKey(Project)
    user              = models.ForeignKey(User)
    friend            = models.BooleanField(default = False)
    observer          = models.BooleanField(default = False)
    principal_contact = models.BooleanField(default = False)
    priority          = models.IntegerField(default = 1)

    def __unicode__(self):
        return "%s (%d) for %s; fr : %s, obs : %s, PI : %s" % \
            ( self.user
            , self.user.id
            , self.project.pcode
            , self.friend
            , self.observer
            , self.principal_contact )

    class Meta:
        db_table = "investigators"

class Session_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type

    class Meta:
        db_table = "session_types"

class Observing_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type

    class Meta:
        db_table = "observing_types"

class Receiver(models.Model):
    name         = models.CharField(max_length = 32)
    abbreviation = models.CharField(max_length = 32)
    freq_low     = models.FloatField()
    freq_hi      = models.FloatField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "receivers"

    @staticmethod
    def get_abbreviations():
        return [r.abbreviation for r in Receiver.objects.all()]

class Receiver_Schedule(models.Model):
    receiver   = models.ForeignKey(Receiver)
    start_date = models.DateTimeField(null = True)
    end_date   = models.DateTimeField(null = True)

    def __unicode__(self):
        return "Availability for %d: %s - %s" % \
          ( self.receiver.name
          , self.start_date
          , self.end_date)

    class Meta:
        db_table = "receiver_schedule"

class Parameter(models.Model):
    name = models.CharField(max_length = 64)
    type = models.CharField(max_length = 32)

    def __unicode__(self):
        return "%s : %s" % (self.name, self.type)

    class Meta:
        db_table = "parameters"

class Status(models.Model):
    enabled    = models.BooleanField()
    authorized = models.BooleanField()
    complete   = models.BooleanField()
    backup     = models.BooleanField()

    def __unicode__(self):
        return "e: %s; a: %s; c: %s; b: %s" % \
            (self.enabled, self.authorized, self.complete, self.backup)

    class Meta:
        db_table = "status"
    
class Sesshun(models.Model):
    
    project            = models.ForeignKey(Project)
    session_type       = models.ForeignKey(Session_Type)
    observing_type     = models.ForeignKey(Observing_Type)
    allotment          = models.ForeignKey(Allotment)
    status             = models.ForeignKey(Status)
    original_id        = models.IntegerField(null = True)
    name               = models.CharField(null = True
                                        , max_length = 64)
    frequency          = models.FloatField(null = True)
    max_duration       = models.FloatField(null = True)
    min_duration       = models.FloatField(null = True)
    time_between       = models.FloatField(null = True)
    selected           = models.BooleanField(default = False)

    restrictions = "Unrestricted" # TBF Do we still need restrictions?

    def __unicode__(self):
        return "(%d) %s : %5.2f GHz, %5.2f Hrs, Rcvrs: %s" % (self.id
                                            , self.name if self.name is not None else ""
                                            , self.frequency if self.frequency is not None else 0
                                            , self.allotment.total_time if self.allotment.total_time is not None else 0
                                            , self.receiver_list())

    def receiver_list(self):
        "Returns a string representation of the rcvr logic."
        return " AND ".join([rg.__str__() for rg in self.receiver_group_set.all()])

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
        
    def letter_grade(self):
        return self.grade_float_2_abc(self.allotment.grade)

    def num_rcvr_groups(self):
        return len(self.receiver_group_set.all())

    def scheduable(self):
        "A simple check for all explicit flags"
        return (self.status.enabled) and \
               (self.status.authorized) and \
               (not self.status.complete)

    def delete(self):
        self.allotment.delete()
        super(Sesshun, self).delete()

    def set_base_fields(self, fdata):
        fsestype = fdata.get("type", "open")
        fobstype = fdata.get("science", "testing")
        proj_code = fdata.get("proj_code", "GBT09A-001")

        p  = first(Project.objects.filter(pcode = proj_code).all())
        st = first(Session_Type.objects.filter(type = fsestype).all()
                 , Session_Type.objects.all()[0])
        ot = first(Observing_Type.objects.filter(type = fobstype).all()
                 , Observing_Type.objects.all()[0])

        self.project          = p
        self.session_type     = st
        self.observing_type   = ot
        self.original_id      = \
            self.get_field(fdata, "orig_ID", None, self.cast_int)
        self.name             = fdata.get("name", None)
        self.frequency        = fdata.get("freq", None)
        self.max_duration     = fdata.get("req_max", 12.0)
        self.min_duration     = fdata.get("req_min",  3.0)
        self.time_between     = fdata.get("between", None)
        self.selected         = fdata.get("selected", False)

    def cast_int(self, strValue):
        "Handles casting of strings where int is displayed as float. ex: 1.0"
        return int(float(strValue))

    def get_field(self, fdata, key, defaultValue, cast):
        "Some values from the JSON dict we know we need to type cast"
        value = fdata.get(key, defaultValue)
        return value if value is None else cast(value) 

    def grade_abc_2_float(self, abc):
        grades = {'A' : 4.0, 'B' : 3.0, 'C' : 2.0}
        return grades.get(abc, None)

    def grade_float_2_abc(self, grade):
        grades = ['A', 'B', 'C']
        floats = [4.0, 3.0, 2.0]
        gradeLetter = 'C'
        for i in range(len(grades)):
            if grade >= (floats[i] - 10e-5):
                gradeLetter = grades[i]
                break
        return gradeLetter

    def validate(self, fdata):
        "Detect illegal values in client modifications to the model."
        """
        # Validate frequency/receiver settings
        given_frequency = fdata.get("frequency", None)
        given_receivers  = fdata.get("receiver", None)
        # Has the frequency changed?
        if frequency and frequency != self.frequency:
            default_receiver = Receiver.getDefault(given_frequency)
            # Do the specified receivers include the one for this frequency?
            if default_receiver != "NS" and \
               not default_receiver.find(given_receivers):
                return False
        """
        return True

    def init_from_post(self, fdata):
        self.set_base_fields(fdata)

        # grade - UI deals w/ letters (A,B,C) - DB deals with floats
        grade = self.grade_abc_2_float(fdata.get("grade", 'A'))
        allot = Allotment(psc_time          = fdata.get("PSC_time", 0.0)
                        , total_time        = fdata.get("total_time", 0.0)
                        , max_semester_time = fdata.get("sem_time", 0.0)
                        , grade             = grade
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

        v_axis = fdata.get("v_axis", 2.0) #TBF
        h_axis = fdata.get("h_axis", 2.0) #TBF
        
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
            rg = Receiver_Group(session = self)
            rg.save()
            for rcvr in ors:
                rcvrId = Receiver.objects.filter(abbreviation = rcvr)[0]
                rg.receivers.add(rcvrId)
                rg.save()

    def get_cadence(self):
        c = first(self.cadence_set.all())
        if c is None:
            return Cadence(session = self)
        return c

    def create_update_cadence(self, fdata):
        start_date = str2dt(fdata.get("cad_start_date", None))
        end_date   = str2dt(fdata.get("cad_end_date", None))
        repeats    = fdata.get("cad_repeats", None)
        intervals  = fdata.get("cad_intervals", None)
        full_size  = fdata.get("cad_full_size", None)

        if start_date is not None or \
           end_date is not None or \
           repeats is not None or \
           full_size is not None or \
           intervals is not None:
            c = self.get_cadence()
            c.set_fields(start_date, end_date, repeats, full_size, intervals)
        
    def update_from_post(self, fdata):
        self.set_base_fields(fdata)
        self.save()

        # grade - UI deals w/ letters (A,B,C) - DB deals with floats
        grade = self.grade_abc_2_float(fdata.get("grade", 'A'))
        self.allotment.psc_time          = fdata.get("PSC_time", 0.0)
        self.allotment.total_time        = fdata.get("total_time", 0.0)
        self.allotment.max_semester_time = fdata.get("sem_time", 0.0)
        self.allotment.grade             = grade
        self.allotment.save()
        self.save()

        # TBF DO SOMETHING WITH RECEIVERS!

        self.status.enabled    = self.get_field(fdata, "enabled", True, bool) 
        self.status.authorized = self.get_field(fdata, "authorized", True, bool)
        self.status.complete   = self.get_field(fdata, "complete", True, bool) 
        self.status.backup     = self.get_field(fdata, "backup", True, bool) 
        self.status.save()
        self.save()

        proposition = fdata.get("receiver", None)
        if proposition is not None:
            self.receiver_group_set.all().delete()
            self.save_receivers(proposition)

        system = first(System.objects.filter(name = "J2000").all()
                     , System.objects.all()[0])

        v_axis = fdata.get("v_axis", 2.0) #TBF
        h_axis = fdata.get("h_axis", 2.0) #TBF

        t            = self.target_set.get()
        t.system     = system
        t.source     = fdata.get("source", None)
        t.vertical   = v_axis
        t.horizontal = h_axis
        t.save()

        self.create_update_cadence(fdata)
        self.save()

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
        rgs = self.receiver_group_set.all()
        ands = []
        for rg in rgs:
            rs = rg.receivers.all()
            ands.append(' | '.join([r.abbreviation for r in rs]))
        if len(ands) == 1:
            return ands[0]
        else:
            return ' & '.join(['(' + rg + ')' for rg in ands])
        
    def jsondict(self):
        target  = first(self.target_set.all())
        rcvrs  = self.get_receiver_req()
        cadence = first(self.cadence_set.all())

        d = {"id"         : self.id
           , "pcode"      : self.project.pcode
           , "type"       : self.session_type.type
           , "science"    : self.observing_type.type
           , "total_time" : self.allotment.total_time
           , "PSC_time"   : self.allotment.psc_time
           , "sem_time"   : self.allotment.max_semester_time
           , "grade"      : self.grade_float_2_abc(self.allotment.grade)
           , "orig_ID"    : self.original_id
           , "name"       : self.name
           , "freq"       : self.frequency
           , "req_max"    : self.max_duration
           , "req_min"    : self.min_duration
           , "between"    : self.time_between
           , "selected"   : self.selected
           , "enabled"    : self.status.enabled
           , "authorized" : self.status.authorized
           , "complete"   : self.status.complete
           , "backup"     : self.status.backup
               }

        if rcvrs is not None:
            d.update({"receiver"   : rcvrs})
            
        if target is not None:
            d.update({"source"     : target.source
                    , "coord_mode" : target.system.name
                    , "source_h"   : target.horizontal
                    , "source_v"   : target.vertical
                      })

        if cadence is not None:
            sd = None if cadence.start_date is None \
                else cadence.start_date.strftime("%m/%d/%Y")
            ed = None if cadence.end_date is None \
                else cadence.end_date.strftime("%m/%d/%Y")
            d.update({"cad_start_date" : sd
                    , "cad_end_date"   : ed
                    , "cad_repeats"    : cadence.repeats
                    , "cad_intervals"  : cadence.intervals
                      })
            
        #  Remove all None values
        for k, v in d.items():
            if v is None:
                _ = d.pop(k)

        return d

    def hourAngleAtHorizon(self):
        "Returns the absolute hour angle in hours at the telescope limits."
        _, dec = self.get_ra_dec()
        lat = TimeAgent.GbtLatitudeInRadians()
        dec = TimeAgent.deg2rad(dec)
        za  = TimeAgent.deg2rad(85)

        # Are we looking at polaris or thereabouts?
        denominator = cos(lat)*cos(dec)
        if abs(denominator) <= 1e-3:
            return 12.0

        cosha = (cos(za) - sin(lat)*sin(dec))/denominator
        # Dropped below the horizon?
        if abs(cosha) >= 1:
            return 12.0
        ha = TimeAgent.rad2hr(acos(cosha))
        return abs(ha)

    def zenithAngle(self, dt):
        "Returns zenith angle at the given time in degrees."
        ra, dec = self.get_ra_dec()
        lat = TimeAgent.GbtLatitudeInRadians()
        dec = TimeAgent.deg2rad(dec)
        ra  = TimeAgent.hr2rad(ra)
        lst = TimeAgent.hr2rad(TimeAgent.Absolute2RelativeLST(dt))
        ha  = lst - ra
            
        # Equation (5) in DS Project Note 5.2
        radians = acos(sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(ha))
        return TimeAgent.rad2deg(radians)

    class Meta:
        db_table = "sessions"

class Cadence(models.Model):
    session    = models.ForeignKey(Sesshun)
    start_date = models.DateTimeField(null = True)
    end_date   = models.DateTimeField(null = True)
    repeats    = models.IntegerField(null = True)
    full_size  = models.CharField(null = True, max_length = 64)
    intervals  = models.CharField(null = True, max_length = 64)

    class Meta:
        db_table = "cadences"

    def __unicode__(self):
        return "Cadence for Sess (%d): %s - %s, r:%d, size: %s ints: %s" % \
          ( self.session.id
          , self.start_date
          , self.end_date
          , self.repeats
          , self.full_size
          , self.intervals )

    def init_from_post(self, s_id, fdata):
        s    = first(Sesshun.objects.filter(id = s_id))
        c    = s.get_cadence()

        start_date = str2dt(fdata.get("start_date", None))
        end_date   = str2dt(fdata.get("end_date", None))
        repeats    = fdata.get("repeats", None)
        intervals  = fdata.get("intervals", None)
        full_size  = fdata.get("full_size", None)
        self.set_fields(start_date, end_date, repeats, full_size, intervals)

    def set_fields(self, start_date, end_date, repeats, full_size, intervals):
        self.start_date = start_date
        self.end_date   = end_date
        self.repeats    = int(float(repeats)) if repeats is not None else repeats
        self.intervals  = intervals
        self.full_size  = full_size
        self.save()

    def jsondict(self):
        sd = None if self.start_date is None \
            else self.start_date.strftime("%m/%d/%Y")
        ed = None if self.end_date is None \
            else self.end_date.strftime("%m/%d/%Y")
        d = {"session_id" : self.session.id
           , "start_date" : sd
           , "end_date"   : ed
           , "repeats"    : self.repeats
           , "full_size"  : self.full_size
           , "intervals"  : self.intervals
             }
            
        #  Remove all None values
        for k, v in d.items():
            if v is None:
                _ = d.pop(k)

        return d

    def gen_windows(self):
        if self.start_date is not None and \
           self.repeats is not None and \
           self.intervals is not None and \
           self.full_size is not None:
            #  Delete all the previously generated windows
            for w in self.session.window_set.all():
                w.delete()
                
            intervals  = self.intervals.split(',')
            full_sizes = self.full_size.split(',')
            if len(intervals) == self.repeats and len(full_sizes) == self.repeats:
                for i in range(self.repeats):
                    interval = int(intervals[i]) - 1
                    size     = int(full_sizes[i])
                    w = Window(session = self.session, required = True)
                    w.save()
                    o = Opportunity(window = w
                                  , start_time = \
                                        self.start_date + timedelta(days = interval)
                                  , duration   = size * 24
                                    )
                    o.save()

            else:
                for i in range(self.repeats):
                    w = Window(session = self.session, required = True)
                    w.save()
                    o = Opportunity(window = w
                                  , start_time = \
                           self.start_date + timedelta(days = int(self.intervals)*i)
                                  , duration   = int(self.full_size) * 24
                                    )
                    o.save()

class Receiver_Group(models.Model):
    session        = models.ForeignKey(Sesshun)
    receivers      = models.ManyToManyField(
                                  Receiver
                                , db_table = "receiver_groups_receivers")

    class Meta:
        db_table = "receiver_groups"

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
    string_value   = models.CharField(null = True, max_length = 64)
    integer_value  = models.IntegerField(null = True)
    float_value    = models.FloatField(null = True)
    boolean_value  = models.BooleanField(null = True)
    datetime_value = models.DateTimeField(null = True)

    class Meta:
        db_table = "observing_parameters"
        unique_together = ("session", "parameter")

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

class Window(models.Model):
    session  = models.ForeignKey(Sesshun)
    required = models.BooleanField()

    def __unicode__(self):
        return "Window (%d) for Sess (%d), Num Opts: %d" % \
            (self.id
           , self.session.id
           , len(self.opportunity_set.all()))

    def num_opportunities(self):
        return len(self.opportunity_set.all())

    def init_from_post(self, fdata = QueryDict({})):
        self.required = fdata.get("required", False)
        self.save()
        start_time    = fdata.getlist("start_time")
        duration      = fdata.getlist("duration")
        for st, d in zip(start_time, duration):
            self.str2opportunity(st, d)

    def str2opportunity(self, start_time, duration):
        d, t      = start_time.split(' ')
        y, m, d   = map(int, d.split('-'))
        h, mm, ss = map(int, map(float, t.split(':')))
        st        = datetime(y, m, d, h, mm, ss)
        o = Opportunity(window = self
                      , start_time = st
                      , duration = float(duration))
        o.save()

    def update_from_post(self, fdata = QueryDict({})):
        for o in self.opportunity_set.all():
            o.delete()
        self.init_from_post(fdata)

    def is_classic(self):
        opt = first(self.opportunity_set.all())
        return len(self.opportunity_set.all()) == 1 and \
                 opt.duration > self.session.max_duration
        
    def jsondict(self, generate = False, now = None):
        now       = now or datetime.utcnow()
        windowed  = first(Session_Type.objects.filter(type = 'windowed'))
        receivers = [[r.abbreviation for r in rg.receivers.all()]
                    for rg in self.session.receiver_group_set.all()]
        d = {"id"       : self.id
           , "required" : self.required
           , "receiver" : receivers
            }
        if self.session.session_type == windowed and generate and self.is_classic():
            o = first(self.opportunity_set.all())
            d.update({"start_time" : str(o.start_time)
                    , "duration"   : o.duration
                     })
            opportunities = self.gen_opportunities(now)
        else:
            opportunities = self.opportunity_set.all()

        d.update({"opportunities" : [o.jsondict() for o in opportunities]})

        return d

    def gen_opportunities(self, now = None):
        w = first(self.opportunity_set.all())
        if w is None:
            return []

        now = now or datetime.utcnow()
        
        # Does the window already have one or more(!) sessions?
        # (Note if a session falls in the overlap of two
        # intersecting windows -- which should not be allowed
        # in any case -- then it satisfies both windows)
        # Note that the window start hour only applies to UTC windows,
        # the window itself starts at the beginning of the start date.
        #start = datetime(w.start_time.year, w.start_time.month, w.start_time.day)

        # TBF: Need to check to see if the window as already been satisfied.

        """
        limit = HourAngleLimit.query.filter(
            and_(
              HourAngleLimit.frequency ==
                               alloc.frequencyIndex(),
              HourAngleLimit.declination ==
                               alloc.declinationIndex()
                )).first()
        """
        limit = None
        ha_limit = int(limit.limit) if limit \
                   else int(round((
                            self.session.min_duration + 119) / 120))

        return OpportunityGenerator(now).generate(w, self.session, ha_limit)

    class Meta:
        db_table = "windows"

class Opportunity(models.Model):
    window     = models.ForeignKey(Window)
    start_time = models.DateTimeField()
    duration   = models.FloatField()

    def __unicode__(self):
        return "Opt (%d) for Win (%d): %s for %5.2f hrs" % (self.id
                                                          , self.window.id
                                                          , self.start_time
                                                          , self.duration)

    def jsondict(self):
        return {"id"         : self.id
              , "start_time" : str(self.start_time)
              , "duration"   : self.duration
                }
    
    def __repr__(self):
        return "%s - %s" % (self.start_time
                          , self.start_time + timedelta(hours = self.duration))

    def __str__(self):
        return "%s - %s" % (self.start_time
                          , self.start_time + timedelta(hours = self.duration))

    class Meta:
        db_table = "opportunities"

class System(models.Model):
    name   = models.CharField(max_length = 32)
    v_unit = models.CharField(max_length = 32)
    h_unit = models.CharField(max_length = 32)

    def __unicode__(self):
        return "%s (%s, %s)" % (self.name, self.v_unit, self.h_unit)

    class Meta:
        db_table = "systems"

class Target(models.Model):
    session    = models.ForeignKey(Sesshun)
    system     = models.ForeignKey(System)
    source     = models.CharField(null = True, max_length = 32)
    vertical   = models.FloatField()
    horizontal = models.FloatField()

    def __str__(self):
        return "%s at %s : %s" % (self.source
                                , self.vertical
                                , self.horizontal
                                  )

    def __unicode__(self):
        return "%s @ (%5.2f, %5.2f), Sys: %s" % \
            (self.source, self.vertical, self.horizontal, self.system)

    class Meta:
        db_table = "targets"

