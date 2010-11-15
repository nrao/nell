from datetime   import datetime
from django.db  import models

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
    blackouts        = models.BooleanField(default = False)
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


    def getActiveElectives(self, dt = datetime.now()):
        """
        Retrieves sessions' electives that are either incomplete,
        or still have a period in the future.
        """
        
        es = []
        for s in self.sesshun_set.all():
            if s.session_type.type == "elective":
                for e in s.elective_set.all():
                    if not e.complete or e.hasPeriodsAfter(dt):
                        es.append(e)
        return es                
                
    def hasActiveElectives(self, dt = datetime.now()):
        return len(self.getActiveElectives(dt)) > 0

    def getPastPeriods(self, dt = datetime.now()):
        "What periods are associated with this project in the past?"
        return [p for p in self.getPeriods() if p.start <= dt] 

    def has_schedulable_sessions(self):
        sessions = [s for s in self.sesshun_set.all() if s.schedulable()]
        return True if sessions != [] else False

    def isInvestigator(self, user):
        return user.id in [i.user.id for i in self.investigator_set.all()]

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

    def anyElevationLimits(self):
        "Returns true if a single session has the El Limit obs param set."
        sessions = [s for s in self.sesshun_set.all() if s.get_elevation_limit() is not None]
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
        are unavailable or it is using Project Blackouts.
        Returns a list of tuples describing the time ranges
        where the project is 'blacked out' in UTC.
        """
        user_blackouts = self.get_user_blackout_times(start, end)
        project_blackouts = self.get_project_blackout_times(start, end) 

        if len(project_blackouts) < 1:
            return user_blackouts
        else:    
            user_blackouts.extend(sorted(project_blackouts))
            return consolidate_events(user_blackouts)

    def get_project_blackout_times(self, start, end):
        """
        A project is 'blacked out' when all of its sanctioned observers
        are unavailable or it is using Project Blackouts.
        Returns a list of tuples describing the time ranges
        where the project is 'blacked out' by project blackouts in UTC.
        """
        # we need to 'flatten' out the blackouts so that they can
        # be combined with user blackouts later
        project_blackouts = []
        for b in self.blackout_set.all():
            project_blackouts.extend(b.generateDates(start, end))
        return project_blackouts

    def get_user_blackout_times(self, start, end):
        """
        A project is 'blacked out' when all of its sanctioned observers
        are unavailable or it is using Project Blackouts.
        User blackouts are much more complicated, thus this method.
        Returns a list of tuples describing the time ranges
        where the project is 'blacked out' by user blackouts in UTC.
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

