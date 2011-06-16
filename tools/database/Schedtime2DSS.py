from datetime                          import datetime, timedelta
from nell.utilities                    import TimeAgent
from scheduler.models                   import *
import math
import MySQLdb as m
import sys

from nell.tools.reports.Report import Report, Line

class Schedtime2DSS(object):

    """
    This class is reponsible for fetching data from the 'schedtime' table
    which is a raw table in MySQL that is a direct dump from Carl's system.
    This is how we transfer over fixed periods and their associated
    projects & sessions.
    """

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "dss"
                     , passwd = "asdf5!"
                     , database = "dss_prime"
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                            )
        self.cursor = self.db.cursor()
        self.silent = silent
        self.semester = Semester()

        self.total_periods_before = None
        self.total_periods_after = None

        # Map Carl's rcvr abbreviations to ours:
        # should we eventually move this into the DB? nope.
        # Carl -> DSS
        self.rcvrMap = { 'R' : 'RRI'
                       , '3' : '342'
                       , '4' : '450'
                       , '6' : '600'
                       , '8' : '800'
                       , 'A' : '1070'
                       , 'L' : 'L'
                       , 'S' : 'S'
                       , 'C' : 'C'
                       , 'X' : 'X'
                       , 'U' : 'Ku'
                       , 'K' : 'K'
                       , 'B' : 'Ka'
                       , 'Q' : 'Q'
                       , 'M' : 'MBA'
                       , 'H' : 'Hol'
                       , 'PF2'   : '1070' # inconsistent!
                       , 'PF1*3' : '342'
                       , 'PF1*4' : '450'
                       , 'PF1*6' : '600'
                       , 'PF1*8' : '800'
                       , 'RRI'   : 'RRI'
                      }

        # for keeping track of period times (checking for overlaps)
        self.times = []
        # where does the pcode start?
        self.proj_counter = 500
        # a unique list of 'activity-observer'
        self.session_names = []


    def transfer_fixed_periods(self, semester):
        """
        We can dump Carl's DB into MySQL tables and use these to suck
        whatever info we need in addition to what is in the DB that
        Carl dumped to.
        Here we will take all 'scheduled dates' and replicate them
        as periods so that in the simulations they get translated
        into fixed periods that we pack around.
        The tricky part is creating the correct projects & sessions:
        Maintanence & Shutdown is easy, but the different types of tests
        need the appropriate project & session names, along w/ appropriate
        observer.
        """

        self.total_periods_before = Period.objects.all()
        self.period_ids_before = []

        for i in self.total_periods_before:
            self.period_ids_before.append(i.id)

        testingTypes = ['Tests', 'Calibration', 'Commissioning']

        # Only transfer fixed periods from schedtime table that cover
        start, end = self.get_schedtime_dates(semester)

        # prepare for transfering over fixed periods by creating the
        # necessary projects & session we know we'll need
        self.create_project_and_session( semester
                                       , "Maintenance"
                                       , "non-science"
                                       , "Maintenance"
                                       , "maintenance")
        self.create_project_and_session( semester
                                       , "Shutdown"
                                       , "non-science"
                                       , "Shutdown"
                                       , "maintenance")


        query = """
        SELECT `etdate`, `startet`, `stopet`, `lengthet`, `type`, `pcode`, `vpkey`, `desc`,
               `bands`, `be`, `observers`
        FROM `schedtime`
        WHERE `etdate` >= %s AND `etdate` < %s
        ORDER BY `etdate`, `startet`
        """ % (start, end)

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            #print row
            # translate row:
            # first, datetime info
            dt = row[0]
            year = int(dt[:4])
            month = int(dt[4:6])
            day = int(dt[6:])

            start_time = row[1]
            hour = int(start_time[:2])
            minutesTrue = int(start_time[2:])

            # DSS operates on hourly quarters: so minutes must be -
            # 0, 15, 30, 45
            # round down starttime to avoid overlaps!
            if 0 <= minutesTrue and minutesTrue < 15:
                minute = 0
            elif 15 <= minutesTrue and minutesTrue < 30:
                minute = 15
            elif 30 <= minutesTrue and minutesTrue < 45:
                minute = 30
            else:
                minute = 45

            # raise an alarm?
            if minute != minutesTrue:
                print >> sys.stderr, "minutes changed from %d to %d for row: " % (minutesTrue, minute), row

            durationHrs = float(row[3].strip())

            # DSS operates on hourly quarters: we need to truncate these
            # down to the nearest quarter to avoid overlaps
            duration = (int((durationHrs * 60) / 15) * 15 ) / 60.0

            # raise an alarm?
            if abs(duration - durationHrs) > 0.01:
                print >> sys.stderr, "duration changed from %f to %f for row: " % (durationHrs, duration), row

            # create the starttime - translate from ET to UT
            start = TimeAgent.est2utc(datetime(year, month, day, hour, minute))

            # get other row values that we'll always need
            type = row[4].strip()
            pcode = row[5].strip()
            try:
                original_id = int(row[6])
            except:
                original_id = None



            # what session to link this to?
            if type in testingTypes:
                s = self.get_testing_session(row, duration, semester)
            elif type == "Maintenance":
                # Maintenance is simple
                s = Sesshun.objects.filter(name = "Maintenance")[0]
            elif type == "Shutdown":
                # Shutdown is simple - not a whole lot going on
                s = Sesshun.objects.filter(name = "Shutdown")[0]
            elif type == "Astronomy":
                # Astronomy is only complicated if something's not right
                # can we use the vpkey?
                if original_id is not None and original_id != 0:
                    # simple case - we're done
                    #print "looking for original_id: ", original_id
                    s = Sesshun.objects.filter(original_id = original_id)[0]
                elif pcode is not None and pcode != "":
                    # try getting a session from the project - we rarely see it
#                    print "Getting Session from pcode: ", pcode
                    p = Project.objects.get(pcode = pcode)
                    s = p.sesshun_set.all()[0] # totally arbitrary!
                else:
                    # failure: this will raise an alarm
                    s = None
            else:
                raise "Unknown Type in Schedtime table."

            # don't save stuff that will cause overlaps
            causesOverlap = self.findOverlap(start, duration)

            if s is not None:

                # check for problems
                # are we assigning fixed periods for open sessions?
                if s.session_type.type == 'open':
                    print >> sys.stderr, "Period fixed for Session of type: ",\
                          s.session_type.type, s, start, duration
                    if duration > s.max_duration or duration < s.min_duration:
                        print >> sys.stderr, "Open Session duration (%f) does not honor min/max: %f/%f"\
                            % (duration, s.min_duration, s.max_duration)
                        print >> sys.stderr, s

                # don't save it off if it caused an overlap
                if causesOverlap:
                    print >> sys.stderr, "Causes Overlap!: ", s, start, duration
                else:
                    #NOTE: we are no longer using windows
                    # instead, just saves these off as periods
                    pa = Period_Accounting(scheduled = duration)
                    pa.save()
                    pending = Period_State.get_state("P")
                    p = Period(session    = s
                             , start      = start
                             , duration   = duration
                             , score      = 0.0
                             , forecast   = datetime.now()
                             , backup     = False
                             , state      = pending
                             , accounting = pa)
                    p.save()
                    # keep track of this added one so we can
                    # check for subsequent overlaps
                    self.times.append((s, start, duration))
            else:
                # warn the user:
                print >> sys.stderr, "Schedtime2DSS: could not find session for row: ", row

        # for debugging:
        #ps = self.get_testing_project_info()
        #for p in ps:
        #    print p


    def get_testing_project_info(self):
        "Returns info on testing projects - good for debugging."
        ps = Project.objects.filter(pcode__contains = 'TGBT09C').all()
        return [(p.pcode
              , [s.name for s in p.sesshun_set.all()]
              , [i.user for i in p.investigators_set.all()]) for p in ps]


    def get_testing_session(self, row, duration, semester):
        """
        Now for the tricky part.  requirments:
        *  non-science projects & sessions must be imported into the DSS
           such that Green Bank staff can determine:
              o the type of activity covered by the project/session
              o the GB staff member responsible for any particular fixed period
              o the hardware needed, including:
                    + receiver
        * all project codes created during the transfer must follow the
          following pattern: TGBT$$$_### where:
              o $$$ - current semester (e.g. '09C')
              o ### - auto-incrementing integer, starting at 500 for 09C
        """
        # get the additional info from the row we'll need
        description = row[7].strip()
        receivers = self.get_schedtime_rcvrs(row[8].strip())
        backend = row[9].strip()
        observers = self.get_schedtime_observers(row[10].strip())
        # Simplest implimentaion: each unique desc is a unique proj/sess
        activity, observerName = self.parse_schedtime_description(description)
        # construct a unique session name based of activity and observer(s)
        observers = self.add_observer(observers, observerName)
        obsNamesStr = ','.join([o.last_name for o in observers])
        sess_name = activity
        if obsNamesStr != '':
            sess_name += "-" + obsNamesStr
        # unique?
        if sess_name not in self.session_names:
            self.session_names.append(sess_name)
            # create the project & session
            proj_name = self.get_project_name(semester, self.proj_counter)
            self.proj_counter += 1
            proj = self.create_project_and_session( semester
                                                  , proj_name
                                                  , "non-science"
                                                  , sess_name
                                                  , "testing")
            # set additional info
            # assign observers
            for priority, o in enumerate(observers):
                i = Investigator( project  = proj
                                , user     = o
                                , observer = True
                                , priority = priority
                                , principal_contact = (priority==0)
                                , principal_investigator = (priority==0)
                            )
                i.save()
            # assign session rcvrs, allotetd time ...
            s = proj.sesshun_set.all()[0]
            s.allotment.total_time = duration
            s.allotment.save()
            s.save()
            # assume just one rcvr group
            rg = Receiver_Group(session = s)
            rg.save()
            for rcvr in receivers:
                rg.receivers.add(rcvr)
            rg.save()
            s.save()
        else:
            # we've already created this proj/sess
            s = Sesshun.objects.filter(name = sess_name)[0]
            # update it's alloted time to take into account
            # this new period
            s.allotment.total_time += duration
            s.allotment.save()
            s.save()

        return s

    def parse_schedtime_description(self, description):
        """
        The desc_ field is overloaded with info:
        desc_ format = [Ta:]activity[-observer]
        """

        # strip out the possible 'Ta:'
        description = description.split(':')[-1]
        # now create a session name based of desc_ and observers
        # split up activity from possible observer
        parts = description.split('-')
        if len(parts) == 1:
            activity = parts[0]
            observerName = None
        elif len(parts) == 2:
            activity = parts[0]
            observerName = parts[1]
        else:
            raise "Bad Schedtime.desc_ format.  Blame Mike McCarty."
        return (activity, observerName)

    def get_schedtime_dates(self, semester):
        "Schedtime table has a peculiar datetime system."
        self.semester.semester = semester

        try:
            startdate = self.semester.start()
            enddate = self.semester.end()
        except KeyError:
            raise "Invalid semester designator %s.  Must be A, B, or C" % semester[2:]
        except ValueError:
            raise "Invalid semester year %s.  Must be numeric, 00 - 99" % semester[:2]

        start = self.date_to_string(startdate)
        end = self.date_to_string(enddate)
        return (start, end)

    def date_to_string(self, date):
        year = str(date.year)
        month = str(date.month)

        if len(month) == 1:
            month = "0" + month

        day = str(date.day)

        if len(day) == 1:
            day = "0" + day

        return year + month + day

    def get_project_name(self, semester, counter):
        return "TGBT%s_%03d" % (semester, counter)

    def get_schedtime_rcvrs(self, bands):
        "Maps entries in schedtime.bands to our receiver objects"
        # this is so inconsistent!
        if bands in ['RRI', 'PF1*3', 'PF1*4', 'PF1*6', 'PF1*8', 'PF2']:
            return [Receiver.objects.get(abbreviation = self.rcvrMap[bands])]
        else:
            return [Receiver.objects.get(abbreviation = self.rcvrMap[b]) for b in bands]

    def get_schedtime_observers(self, names):
        "Maps entries in schedtime.observers to our user objects"
        names = names.split('&')
        observers = []
        for name in names:
            if name != '':
                observers = self.add_observer(observers, name.strip())
        return observers

    def add_observer(self, observers, last_name):
        "Adds observer to list, only if last_name isn't in list already"
        obs = self.get_unique_user(last_name)
        if obs is not None and obs not in observers:
            observers.insert(0, obs) # add observer to start of list
        return observers

    def get_unique_user(self, last_name):
        "This last name you give me better be unique or I'm taking my ball home"
        # fundamental flaw here: all we've got are last names.  We
        # have to make assumptions that this means certain staff members
        users = User.objects.filter(last_name = last_name).all()
        if len(users) == 0:
            return None
        elif len(users) > 1:
            # Nothing to do here but make some assumptions.
            # Who else?
            if last_name == "Ford":
                # assume it's John and not Pam!
                return User.objects.filter(last_name = last_name
                                               , first_name = "John")[0]
            else:
                return users[0]
        else:
            return users[0]

    def findOverlap(self, start, dur):
        for _, start2, dur2 in self.times:
            if self.overlap(start, dur, start2, dur2):
                print >> sys.stderr, "overlap: ", start, dur, start2, dur2
                return True
        return False

    def overlap(self, start1, dur1, start2, dur2):
        end1 = start1 + timedelta(seconds = dur1 * 60 * 60)
        end2 = start2 + timedelta(seconds = dur2 * 60 * 60)
        return start1 < end2 and start2 < end1

    def create_project_and_session(self, semesterName
                                       , projectName
                                       , projectType
                                       , sessionName
                                       , observingType):
        """
        Creates a project & single session
        """

        # clean up!
        ps = Project.objects.filter(pcode = projectName)

        # Don't want to wipe out project Maintenance, if it's there.
        # If it is, nothing more to be done.  But if it isn't there,
        # we need to create it.
        if projectName in ["Maintenance", "Shutdown"] and len(ps) > 0:
            return

        ss = Sesshun.objects.filter(name = sessionName)

        # first, just set up the project and single session
        self.semester.semester = semesterName

        try:
            semesterStart = self.semester.start()
            semesterEnd = self.semester.end()
        except KeyError:
            raise "Invalid semester designator %s.  Must be A, B, or C" % semester[2:]
        except ValueError:
            raise "Invalid semester year %s.  Must be numeric, 00 - 99" % semester[:2]

        semester = Semester.objects.get(semester = semesterName)
        ptype    = Project_Type.objects.get(type = projectType)

        p = Project(semester     = semester
                  , project_type = ptype
                  , pcode        = projectName
                  , name         = projectName
                  , thesis       = False
                  , complete     = False
                  , start_date   = semesterStart
                  , end_date     = semesterEnd
                    )
        p.save()

        # max hours should be some generous estimate of the time needed
        maxHrs = (16 * 10.5)
        allot = Allotment(psc_time          = maxHrs
                        , total_time        = maxHrs
                        , max_semester_time = maxHrs
                        , grade             = 4.0
                          )
        allot.save()
        pa = Project_Allotment(project = p, allotment = allot)
        pa.save()
        p.project_allotment_set.add(pa)
        status = Status(enabled    = False
                      , authorized = False
                      , complete   = False
                      , backup     = False
                        )
        status.save()
        otype    = Observing_Type.objects.get(type = observingType)
        stype    = Session_Type.objects.get(type = "fixed")
        # original_id is meaningless here, since we don't have this
        # record from Carl's system.  Just use something distinctive,
        # like the number of the beast, say.
        ourId = 666
        s = Sesshun(project        = p
                  , session_type   = stype
                  , observing_type = otype
                  , allotment      = allot
                  , status         = status
                  , original_id    = ourId 
                  , name           = sessionName
                  , frequency      = 0.0 #None
                  , max_duration   = 12.0 #None
                  , min_duration   = 1.0 #None
                  , time_between   = 0.0 #None
                    )
        s.save()

        # put in a dummy target so that Antioch can pick it up!
        system = System.objects.get(name = "J2000")
        target = Target(session    = s
                      , system     = system
                      , source     = sessionName
                      , vertical   = 0.0
                      , horizontal = 0.0
                    )
        target.save()

        # return the project, which links in the session
        return p

    def report_result(self, semester, sess_type, periods):
        dss_prime_sql = """select `etdate`, `startet`, `lengthet`, `type`, `desc`
                               from schedtime
                               where `etdate` >= \"%s\" and `etdate` <= \"%s\"
                               and %s order by `etdate`"""


        self.semester.semester = semester;
        start_date = self.semester.start()

        if sess_type == "Tests":
            type_clause = "(type = 'Tests' or type = 'Commissioning')"
        else:
            type_clause = "type = \"%s\"" % sess_type

        start, end = self.get_schedtime_dates(semester)
        header = ["date", "start (ET)", "length", "type", "desc"]
        dss_header = ["date", "start (UT)", "length", "pcode", "desc"]

        self.cursor.execute(dss_prime_sql % (start, end, type_clause))
        rows = self.cursor.fetchall()

        dss_prime_report = Report()
        line = Line()

        for i in header:
            line.add(i)

        dss_prime_report.add_headers(line)

        for row in rows:
            line.clear()

            for item in row:
                line.add(item)

            dss_prime_report.add_line(line)


        if sess_type == "Tests":
            pcode = "TGBT" + semester
        else:
            pcode = sess_type

        dss_report = Report()
        line.clear()

        for i in dss_header:
            line.add(i)

        dss_report.add_headers(line)

        for p in periods:
            line.clear()
            line.add(self.date_to_string(p.start))
            line.add("%02i" % p.start.hour + "%02i" % p.start.minute)
            line.add(p.duration)
            line.add(p.session.project.pcode)
            line.add(p.session.name)
            dss_report.add_line(line)

        return dss_prime_report, dss_report


    def print_report(self, semester):

        self.total_periods_after = Period.objects.all()
        self.period_ids_after = []

        for i in self.total_periods_after:
            self.period_ids_after.append(i.id)

        lbefore = len(self.period_ids_before)
        lafter = len(self.period_ids_after)
        new_periods = self.total_periods_after

        if lafter == lbefore:
            print "No new periods transferred!"
            return

        for i in self.total_periods_before:
            new_periods = new_periods.exclude(id__exact = i.id)

        print "\nPeriods before: %i, after: %i, transferred: %i" % (lbefore, lafter, len(new_periods))

        new_tests = new_periods.filter(session__observing_type__type = "testing").order_by("start")
        new_periods = new_periods.exclude(session__observing_type__type = "testing")

        new_maintenance = new_periods.filter(session__project__pcode = "Maintenance").order_by("start")
        new_periods = new_periods.exclude(session__project__pcode = "Maintenance")

        new_shutdown = new_periods.filter(session__project__pcode = "Shutdown").order_by("start")
        new_periods = new_periods.exclude(session__project__pcode = "Shutdown")

        new_astronomy = new_periods

        (prime_astronomy, dss_astronomy) = self.report_result(semester, "Astronomy", new_astronomy)
        (prime_tests, dss_tests) = self.report_result(semester, "Tests", new_tests)
        (prime_maintenance, dss_maintenance) = self.report_result(semester, "Maintenance", new_maintenance)
        (prime_shutdown, dss_shutdown) = self.report_result(semester, "Shutdown", new_shutdown)

        print "\nSummary of results:\n"
        print "Astronomy: %i entries found, %i entries transferred." % \
              (prime_astronomy.lines(), dss_astronomy.lines())
        print "Test and commissioning: %i entries found, %i entries tranferred." % \
              (prime_tests.lines(), dss_tests.lines())
        print "Maintenance: %i entries found, %i entries transferred." % \
              (prime_maintenance.lines(), dss_maintenance.lines())
        print "Shutdown: %i entries found, %i entries transferred." % \
              (prime_shutdown.lines(), dss_shutdown.lines())

        print "\nAstronomy, DSS':"
        prime_astronomy.output()
        print "%i rows" % prime_astronomy.lines()
        print "\nAstronomy, DSS:"
        dss_astronomy.output()
        print "%i rows" % dss_astronomy.lines()
        print "\nTest and commissioning, DSS':"
        prime_tests.output()
        print "%i rows" % prime_tests.lines()
        print "\nTest and commissioning, DSS:"
        dss_tests.output()
        print "%i rows" % dss_tests.lines()
        print "\nMaintenance, DSS':"
        prime_maintenance.output()
        print "%i rows" % prime_maintenance.lines()
        print "\nMaintenance, DSS:"
        dss_maintenance.output()
        print "%i rows" % dss_maintenance.lines()
        print "\nShutdown, DSS':"
        prime_shutdown.output()
        print "%i rows" % prime_shutdown.lines()
        print "\nShutdown, DSS:"
        dss_shutdown.output()
        print "%i rows" % dss_shutdown.lines()
