from django.db import models

def first(results, default = None):
    return default if len(results) == 0 else results[0]

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

class Sesshun(models.Model):
    
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

    def delete(self):
        self.allotment.delete()
        super(Sesshun, self).delete()
        
    def init_from_json(self, fdata):
        fsestype = fdata.get("type", "open")
        fobstype = fdata.get("science", "testing")
        frcvr    = fdata.get("receiver", "Rcvr1_2")

        p  = first(Project.objects.filter(pcode = "GBT09A-001").all())
        st = first(Session_Type.objects.filter(type = fsestype).all()
                 , Session_Type.objects.all()[0])
        ot = first(Observing_Type.objects.filter(type = fobstype).all()
                 , Observing_Type.objects.all()[0])
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

        rcvr   = first(Receiver.objects.filter(name = frcvr).all()
                     , Receiver.objects.all()[0])
        rg     = Receiver_Group(session = self)
        rg.save()
        rg.receiver_group_receiver_set.add(rcvr)
        rg.save()
        
        status = Status(session    = self
                      , enabled    = fdata.get("enabled", True)
                      , authorized = fdata.get("authorized", True)
                      , complete   = fdata.get("complete", True)
                      , backup     = fdata.get("backup", True)
                        )
        status.save()

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

    def update_from_json(self, fdata):
        fsestype = fdata.get("type", "open")
        fobstype = fdata.get("science", "testing")
        frcvr    = fdata.get("receiver", "Rcvr1_2")

        p  = first(Project.objects.filter(pcode = "GBT09A-001").all())
        st = first(Session_Type.objects.filter(type = fsestype).all()
                 , Session_Type.objects.all()[0])
        ot = first(Observing_Type.objects.filter(type = fobstype).all()
                 , Observing_Type.objects.all()[0])

        self.allotment.psc_time          = fdata.get("PSC_time", 0.0)
        self.allotment.total_time        = fdata.get("total_time", 0.0)
        self.allotment.max_semester_time = fdata.get("sem_time", 0.0)

        self.project          = p
        self.session_type     = st
        self.observing_type   = ot
        self.original_id      = fdata.get("orig_ID", None)
        self.name             = fdata.get("name", None)
        self.frequency        = fdata.get("freq", None)
        self.max_duration     = fdata.get("req_max", None)
        self.min_duration     = fdata.get("req_min", None)
        self.time_between     = fdata.get("between", None)
        self.grade            = fdata.get("grade", None)

        # TBF DO SOMETHING WITH RECEIVERS!

        self.status_set.get().enabled    = fdata.get("enabled", True)
        self.status_set.get().authorized = fdata.get("authorized", True)
        self.status_set.get().complete   = fdata.get("complete", True)
        self.status_set.get().backup     = fdata.get("backup", True)

        system = first(System.objects.filter(name = "J2000").all()
                     , System.objects.all()[0])

        v_axis = fdata.get("v_axis", 2.0) #TBF
        h_axis = fdata.get("h_axis", 2.0) #TBF

        self.target_set.get().system     = system
        self.target_set.get().source     = fdata.get("source", None)
        self.target_set.get().vertical   = v_axis
        self.target_set.get().horizontal = h_axis

        self.save()

    def get_receiver_req(self):
        return first(self.receiver_group_set.get().receivers.all())
        
    def jsondict(self):
        status = first(self.status_set.all())
        target = first(self.target_set.all())
        rcvr   = self.get_receiver_req()

        d = {"id"         : self.id
           , "proj_code"  : self.project.pcode
           , "type"       : self.session_type.type
           , "science"    : self.observing_type.type
           , "total_time" : self.allotment.total_time
           , "PSC_time"   : self.allotment.psc_time
           , "sem_time"   : self.allotment.max_semester_time
           , "orig_ID"    : self.original_id
           , "name"       : self.name
           , "freq"       : self.frequency
           , "req_max"    : self.max_duration
           , "req_min"    : self.min_duration
           , "between"    : self.time_between
           , "grade"      : self.grade
             }

        if rcvr is not None:
            d.update({"receiver"   : rcvr.abbreviation})
            
        if status is not None:
            s_d = {"enabled"    : status.enabled
                 , "authorized" : status.authorized
                 , "complete"   : status.complete
                 , "backup"     : status.backup
                   }
            # TBF turning all data to strings for GWT code
            """
            for k, v in s_d.items():
                s_d[k] = str(v).lower()
                
            d.update(s_d)
            """

        if target is not None:
            d.update({"source" : target.source})

        #  Remove all None values
        for k, v in d.items():
            if v is None:
                _ = d.pop(k)

        # TBF turning all data to strings for GWT code
        """
        for k, v in d.items():
            if k != "id":
                d[k] = str(v)

        """
        return d

    class Meta:
        db_table = "sessions"

class Receiver_Group(models.Model):
    session        = models.ForeignKey(Sesshun)
    receivers      = models.ManyToManyField(Receiver
                                          , through = "Receiver_Group_Receiver")

    class Meta:
        db_table = "receiver_groups"

class Receiver_Group_Receiver(models.Model):
    group          = models.ForeignKey(Receiver_Group)
    receiver       = models.ForeignKey(Receiver)

    class Meta:
        db_table = "receiver_groups_receiver"

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

class Status(models.Model):
    session    = models.ForeignKey(Sesshun)
    enabled    = models.BooleanField()
    authorized = models.BooleanField()
    complete   = models.BooleanField()
    backup     = models.BooleanField()

    class Meta:
        db_table = "status"

class Window(models.Model):
    session  = models.ForeignKey(Sesshun)
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
    session    = models.ForeignKey(Sesshun)
    system     = models.ForeignKey(System)
    source     = models.CharField(null = True, max_length = 32)
    vertical   = models.FloatField()
    horizontal = models.FloatField()

    class Meta:
        db_table = "targets"

