from datetime                  import datetime, timedelta
from math                      import asin, acos, cos, sin
from tools                     import TimeAccounting
from django.conf               import settings
from django.db                 import models
from django.http               import QueryDict
from settings                  import ANTIOCH_SERVER_URL
from utilities.receiver        import ReceiverCompile
from utilities                 import TimeAgent, UserInfo, NRAOBosDB

import calendar
import pg
from sets                      import Set
import urllib2
import simplejson as json
import sys

def first(results, default = None):
    return default if len(results) == 0 else results[0]

def str2dt(str):
    "'YYYY-MM-DD hh:mm:ss' to datetime object"
    if str is None:
        return None

    if ' ' in str:
        dstr, tstr = str.split(' ')
        y, m, d    = map(int, dstr.split('-'))
        time       = tstr.split(':')
        h, mm, ss  = map(int, map(float, time))
        return datetime(y, m, d, h, mm, ss)

    y, m, d   = map(int, str.split('-'))
    return datetime(y, m, d)

def strStr2dt(dstr, tstr):
    return str2dt(dstr + ' ' + tstr) if tstr else str2dt(dstr)
        
def dt2str(dt):
    "datetime object to YYYY-MM-DD hh:mm:ss string"
    if dt is None:
        return None
    else:    
        return dt.strftime("%Y-%m-%d %H:%M:%S")

def d2str(dt):
    "datetime object to YYYY-MM-DD string"
    if dt is None:
        return None
    else:    
        return dt.strftime("%Y-%m-%d")

def t2str(dt):
    "datetime object to hh:mm string"
    if dt is None:
        return None
    else:    
        return dt.strftime("%H:%M")

def grade_abc_2_float(abc):
    grades = {'A' : 4.0, 'B' : 3.0, 'C' : 2.0}
    return grades.get(abc, None)

def grade_float_2_abc(grade):
    grades = ['A', 'B', 'C']
    floats = [4.0, 3.0, 2.0]
    gradeLetter = 'C'
    for i in range(len(grades)):
        if grade >= (floats[i] - 10e-5):
            gradeLetter = grades[i]
            break
    return gradeLetter

def range_to_days(ranges):
    dates = []
    for rstart, rend in ranges:
        if rend - rstart > timedelta(days = 1):
            start = rstart
            end   = rstart.replace(hour = 0, minute = 0, second = 0) + timedelta(days = 1)
            while start < rend:
                if end - start >= timedelta(days = 1):
                    dates.append(start)
                start = end
                end   = end + timedelta(days = 1)
    return dates

def overlaps(dt1, dt2):
    start1, end1 = dt1
    start2, end2 = dt2

    if start1 < end2 and start2 < end1:
        return True
    else:
        return False

def find_intersections(events):
    """
    Takes a list of lists of datetime tuples of the form (start, end) 
    representing sets of events, finds the intersections of all the
    sets, and returns a list of datetime tuples of the form (start, end)
    describing the intersections.  All datetime tuples are assumed to be 
    in the same timezone.
    """
    start = 0; end = 1
    intersections = []
    for b in events[0]:
        for set in events[1:]:
            if any([overlaps(b, s) for s in set]):
                intersections.extend(
                    [(max([b[start], s[start]]), min([b[end], s[end]])) \
                     for s in set if overlaps(b, s)])
            else:
                return [] # No intersections for all sets.

    return intersections

def consolidate_events(events):
    """
    Takes a list of datetime tuples of the form (start, end) and
    reduces it to the smallest list that fully describes the events.
    All datetime tuples are assumed to be in the same timezone.
    """
    if len(events) == 1:
        return events
    else:
        return combine_events(consolidate_overlaps(events))

def consolidate_overlaps(events):
    reduced = []
    for (begin1, end1) in events:
        begin = begin1
        end   = end1
        for (begin2, end2) in events:
            if (begin1, end1) != (begin2, end2) and \
               begin1 < end2 and begin2 < end1:
                begin = max([begin, begin1, begin2])
                end   = min([end, end1, end2])
        if (begin, end) not in reduced:
            reduced.append((begin, end))            
    return reduced

def combine_events(events):
    if len(events) in (0, 1):
        return events 

    events = sorted(events)
    combined = [events[0]]
    for (begin2, end2) in events[1:]:
        begin1, end1 = combined[-1]
        if begin2 == end1:
            combined[-1] = (begin1, end2)
        else:
            combined.append((begin2, end2))
    return combined

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
         , "receiver"       : "receiver_group__receivers__abbreviation"
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

class Role(models.Model):
    role = models.CharField(max_length = 32)

    class Meta:
        db_table = "roles"

class User(models.Model):
    original_id = models.IntegerField(null = True)
    pst_id      = models.IntegerField(null = True)
    username    = models.CharField(max_length = 32, null = True)
    sanctioned  = models.BooleanField(default = False)
    first_name  = models.CharField(max_length = 32)
    last_name   = models.CharField(max_length = 150)
    contact_instructions = models.TextField(null = True)
    role                 = models.ForeignKey(Role)

    class Meta:
        db_table = "users"

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def name(self):
        return self.__str__()

    def isAdmin(self):
        return self.role.role == "Administrator"

    def isOperator(self):
        return self.role.role == "Operator"

    def getStaticContactInfo(self):
        return UserInfo().getProfileByID(self)

    def getReservations(self):
        return NRAOBosDB().getReservationsByUsername(self.username)

    def getPeriods(self):
        retval = []
        for i in self.investigator_set.all():
            retval.extend(i.project.getPeriods())
        return sorted(list(Set(retval)))

    def getPeriodsByProject(self):
        """
        Returns a dictionary of project: [periods] associated with this
        user sorted by start date.
        """
        retval = {}
        for i in self.investigator_set.all():
            retval[i.project] = i.project.getPeriods()
        return retval

    def getUpcomingPeriods(self, dt = datetime.now()):
        "What periods might this observer have to observe soon?"
        return [p for p in self.getPeriods() if p.start >= dt]

    def getUpcomingPeriodsByProject(self, dt = datetime.now()):
        "What periods might this observer have to observe soon?"
        retval = {}
        for project, period in self.getPeriodsByProject().items():
            retval[project] = [p for p in period if p.start >= dt]
        return retval

    def getObservedPeriods(self, dt = datetime.now()):
        "What periods associated w/ this observer have been observed?"
        return [p for p in self.getPeriods() if p.start < dt]

    def getObservedPeriodsByProject(self, dt = datetime.now()):
        "What periods associated w/ this observer have been observed?"
        retval = {}
        for project, period in self.getPeriodsByProject().items():
            retval[project] = [p for p in period if p.start < dt]
        return retval

class Email(models.Model):
    user  = models.ForeignKey(User)
    email = models.CharField(max_length = 255)

    class Meta:
        db_table = "emails"

class Semester(models.Model):
    semester = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.semester

    def start(self):
        # A starts in February, B in June, C in October
        start_months = {"A": 2, "B": 6, "C": 10}

        year  = 2000 + int(self.semester[:2])
        month = start_months[self.semester[-1]]

        return datetime(year, month, 1)

    def end(self):
        # A ends in May, B in September, C in January
        end_months = {"A": 5, "B": 9, "C": 1}

        year   = 2000 + int(self.semester[:2])
        month  = end_months[self.semester[-1]]
        _, day = calendar.monthrange(year, month)

        return datetime(year, month, day)

    def eventjson(self, id):
        return {
            "id"   : id
          , "title": "".join(["Start of ", self.semester])
          , "start": self.start().isoformat()
        }

    @staticmethod
    def getFutureSemesters(date):
        "Returns a list of Semesters that start on or before the given date."
        return [s for s in Semester.objects.all() if s.start() >= date]

    class Meta:
        db_table = "semesters"

class Project_Type(models.Model):
    type = models.CharField(max_length = 64)

    def __unicode__(self):
        return self.type

    class Meta:
        db_table = "project_types"

class Allotment(models.Model):
    psc_time          = models.FloatField(help_text = "Hours")
    total_time        = models.FloatField(help_text = "Hours")
    max_semester_time = models.FloatField(help_text = "Hours")
    grade             = models.FloatField(help_text = "0.0 - 4.0")
    ignore_grade      = models.NullBooleanField(null = True, default = False)

    base_url = "/sesshuns/allotment/"

    def __unicode__(self):
        return "(%d) Total: %5.2f, Grade: %5.2f, PSC: %5.2f, Max: %5.2f" % \
                                       (self.id
                                      , self.total_time
                                      , self.grade
                                      , self.psc_time
                                      , self.max_semester_time) 

    def get_absolute_url(self):
        return "/sesshuns/allotment/%i/" % self.id

    class Meta:
        db_table = "allotment"
        
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
    accounting_notes = models.CharField(null = True, max_length = 1024)

    base_url = "/sesshuns/project/"

    def __unicode__(self):
        return "%s, %s, %s" % (self.pcode, self.semester, self.name)

    def __str__(self):
        return self.pcode

    def is_maintenance(self):
        return self.name == 'Maintenance' 

    def get_allotments_display(self):
        return self.allotments.all()

    def init_from_post(self, fdata):
        self.update_from_post(fdata)

    def update_from_post(self, fdata):
        fproj_type = fdata.get("type", "science")
        p_type     = first(Project_Type.objects.filter(type = fproj_type))
        fsemester  = fdata.get("semester", "09C")
        semester   = first(Semester.objects.filter(semester = fsemester))

        self.semester     = semester
        self.project_type = p_type
        self.pcode        = fdata.get("pcode", "")
        self.name         = fdata.get("name", "")
        self.thesis       = fdata.get("thesis", "false") == "true"
        self.complete     = fdata.get("complete", "false") == "true"

        self.save()

        totals   = map(float, fdata.get("total_time", "0.0").split(', '))
        pscs     = map(float, fdata.get("PSC_time", "0.0").split(', '))
        max_sems = map(float, fdata.get("sem_time", "0.0").split(', '))
        grades   = map(grade_abc_2_float, fdata.get("grade", "A").split(', '))
        
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
        grades   = ', '.join([grade_float_2_abc(a.grade) for a in self.allotments.all()])

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
              , "grade"        : grades
              , "pcode"        : self.pcode
              , "name"         : self.name
              , "thesis"       : self.thesis
              , "complete"     : self.complete
              , "pi"           : pi
              , "co_i"         : co_i
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
        "What are the periods associated with this project?"
        return sorted([p for s in self.sesshun_set.all()
                         for p in s.period_set.all()])

    def getUpcomingPeriods(self, dt = datetime.now()):
        "What periods are associated with this project in the future?"
        return [p for p in self.getPeriods() if p.start > dt] 


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
                 if p != self and d.start >= start and d.start <= end]
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
        # WWHD?
        return [p for s in self.sesshun_set.all() \
                    for p in s.period_set.all() \
                        if p.start < dt]

    class Meta:
        db_table = "projects"

class Project_Allotment(models.Model):
    project = models.ForeignKey(Project)
    allotment = models.ForeignKey(Allotment)

    class Meta:
        db_table = "projects_allotments"

class Repeat(models.Model):
    repeat = models.CharField(max_length = 32)

    def __str__(self):
        return self.repeat

    class Meta:
        db_table = "repeats"
        
class TimeZone(models.Model):
    timeZone = models.CharField(max_length = 128)

    def __str__(self):
        return self.timeZone
        
    def utcOffset(self):
        "Returns a timedelta representing the offset from UTC."
        offset = int(self.timeZone[4:]) if self.timeZone != "UTC" else 0
        return timedelta(hours = offset)
 
    class Meta:
        db_table = "timezones"
        
class Blackout(models.Model):
    user         = models.ForeignKey(User)
    start_date   = models.DateTimeField(null = True)
    end_date     = models.DateTimeField(null = True)
    repeat       = models.ForeignKey(Repeat)
    until        = models.DateTimeField(null = True)
    description  = models.CharField(null = True, max_length = 1024)

    def __unicode__(self):
        return "%s Blackout for %s: %s - %s" % \
               (self.repeat.repeat, self.user, self.start_date, self.end_date)

    def isActive(self, date = datetime.utcnow()):
        """
        Takes a UTC datetime object and returns a Boolean indicating whether
        this blackout's effective date range is effective on this date.
        """

        if self.start_date is None:
            return False # Never started, not active
        
        if self.start_date >= date:
            return True # Happens in the future

        if not self.end_date and self.start_date <= date:
            return True # Started on/before date, never ends

        if self.start_date <= date and self.end_date >= date:
            return True # Starts on/before date, ends on/after date

        if self.repeat.repeat != "Once":
            if not self.until and self.start_date <= date:
                return True # Started on/before date, repeats forever

            if self.until and self.until >= date and self.start_date <= date:
                return True # Started on/before date, repeats on/after date

        return False

    def generateDates(self, calstart, calend):
        """
        Takes two UTC datetimes representing a period of time on the calendar.
        Returns a list of (datetime, datetime) tuples representing all the
        events generated by this blackout in that period.
        """
        if self.start_date is None or self.end_date is None:
            return [] # What does it mean to have None in start or end?

        start       = self.start_date
        end         = self.end_date
        until       = min(self.until, calend) if self.until else calend
        periodicity = self.repeat.repeat
        dates       = []

        if periodicity == "Once":
            dates.append((start, end))
        elif periodicity == "Weekly":
            while start <= until:
                if start >= calstart:
                    dates.append((start, end))

                start = start + timedelta(days = 7)
                end   = end   + timedelta(days = 7)
        elif periodicity == "Monthly":
            while start <= until:
                if start >= calstart:
                    dates.append((start, end))

                if start.month == 12: # Yearly wrap around
                    start.month = 0; start.year = start.year + 1

                start = datetime(year   = start.year
                               , month  = start.month + 1
                               , day    = start.day
                               , hour   = start.hour
                               , minute = start.minute)
                end   = datetime(year   = end.year
                               , month  = end.month + 1
                               , day    = end.day
                               , hour   = end.hour
                               , minute = end.minute)
        return dates

    def eventjson(self, calstart, calend, id = None):
        calstart = datetime.fromtimestamp(float(calstart))
        calend   = datetime.fromtimestamp(float(calend))
        dates    = self.generateDates(calstart, calend)
        title    = "%s: %s" % (self.user.name()
                             , self.description or "blackout")
        return [{
            "id"   : self.id
          , "title": title
          , "start": d[0].isoformat() if d[0] else None
          , "end"  : d[1].isoformat() if d[1] else None
        } for d in dates]

    class Meta:
        db_table = "blackouts"

class Investigator(models.Model):
    project                = models.ForeignKey(Project)
    user                   = models.ForeignKey(User)
    observer               = models.BooleanField(default = False)
    principal_contact      = models.BooleanField(default = False)
    principal_investigator = models.BooleanField(default = False)
    priority               = models.IntegerField(default = 1)

    def __unicode__(self):
        return "%s (%d) for %s; obs : %s, PC : %s, PI : %s" % \
            ( self.user
            , self.user.id
            , self.project.pcode
            , self.observer
            , self.principal_contact
            , self.principal_investigator )

    def name(self):
        return self.user

    def project_name(self):
        return self.project.pcode

    def projectBlackouts(self):
        return sorted([b for b in self.user.blackout_set.all()
                       if b.isActive()])
    
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
    freq_low     = models.FloatField(help_text = "GHz")
    freq_hi      = models.FloatField(help_text = "GHz")

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
    def extract_schedule(startdate = datetime.utcnow().date(), days = 120):
        """
        Returns the entire receiver schedule starting at 'startdate' and
        ending 'days' after the 'startdate'.  The schedule is of the form:
        {
           start_date : [<receivers available>]
        }
        where start_date is a datetime object and [<receivers available>] is
        a list of Receiver objects.
        """
        schedule = dict()

        prev = Receiver_Schedule.previousDate(startdate)
        if prev is None:
            schedule[startdate] = [] # Empty schedule on/before this date
        else:
            startdate = prev

        enddate = startdate + timedelta(days = days)
        for s in Receiver_Schedule.objects.filter(
                                              start_date__gte = startdate
                                                     ).filter(
                                              start_date__lte = enddate):
            schedule.setdefault(s.start_date, []).append(s.receiver)
        return schedule

    @staticmethod
    def previousDate(date):
        try:
            prev = Receiver_Schedule.objects.filter(start_date__lte = date).order_by('-start_date')[0].start_date
        except IndexError:
            prev = None

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
    frequency          = models.FloatField(null = True, help_text = "GHz")
    max_duration       = models.FloatField(null = True, help_text = "Hours")
    min_duration       = models.FloatField(null = True, help_text = "Hours")
    time_between       = models.FloatField(null = True, help_text = "Hours", blank = True)
    accounting_notes   = models.CharField(null = True, max_length = 1024)
    notes              = models.CharField(null = True, max_length = 1024)

    restrictions = "Unrestricted" # TBF Do we still need restrictions?

    base_url = "/sesshuns/sesshun/"

    def __unicode__(self):
        return "(%d) %s : %5.2f GHz, %5.2f Hrs, Rcvrs: %s" % (
                  self.id
                , self.name if self.name is not None else ""
                , self.frequency if self.frequency is not None else 0
                , self.allotment.total_time
                      if self.allotment.total_time is not None else 0
                , self.receiver_list())

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

    def letter_grade(self):
        return grade_float_2_abc(self.allotment.grade)

    def num_rcvr_groups(self):
        return len(self.receiver_group_set.all())

    def schedulable(self):
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
            self.get_field(fdata, "orig_ID", None, self.cast_int)
        self.name             = fdata.get("name", None)
        self.frequency        = fdata.get("freq", None)
        self.max_duration     = TimeAgent.rndHr2Qtr(float(fdata.get("req_max", 12.0)))
        self.min_duration     = TimeAgent.rndHr2Qtr(float(fdata.get("req_min",  3.0)))
        self.time_between     = fdata.get("between", None)

    def cast_int(self, strValue):
        "Handles casting of strings where int is displayed as float. ex: 1.0"
        return int(float(strValue))

    def get_field(self, fdata, key, defaultValue, cast):
        "Some values from the JSON dict we know we need to type cast"
        value = fdata.get(key, defaultValue)
        if cast != bool:
            return value if value is None else cast(value)
        else:
            return value == "true"

    def init_from_post(self, fdata):
        self.set_base_fields(fdata)

        # grade - UI deals w/ letters (A,B,C) - DB deals with floats
        grade = grade_abc_2_float(fdata.get("grade", 'A'))
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
        grade = grade_abc_2_float(fdata.get("grade", 'A'))
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

        new_transit = self.get_field(fdata, "transit", False, bool)
        old_transit = self.transit()
        tp = Parameter.objects.filter(name='Transit')[0]
        if old_transit is None:
            if new_transit:
                obs_param =  Observing_Parameter(session = self
                                               , parameter = tp
                                               , boolean_value = True
                                                )
                obs_param.save()
        else:
            obs_param = self.observing_parameter_set.filter(parameter=tp)[0]
            if new_transit:
                obs_param.boolean_value = True
                obs_param.save()
            else:
                obs_param.delete()

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

    def get_ha_limit_blackouts(self, startdate, days):
        # TBF: Not complete or even correct yet.

        targets = [(t.horizontal, t.vertical) for t in self.target_set.all()]

        # startdate, days, self.frequency, targets
        #url       = "?"
        #blackouts = json.load(urlllib.urlopen(url))['blackouts']

        #return consolidate_events(find_intersections(blackouts))

    def getObservedTime(self):
        return TimeAccounting().getObservedTime(self)

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
           , "grade"      : grade_float_2_abc(self.allotment.grade)
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

        trnst = self.transit()
        if trnst is not None:
            d.update({"transit"    : trnst})
        else:
            d.update({"transit"    : False})

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

    def transit(self):
        """
        Returns True or False if has 'Transit' observing parameter,
        else None if not.
        """
        tp = Parameter.objects.filter(name='Transit')[0]
        top = self.observing_parameter_set.filter(parameter=tp)
        return top[0].boolean_value if top else None

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
    boolean_value  = models.NullBooleanField(null = True)
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
    duration   = models.FloatField(help_text = "Hours")

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

class Period_Accounting(models.Model):

    # XX notation is from Memo 11.2
    scheduled             = models.FloatField(help_text = "Hours") # SC
    not_billable          = models.FloatField(help_text = "Hours"  # NB
                                       , default = 0.0) 
    other_session_weather = models.FloatField(help_text = "Hours"  # OS1
                                       , default = 0.0) 
    other_session_rfi     = models.FloatField(help_text = "Hours"  # OS2
                                       , default = 0.0) 
    other_session_other   = models.FloatField(help_text = "Hours"  # OS3
                                       , default = 0.0) 
    lost_time_weather     = models.FloatField(help_text = "Hours"  # LT1
                                       , default = 0.0) 
    lost_time_rfi         = models.FloatField(help_text = "Hours"  # LT2
                                       , default = 0.0) 
    lost_time_other       = models.FloatField(help_text = "Hours"  # LT3
                                       , default = 0.0) 
    short_notice          = models.FloatField(help_text = "Hours"  # SN
                                       , default = 0.0) 
    description           = models.CharField(null = True, max_length = 512)

    class Meta:
        db_table = "periods_accounting"

    def __unicode__(self):
        return "Id (%d); SC:%5.2f OT:%5.2f NB:%5.2f OS:%5.2f LT:%5.2f SN:%5.2f" % \
            (self.id
           , self.scheduled
           , self.observed()
           , self.not_billable
           , self.other_session()
           , self.lost_time()
           , self.short_notice)

    def observed(self):
        "OT = SC - OS -LT"
        return self.scheduled - self.other_session() - self.lost_time()

    def other_session(self):
        "OS = OS1 + OS2 + OS3"
        return self.other_session_weather + \
               self.other_session_rfi + \
               self.other_session_other

    def lost_time(self):
        "LT = LT1 + LT2 + LT3"
        return self.lost_time_weather + \
               self.lost_time_rfi + \
               self.lost_time_other

    def time_billed(self):
        "TB = OT - NB"
        return self.observed() - self.not_billable

    def unaccounted_time(self):
        "UT=SC-OT-OS-LT; should always be zero."
        return self.scheduled - self.observed()

    def set_changed_time(self, reason, time):
        "Determines which field to assign the time to."
        self.__setattr__(reason, time)

    def update_from_post(self, fdata):    
        fields = ['not_billable'
                , 'other_session_weather'
                , 'other_session_rfi'
                , 'other_session_other'
                , 'lost_time_weather'
                , 'lost_time_rfi'
                , 'lost_time_other'
                ]
        for field in fields:        
            self.set_changed_time(field
                                , float(fdata.get(field, "0.0")))    
        self.save()

    def jsondict(self):
        description = self.description if self.description is not None else ""
        return {"id"                    : self.id
              , "scheduled"             : self.scheduled
              , "observed"              : self.observed()
              , "not_billable"          : self.not_billable
              , "other_session"         : self.other_session()
              , "other_session_weather" : self.other_session_weather
              , "other_session_rfi"     : self.other_session_rfi
              , "other_session_other"   : self.other_session_other
              , "lost_time"             : self.lost_time()
              , "lost_time_weather"     : self.lost_time_weather
              , "lost_time_rfi"         : self.lost_time_rfi
              , "lost_time_other"       : self.lost_time_other
              , "unaccounted_time"      : self.unaccounted_time()
              , "short_notice"          : self.short_notice
              , "description"           : description}

class Period(models.Model):
    session    = models.ForeignKey(Sesshun)
    accounting = models.ForeignKey(Period_Accounting, null=True)
    start      = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")
    duration   = models.FloatField(help_text = "Hours")
    score      = models.FloatField(null = True, editable=False)
    forecast   = models.DateTimeField(null = True, editable=False)
    backup     = models.BooleanField()
    moc_ack    = models.BooleanField(default = False)

    class Meta:
        db_table = "periods"
    
    def end(self):
        "The period ends at start + duration"
        return self.start + timedelta(hours = self.duration)

    def on_day(self, day):
        "Does this period ever take place on the specified day (a datetime)?"
        next_day = day + timedelta(days = 1)
        return (self.end() > day) and (self.start < next_day)

    def __unicode__(self):
        return "Period for Session (%d): %s for %5.2f Hrs" % \
            (self.session.id, self.start, self.duration)

    def __str__(self):
        return "%s: %s for %5.2f Hrs" % \
            (self.session.name, self.start, self.duration)

    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def display_name(self):
        return self.__str__()

    def init_from_post(self, fdata, tz):
        self.from_post(fdata, tz)

    def update_from_post(self, fdata, tz):
        self.from_post(fdata, tz)
        # TBF: should we do this?
        if self.accounting is not None:
            self.accounting.update_from_post(fdata)
        

    def from_post(self, fdata, tz):
        handle = fdata.get("handle", "")
        if handle:
            self.session = self.handle2session(handle)
        else:
            try:
                maintenance = first(Project.objects.filter(pcode='Maintenance'))
                self.session = first(Sesshun.objects.filter(project=maintenance))
            except:
                self.session  = Sesshun.objects.get(id=fdata.get("session", 1))
        now           = dt2str(TimeAgent.quarter(datetime.utcnow()))
        date          = fdata.get("date", None)
        time          = fdata.get("time", "00:00")
        if date is None:
            self.start = now
        else:
            self.start = TimeAgent.quarter(strStr2dt(date, time + ':00'))
            if tz == 'ET':
                self.start = TimeAgent.est2utc(self.start)
        self.duration = TimeAgent.rndHr2Qtr(float(fdata.get("duration", "0.0")))
        self.score    = 0.0
        self.forecast = now
        #self.score    = fdata.get("score", 0.0)
        #forecast      = fdata.get("forecast", None)
        # No forecast or maybe 0 indicates new score
        #if forecast is None:
        #    self.forecast = forecast
        #else:
        #    self.forecast = TimeAgent.hour(now) # TBF: or what??
        self.backup   = True if fdata.get("backup", None) == 'true' else False
        # TBF: how to initialize scheduled time?  Do Periods need state?
        pa = Period_Accounting(scheduled = self.duration)
        pa.save()
        self.accounting = pa
        self.save()

    def handle2session(self, h):
        n, p = h.rsplit('(', 1)
        name = n.strip()
        pcode, _ = p.split(')', 1)
        return Sesshun.objects.filter(project__pcode__exact=pcode).get(name=name)

    def toHandle(self):
        if self.session.original_id is None:
            original_id = ""
        else:
            original_id = str(self.session.original_id)
        return "%s (%s) %s" % (self.session.name
                             , self.session.project.pcode
                             , original_id)

    def eventjson(self, id):
        end = self.start + timedelta(hours = self.duration)

        return {
                "id"   : id
              , "title": "".join(["Observing ", self.session.name])
              , "start": self.start.isoformat()
              , "end"  : end.isoformat()
        }

    def jsondict(self, tz):
        start = self.start if tz == 'UTC' else TimeAgent.utc2est(self.start)
        js =   {"id"           : self.id
              , "session"      : self.session.jsondict()
              , "handle"       : self.toHandle()
              , "stype"        : self.session.session_type.type[0].swapcase()
              , "date"         : d2str(start)
              , "time"         : t2str(start)
               , "lst"          : str(TimeAgent.dt2tlst(self.start))
              , "duration"     : self.duration
              , "score"        : self.score
              , "forecast"     : dt2str(self.forecast)
              , "backup"       : self.backup
                }
        # include the accounting but keep the dict flat
        if self.accounting is not None:
            accounting_js = self.accounting.jsondict()
            # make sure the final jsondict has only one 'id'
            accounting_id = accounting_js.pop('id')
            accounting_js.update({'accounting_id' : accounting_id})
            js.update(accounting_js)
        return js

    def moc_met(self):
        """
        Returns a Boolean indicated if MOC are met (True) or not (False).
        Only bothers to calculate MOC for open sessions whose end time
        is not already past.
        """
        return True   # until fixed
        # TBF: When windows are working correctly, replace with line below.
        #if self.session.session_type.type not in ("open", "windowed") or \
        if self.session.session_type.type not in ("open",) or \
           self.end() < datetime.utcnow():
            return True

        url = ANTIOCH_SERVER_URL + \
              "/moc?session_id=" + \
              `self.session.id` + \
              "&start=" + \
              self.start.isoformat().replace("T", "+").replace(":", "%3A")
        try:
            antioch_cnn = urllib2.build_opener().open(url)
            moc = json.loads(antioch_cnn.read(0x4000))['moc']
        except:
            moc = True

        return moc

    def has_required_receivers(self):

        # Find all the required receiver sets for this period and schedule.
        # E.g. for one session:
        #     [[a, b, c], [x, y, z]] = (a OR b OR c) AND (x OR y OR z)
        required = [self.session.receiver_group_set.all()]
        if required == []:
            return False # No receivers, problem!

        schedule = Receiver_Schedule.extract_schedule(self.start, 0)
        if schedule == {}:
            return False # no schedule, no required rcvrs!
        # should return a single date w/ rcvr list
        items = schedule.items()
        assert len(items) == 1
        dt, receivers = items[0]

        receivers = Set(receivers)
        if not any([all([Set(g.receivers.all()).intersection(receivers) \
                        for g in set]) for set in required]):
            # No receivers available. 
            return False
        else:
            return True

    @staticmethod
    def get_periods(start, duration):
        "Returns all periods that overlap given time interval (start, minutes)"
        end = start + timedelta(minutes = duration)
        # there is no Period.end in the database, so, first cast a wide net.
        # we can do this because periods won't last more then 16 hours ...
        beforeStart = start - timedelta(days = 1)
        afterEnd    = end   + timedelta(days = 1)
        some = Period.objects.filter(start__gt = beforeStart
                                   , start__lt = afterEnd).order_by('start')
        # now widdle this down to just the periods that overlap  
        ps = [p for p in some if (p.start >= start and p.end() <= end) \
                              or (p.start <= start and p.end() > start) \
                              or (p.start < end    and p.end() >= end)]
        return ps
          
        
    @staticmethod    
    def in_time_range(begin, end):
        """
        Returns all periods in a time range, taking into account that periods
        can overlap into the first day.
        """
        # TBF: why doesn't ps.query.group_by = ['start'] work?
        day_before = begin - timedelta(days = 1)
        return Period.objects.filter(start__gt = day_before
                                   , start__lt = end).order_by('start')

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

# TBF: might need this in order to get around Haskell not working w/ BOS
#class Reservation(models.Model):
#    user       = models.ForeignKey(User)
#    start_date = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")
#    end_date   = models.DateTimeField(help_text = "yyyy-mm-dd hh:mm:ss")
#
#    class Meta:
#        db_table = "reservations"
    
