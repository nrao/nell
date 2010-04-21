from datetime   import datetime
from django.db  import models

from tools        import TimeAccounting

#models
from common            import *
from Allotment         import Allotment
from Project_Type      import Project_Type
from Receiver_Schedule import Receiver_Schedule
from Semester          import Semester
from User              import User

class Project(models.Model):
    semester         = models.ForeignKey(Semester)
    project_type     = models.ForeignKey(Project_Type)
    allotments       = models.ManyToManyField(Allotment, through = "Project_Allotment")
    pcode            = models.CharField(max_length = 32)
    name             = models.CharField(max_length = 150)
    thesis           = models.BooleanField()
    complete         = models.BooleanField()
    start_date       = models.DateTimeField(null = True, blank = True)
    end_date         = models.DateTimeField(null = True, blank = True)
    friend           = models.ForeignKey(User, null = True, blank = True)
    accounting_notes = models.TextField(null = True, blank = True)
    notes            = models.TextField(null = True, blank = True)
    schedulers_notes = models.TextField(null = True, blank = True)

    base_url = "/sesshuns/project/"

    def __unicode__(self):
        return "%s, %s, %s" % (self.pcode, self.semester, self.name)

    def __str__(self):
        return self.pcode

    def is_science(self):
        return self.project_type.type == "science"

    def is_shutdown(self):
        return self.name == 'Shutdown'

    def is_maintenance(self):
        return any([s.observing_type.type == 'maintenance' \
                    for s in self.sesshun_set.all()])

    def is_test(self):
        return any([s.observing_type.type == 'testing' \
                    for s in self.sesshun_set.all()])

    def is_commissioning(self):
        return any([s.observing_type.type == 'commissioning' \
                    for s in self.sesshun_set.all()])

    def is_calibration(self):
        return any([s.observing_type.type == 'calibration' \
                    for s in self.sesshun_set.all()])

    @staticmethod
    def get_categories():
        "Return all possible categories of interest to Operations."
        return ["Un-assigned", "Astronomy", "Maintenance", "Shutdown"
              , "Tests", "Calibration", "Commissioning"]

    def get_category(self):
        "Categorize this project in a meaningful way for Operations."
        category = "Un-assigned"
        if self.is_science():
            category = "Astronomy"
        elif self.is_shutdown():
            category = "Shutdown"
        elif self.is_maintenance():
            category = "Maintenance"
        elif self.is_test():
            category = "Tests"
        elif self.is_commissioning():
            category = "Commissioning"
        elif self.is_calibration():
            category = "Calibration"

        return category

    def get_allotments_display(self):
        return self.allotments.all()

    def getObservedTime(self):
        return TimeAccounting().getTime("observed", self)

    def getTimeBilled(self):
        return TimeAccounting().getTime("time_billed", self)

    def getSumTotalTime(self):
        return TimeAccounting().getProjectTotalTime(self)

    def getTimeRemainingFromCompleted(self):
        return TimeAccounting().getTimeRemainingFromCompleted(self)

    def getTimeRemaining(self):
        return TimeAccounting().getTimeRemaining(self)

    def init_from_post(self, fdata):
        self.update_from_post(fdata)

    def update_from_post(self, fdata):
        fproj_type = fdata.get("type", "science")
        p_type     = first(Project_Type.objects.filter(type = fproj_type))
        fsemester  = fdata.get("semester", "09C")
        semester   = first(Semester.objects.filter(semester = fsemester))

        self.semester         = semester
        self.project_type     = p_type
        self.pcode            = fdata.get("pcode", "")
        self.name             = fdata.get("name", "")
        self.thesis           = fdata.get("thesis", "false") == "true"
        self.complete         = fdata.get("complete", "false") == "true"
        self.notes            = fdata.get("notes", "")
        self.schedulers_notes = fdata.get("schd_notes", "")

        self.save()

        totals   = map(float, fdata.get("total_time", "0.0").split(', '))
        pscs     = map(float, fdata.get("PSC_time", "0.0").split(', '))
        max_sems = map(float, fdata.get("sem_time", "0.0").split(', '))
        grades   = map(float, fdata.get("grade", "4.0").split(', '))
        
        assert len(totals) == len(pscs) and \
               len(totals) == len(max_sems) and \
               len(totals) == len(grades)

        num_new = len(totals)
        num_cur = len(self.allotments.all())
        if num_new > num_cur:
            for i in range(num_new - num_cur):
                a = Allotment(psc_time = 0.0
                            , total_time = 0.0
                            , max_semester_time = 0.0
                            , grade             = 0.0
                              )
                a.save()

                pa = Project_Allotment(project = self, allotment = a)
                pa.save()
        elif num_new < num_cur:
            for a in self.allotments.all()[:(num_cur - num_new)]:
                a.delete()
                
        allotment_data = zip(totals, pscs, max_sems, grades)
        for data, a in zip(allotment_data, self.allotments.all()):
            t, p, m, g = data
            a.total_time        = t
            a.psc_time          = p
            a.max_semester_time = m
            a.grade             = g
            a.save()
        
        self.save()

    def jsondict(self):
        totals   = ', '.join([str(a.total_time) for a in self.allotments.all()])
        pscs     = ', '.join([str(a.psc_time) for a in self.allotments.all()])
        max_sems = ', '.join([str(a.max_semester_time) for a in self.allotments.all()])
        grades   = ', '.join([str(a.grade) for a in self.allotments.all()])

        pi = '; '.join([i.user.name() for i in self.investigator_set.all()
                        if i.principal_investigator])
        co_i = '; '.join([i.user.name() for i in self.investigator_set.all()
                        if not i.principal_investigator])

        return {"id"           : self.id
              , "semester"     : self.semester.semester
              , "type"         : self.project_type.type
              , "total_time"   : totals
              , "PSC_time"     : pscs
              , "sem_time"     : max_sems
              , "remaining"    : self.getTimeRemaining()
              , "grade"        : grades
              , "pcode"        : self.pcode
              , "name"         : self.name
              , "thesis"       : self.thesis
              , "complete"     : self.complete
              , "pi"           : pi
              , "co_i"         : co_i
              , "notes"        : self.notes if self.notes is not None else ""
              , "schd_notes"   : self.schedulers_notes \
                                 if self.schedulers_notes is not None else ""
                }

    def principal_contact(self):
        "Who is the principal contact for this Project?"
        pc = None
        for inv in self.investigator_set.all():
            # if more then one, it's arbitrary
            if inv.principal_contact:
                pc = inv.user
        return pc        

    def principal_investigator(self):
        "Who is the principal investigator for this Project?"
        pc = None
        for inv in self.investigator_set.all():
            # if more then one, it's arbitrary
            if inv.principal_investigator:
                pc = inv.user
        return pc    

    def normalize_investigators(self):
        """
        Adjusts the priority field of all the project's investigators
        to a standard form in response to any possible change.
        """

        priority = 1
        for i in self.investigator_set.order_by('priority').all():
            if i.observer:
                i.priority = priority
                priority += 1
            else:
                i.priority = 999
            i.save()

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

    def getPeriods(self):
        "What are the periods associated with this project, vis. to observer?"
        return sorted([p for s in self.sesshun_set.all()
                         for p in s.period_set.all()
                         if p.state.abbreviation not in ['P','D']])

    def getUpcomingPeriods(self, dt = datetime.now()):
        "What periods are associated with this project in the future?"
        return [p for p in self.getPeriods() if p.start > dt] 


    def getPastPeriods(self, dt = datetime.now()):
        "What periods are associated with this project in the past?"
        return [p for p in self.getPeriods() if p.start <= dt] 

    def has_schedulable_sessions(self):
        sessions = [s for s in self.sesshun_set.all() if s.schedulable()]
        return True if sessions != [] else False

    def get_observers(self):
        return [i for i in self.investigator_set.order_by('priority').all() \
                if i.observer]

    def get_sanctioned_observers(self):
        return [i for i in self.investigator_set.order_by('priority').all() \
                if i.observer and i.user.sanctioned]

    def has_sanctioned_observers(self):
        return True if self.get_sanctioned_observers() != [] else False

    def transit(self):
        "Returns true if a single one of it's sessions has this flag true"
        sessions = [s for s in self.sesshun_set.all() if s.transit()]
        return True if sessions != [] else False

    def nighttime(self):
        "Returns true if a single one of it's sessions has this flag true"
        sessions = [s for s in self.sesshun_set.all() if s.nighttime()]
        return True if sessions != [] else False

    def anyNonOneXiSessions(self):
        "Returns true if a single session has a non 1.0 xi factor."
        sessions = [s for s in self.sesshun_set.all() if s.get_min_eff_tsys_factor() is not None and s.get_min_eff_tsys_factor() != 1.0]
        return sessions != []

    def anyCompleteSessions(self):
        "Returns true if a single session has been set as complete"
        sessions = [s for s in self.sesshun_set.all() if s.status.complete]
        return True if sessions != [] else False

    def get_prescheduled_days(self, start, end):
        """
        Returns a list of binary tuples of the form (start, end) that
        describe the whole days when this project cannot observe 
        because other projects already have scheduled telescope periods
        during the time range specified by the start and end arguments.
        """
        return range_to_days(self.get_prescheduled_times(start, end))

    def get_prescheduled_times(self, start, end):
        """
        Returns a list of binary tuples of the form (start, end) that
        describe when this project cannot observe because other 
        projects already have scheduled telescope periods during
        the time range specified by the start and end arguments.
        """
        times = [(d.start, d.start + timedelta(hours = d.duration)) \
                 for p in Project.objects.all() \
                 for d in p.getPeriods() \
                 if p != self and \
                    d.state.abbreviation == 'S' and \
                    overlaps((d.start, d.end()), (start, end))]
        return consolidate_events(times)

    def get_blackout_dates(self, start, end):
        """
        A project is 'blacked out' when all of its sanctioned observers
        are unavailable.  Returns a list of tuples describing the whole days
        where the project is 'blacked out' in UTC.
        """
        return range_to_days(self.get_blackout_times(start, end))

    def get_blackout_times(self, start, end):
        """
        A project is 'blacked out' when all of its sanctioned observers
        are unavailable.  Returns a list of tuples describing the time ranges
        where the project is 'blacked out' in UTC.
        """
        if not self.has_sanctioned_observers():
            return []

        blackouts = [o.user.blackout_set.all() \
                     for o in self.get_sanctioned_observers()]

        # Change all to UTC.
        utcBlackouts = []
        for set in blackouts:
            utc = []
            for b in set:
                utc.extend(b.generateDates(start, end))
            utcBlackouts.append(utc)

        if len(utcBlackouts) == 1: # One observer runs the show.
            return sorted(utcBlackouts[0])

        return consolidate_events(find_intersections(utcBlackouts))

    def get_receiver_blackout_ranges(self, start, end):
        """
        Returns a list of tuples of the form (start, end) where
        start and end are datetime objects that denote the 
        beginning and ending of a period where no receivers are available
        for any session in a project.  If there is a receiver available
        at all times for any session, an empty list is returned.  If there
        are no session for a project, an empty list is returned.
        """

        # Find all the required receiver sets for this project and schedule.
        # E.g. for one session:
        #     [[a, b, c], [x, y, z]] = (a OR b OR c) AND (x OR y OR z)
        required = [s.receiver_group_set.all() for s in self.sesshun_set.all()]
        if required == []:
            return [] # No sessions, no problem

        schedule = Receiver_Schedule.extract_schedule(start, (end - start).days)

        if schedule == {}: # No receiver schedule present!
            return [(start, None)]

        # Go through the schedule and determine blackout ranges.
        ranges = []
        for date, receivers in sorted(schedule.items()):
            receivers = Set(receivers)
            if not any([all([Set(g.receivers.all()).intersection(receivers) \
                        for g in set]) for set in required]):
                # No session has receivers available. Begin drought.
                if not ranges or ranges[-1][1] is not None:
                    ranges.append((date, None))
            else:
                # A session has receivers available. End drought, if present.
                if ranges and ranges[-1][1] is None:
                    start, _ = ranges.pop(-1)
                    ranges.append((start, date))
        return ranges

    def get_receiver_blackout_dates(self, start, end):
        # Change date ranges into individual days.
        blackouts = []
        for rstart, rend in self.get_receiver_blackout_ranges(start, end):
            counter = rstart.replace(hour = 0)
            while counter < (rend or end):
                blackouts.append(counter)
                counter = counter + timedelta(days = 1)
 
        return blackouts

    def get_observed_periods(self, dt = datetime.now()):
        "What periods have been observed on this project?"
        return self.getPastPeriods(dt)

    def get_allotment(self, grade):
        "Returns the allotment that matches the specified grade"
        # TBF watch out - this is a float!
        epsilon = 1e-3
        for a in self.allotments.all():
            diff = abs(a.grade - grade)
            if diff < epsilon:
                return a
        return None # uh-oh

    def get_windows(self):
        # TBF no filtering here, ALL windows!
        return sorted([w for s in self.sesshun_set.all()
                         for w in s.window_set.all()
                         if s.session_type.type == 'windowed']
                     , key = lambda x : x.start_date)

    def get_active_windows(self):
        "Returns current and future windows."
        wins = self.get_windows()
        now = datetime.utcnow()
        today = date(now.year, now.month, now.day)
        return [ w for w in wins
                 if today < (w.start_date + timedelta(days = w.duration)) ]

    class Meta:
        db_table  = "projects"
        app_label = "sesshuns"

class Project_Allotment(models.Model):
    project = models.ForeignKey(Project)
    allotment = models.ForeignKey(Allotment)

    class Meta:
        db_table  = "projects_allotments"
        app_label = "sesshuns"

