from datetime                  import datetime, timedelta
from math                      import asin, acos, cos, sin
from django.db                 import models
from django.http               import QueryDict
from utilities.receiver        import ReceiverCompile

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
        return "(%d) Total: %5.2f, Grade: %5.2f, PSC: %5.2f, Max: %5.2f" % \
                                       (self.id
                                      , self.total_time
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
        return "%s, %s, %s" % (self.pcode, self.semester, self.name)

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

    def principal_investigator(self):
        "Who is the principal investigator for this Project?"
        pc = None
        for inv in self.investigators_set.all():
            # if more then one, it's arbitrary
            if inv.principal_investigator:
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

# TBF: recurrences don't apply for 09B, but we'll need to do these latter
class Blackout(models.Model):
    user         = models.ForeignKey(User)
    #recurrence  = models.ForeignKey(Recurrence)
    start        = models.DateTimeField(null = True)
    end          = models.DateTimeField(null = True)
    description  = models.CharField(null = True, max_length = 512)

    def __unicode__(self):
        return "Blackout for %s: %s - %s" % (self.user, self.start, self.end)

    class Meta:
        db_table = "blackouts"

# TBF: temporary table/class for scheduling just 09B.  We can safely
# dispose of this after 09B is complete.  Delete Me!
class Project_Blackout_09B(models.Model):
    project      = models.ForeignKey(Project)
    requester    = models.ForeignKey(User)
    start_date   = models.DateTimeField(null = True)
    end_date     = models.DateTimeField(null = True)
    description  = models.CharField(null = True, max_length = 512)

    def __unicode__(self):
        return "Blackout for %s: %s - %s" % (self.project.pcode, self.start_date, self.end_date)

    class Meta:
        # Note: using upper case B at the end of this name causes 
        # problems with postrgreSQL
        db_table = "project_blackouts_09b"

class Investigators(models.Model):
    project                = models.ForeignKey(Project)
    user                   = models.ForeignKey(User)
    friend                 = models.BooleanField(default = False)
    observer               = models.BooleanField(default = False)
    principal_contact      = models.BooleanField(default = False)
    principal_investigator = models.BooleanField(default = False)
    priority               = models.IntegerField(default = 1)

    def __unicode__(self):
        return "%s (%d) for %s; fr : %s, obs : %s, PC : %s, PI : %s" % \
            ( self.user
            , self.user.id
            , self.project.pcode
            , self.friend
            , self.observer
            , self.principal_contact
            , self.principal_investigator )

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

    def jsondict(self):
        return self.abbreviation

    @staticmethod
    def get_abbreviations():
        return [r.abbreviation for r in Receiver.objects.all()]

class Receiver_Schedule(models.Model):
    receiver   = models.ForeignKey(Receiver)
    start_date = models.DateTimeField(null = True)

    def __unicode__(self):
        return "%s on %s" % \
          ( self.receiver.name
          , self.start_date)

    class Meta:
        db_table = "receiver_schedule"

    @staticmethod
    def jsondict(schedule):
        jschedule = {}
        for d in schedule:
            jd = None if d is None else d.strftime("%m/%d/%Y")
            jschedule[jd] = [r.jsondict() for r in schedule[d]]
        return jschedule

    @staticmethod
    def extract_schedule(startdate = None, days=None):
        startdate = startdate or datetime.utcnow()
        startdate = Receiver_Schedule.previousDate(startdate)
        days = days or 120
        enddate   = startdate + timedelta(days=days)
        schedule = dict()
        for dt_rcvr in [dt_rcvr
                        for dt_rcvr in Receiver_Schedule.objects.filter(
                                              start_date__gte = startdate
                                                     ).filter(
                                              start_date__lte = enddate)]:
            schedule.setdefault(dt_rcvr.start_date, []).append(dt_rcvr.receiver)
        return schedule

    @staticmethod
    def previousDate(date):
        prev = date
        try:
            prev = Receiver_Schedule.objects.filter(start_date__lte = date).order_by('-start_date')[0].start_date
        except IndexError:
            pass
        return prev

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
        return "(%d) e: %s; a: %s; c: %s; b: %s" % \
            (self.id, self.enabled, self.authorized, self.complete, self.backup)

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

    restrictions = "Unrestricted" # TBF Do we still need restrictions?

    def __unicode__(self):
        return "(%d) %s : %5.2f GHz, %5.2f Hrs, Rcvrs: %s" % (
                  self.id
                , self.name if self.name is not None else ""
                , self.frequency if self.frequency is not None else 0
                , self.allotment.total_time
                      if self.allotment.total_time is not None else 0
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
        proj_code = fdata.get("pcode", "GBT09A-001")

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
            rg = Receiver_Group(session = self)
            rg.save()
            for rcvr in ors:
                rcvrId = Receiver.objects.filter(abbreviation = rcvr)[0]
                rg.receivers.add(rcvrId)
                rg.save()

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

        v_axis = fdata.get("source_v", None)
        h_axis = fdata.get("source_h", None)

        t            = self.target_set.get()
        t.system     = system
        t.source     = fdata.get("source", None)
        t.vertical   = v_axis if v_axis is not None else t.vertical
        t.horizontal = h_axis if h_axis is not None else t.horizontal
        t.save()

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

        #  Remove all None values
        for k, v in d.items():
            if v is None:
                _ = d.pop(k)

        return d

    class Meta:
        db_table = "sessions"

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
    vertical   = models.FloatField(null = True)
    horizontal = models.FloatField(null = True)

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

class Period(models.Model):
    session    = models.ForeignKey(Sesshun)
    start      = models.DateTimeField()
    duration   = models.FloatField()
    score      = models.FloatField(null = True)
    forecast   = models.DateTimeField(null = True)
    backup     = models.BooleanField()

    def __unicode__(self):
        return "Period for Session (%d): %s for %5.2f Hrs" % \
            (self.session.id, self.start, self.duration)

    class Meta:
        db_table = "periods"
    

