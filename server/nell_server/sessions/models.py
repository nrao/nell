from django.db import models

class Semester(models.Model):
    semester = models.CharField(max_length = 64)

    class Meta:
        db_table = "semesters"

class Project_Type(models.Model):
    type = models.CharField(max_length = 64)

    class Meta:
        db_table = "project_types"

class Allotment(models.Model):
    psc_time          = models.FloatField()
    total_time        = models.FloatField()
    max_semester_time = models.FloatField()

    class Meta:
        db_table = "allotment"

class Project(models.Model):
    semester     = models.ForeignKey(Semester)
    project_type = models.ForeignKey(Project_Type)
    allotment    = models.ForeignKey(Allotment)
    pcode        = models.CharField(max_length = 32)
    name         = models.CharField(max_length = 60)
    thesis       = models.BooleanField()
    complete     = models.BooleanField()
    ignore_grade = models.BooleanField()
    start_date   = models.DateTimeField(null = True)
    end_date     = models.DateTimeField(null = True)

    class Meta:
        db_table = "projects"

class Session_Type(models.Model):
    type = models.CharField(max_length = 64)

    class Meta:
        db_table = "session_types"

class Observing_Type(models.Model):
    type = models.CharField(max_length = 64)

    class Meta:
        db_table = "observing_types"

class Receiver(models.Model):
    name         = models.CharField(max_length = 32)
    abbreviation = models.CharField(max_length = 32)
    freq_low     = models.FloatField()
    freq_hi      = models.FloatField()

    class Meta:
        db_table = "receivers"

class Parameter(models.Model):
    name = models.CharField(max_length = 64)
    type = models.CharField(max_length = 32)

    class Meta:
        db_table = "parameters"

class Sessions(models.Model):
    """
    Sessions hold meta data used to create a period.

    # Create some sessions
    >>> s    = Sessions.objects.create()
    >>> data = {}
    >>> s.init_from_json(data)
    """
    
    project            = models.ForeignKey(Project)
    session_type       = models.ForeignKey(Session_Type)
    observing_type     = models.ForeignKey(Observing_Type)
    allotment          = models.ForeignKey(Allotment)
    original_id        = models.IntegerField(null = True)
    name               = models.CharField(null = True
                                        , max_length = 64)
    frequency          = models.FloatField(null = True)
    max_duration       = models.FloatField(null = True)
    min_duration       = models.FloatField(null = True)
    time_between       = models.FloatField(null = True)
    grade              = models.FloatField(null = True)

    def init_from_json(self, fdata):
        fsestype = fdata.get("type", "open")
        fobstype = fdata.get("science", "testing")
        frcvr    = fdata.get("receiver", "Rcvr1_2")

        p  = Project.objects.filter(pcode = "GBT09A-001").all()[0]
        st = Session_Type.objects.filter(type = fsestype).all()[0]
        ot = Observing_Type.objects.filter(type = fobstype).all()[0]
        allot = Allotment(psc_time          = fdata.get("PSC_time", 0.0)
                        , total_time        = fdata.get("total_time", 0.0)
                        , max_semester_time = fdata.get("sem_time", 0.0)
                          )
        allot.save()

        self.project          = p
        self.session_type     = st
        self.observing_type   = ot
        self.allotment        = allot
        self.original_id      = fdata.get("orig_ID", None)
        self.name             = fdata.get("name", None)
        self.frequency        = fdata.get("freq", None)
        self.max_duration     = fdata.get("req_max", None)
        self.min_duration     = fdata.get("req_min", None)
        self.time_between     = fdata.get("between", None)
        self.grade            = fdata.get("grade", None)

        self.save()
        
        rcvr   = Receiver.objects.filter(name = frcvr).all()[0]
        rg     = Receiver_Group(session = self)
        rg.save()
        rg.receivers.add(rcvr)
        rg.save()
        
        status = Status(session    = self
                      , enabled    = fdata.get("enabled", True)
                      , authorized = fdata.get("authorized", True)
                      , complete   = fdata.get("complete", True)
                      , backup     = fdata.get("backup", True)
                        )
        status.save()

        system = System.objects.filter(name = "J2000").all()[0]

        v_axis = fdata.get("v_axis", 2.0) #TBF
        h_axis = fdata.get("h_axis", 2.0) #TBF
        
        target = Target(session    = self
                      , system     = system
                      , source     = fdata.get("source", None)
                      , vertical   = v_axis
                      , horizontal = h_axis
                        )
        target.save()

    def get_receiver_req(self):
        return self.receiver_group_set.get().receivers.all()[0]
        
    def jsondict(self):
        status = self.status_set.all()[0]
        rcvr   = self.get_receiver_req()
        
        target = self.target_set.all()[0]
        d = {"id"         : self.id
           , "proj_code"  : self.project.pcode
           , "type"       : self.session_type.type
           , "science"    : self.observing_type.type
           , "total_time" : self.allotment.total_time
           , "PSC_time"   : self.allotment.psc_time
           , "sem_time"   : self.allotment.max_semester_time
           , "receiver"   : rcvr.abbreviation
           , "orig_ID"    : self.original_id
           , "name"       : self.name
           , "freq"       : self.frequency
           , "req_max"    : self.max_duration
           , "req_min"    : self.min_duration
           , "between"    : self.time_between
           , "grade"      : self.grade
           , "enabled"    : status.enabled
           , "authorized" : status.authorized
           , "complete"   : status.complete
           , "backup"     : status.backup
           , "source"     : target.source
             }
        
        return d

    class Meta:
        db_table = "sessions"

class Receiver_Group(models.Model):
    session        = models.ForeignKey(Sessions)
    receivers      = models.ManyToManyField(Receiver
                                          , db_table = "receiver_groups_receivers")

    class Meta:
        db_table = "receiver_groups"

class Observing_Parameter(models.Model):
    session        = models.ForeignKey(Sessions)
    parameter      = models.ForeignKey(Parameter)
    string_value   = models.CharField(null = True, max_length = 64)
    integer_value  = models.IntegerField(null = True)
    float_value    = models.FloatField(null = True)
    boolean_value  = models.BooleanField(null = True)
    datetime_value = models.DateTimeField(null = True)

    class Meta:
        db_table = "observing_parameters"
        unique_together = ("session", "parameter")

class Status(models.Model):
    session    = models.ForeignKey(Sessions)
    enabled    = models.BooleanField()
    authorized = models.BooleanField()
    complete   = models.BooleanField()
    backup     = models.BooleanField()

    class Meta:
        db_table = "status"

class Window(models.Model):
    session  = models.ForeignKey(Sessions)
    required = models.BooleanField()

    class Meta:
        db_table = "windows"

class Opportunity(models.Model):
    window     = models.ForeignKey(Window)
    start_time = models.DateTimeField()
    duration   = models.FloatField()

    class Meta:
        db_table = "opportunities"

class System(models.Model):
    name   = models.CharField(max_length = 32)
    v_unit = models.CharField(max_length = 32)
    h_unit = models.CharField(max_length = 32)

    class Meta:
        db_table = "systems"

class Target(models.Model):
    session    = models.ForeignKey(Sessions)
    system     = models.ForeignKey(System)
    source     = models.CharField(null = True, max_length = 32)
    vertical   = models.FloatField()
    horizontal = models.FloatField()

    class Meta:
        db_table = "targets"

