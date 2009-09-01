from sesshuns.models import *
from datetime        import datetime, timedelta
from utilities.database.UserNames import UserNames
import math
import MySQLdb as m

class DSSPrime2DSS(object):
    """
    This class is reponsible for fetching data from the 'stepping stone'
    database, which is where the proposal information is stored after the
    export from Carl's database, and importing this data into the DSS database.
    """

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "dss"
                     , passwd = "asdf5!"
                     , database = "dss_prime"
                     #, database = "dss_prime_backup_310809"
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                            )
        self.cursor = self.db.cursor()
        self.silent = silent

        # Carl transferred only Astronomy Windows & Opportunities.
        # set this to false if you are to ignore these and instead want
        # to use our self.create_09B_opportunities 
        self.use_transferred_windows = False

    def __del__(self):
        self.cursor.close()

    def transfer(self):
        self.transfer_projects()
        self.transfer_authors()
        self.transfer_friends()
        self.transfer_sessions()

            
    def transfer_sessions(self):
        query = """
                SELECT sessions.*
                     , projects.pcode
                     , allotment.*
                     , status.*
                     , observing_types.type
                     , session_types.type
                FROM sessions
                INNER JOIN (projects
                          , allotment
                          , status
                          , observing_types
                          , session_types)
                ON sessions.project_id = projects.id AND
                   sessions.allotment_id = allotment.id AND
                   sessions.status_id = status.id AND
                   sessions.observing_type_id = observing_types.id AND
                   sessions.session_type_id = session_types.id
                ORDER BY sessions.id
                """
        self.cursor.execute(query)
        
        rows = self.cursor.fetchall()

        # Just run a quick query to check that we got all the sessions
        self.cursor.execute("SELECT id FROM sessions")
        results = self.cursor.fetchall()
        assert len(results) == len(rows)

        for row in rows:
            otype = first(Observing_Type.objects.filter(type = row[23]))
            stype = first(Session_Type.objects.filter(type = row[24]))
            project = first(Project.objects.filter(pcode = row[12]))

            if project is None:
                print "*********Transfer Sessions Error: no project for pcode: ", row[12]
                continue
              

            allot = Allotment(psc_time          = float(row[14])
                            , total_time        = float(row[15])
                            , max_semester_time = float(row[16])
                            , grade             = float(row[17])
                              )
            allot.save()

            status = Status(enabled    = row[19] == 1
                          , authorized = row[20] == 1
                          , complete   = row[21] == 1
                          , backup     = row[22] == 1
                            )
            status.save()

            s = Sesshun(project        = project
                      , session_type   = stype
                      , observing_type = otype
                      , allotment      = allot
                      , status         = status
                      , original_id    = row[6] 
                      , name           = row[7]
                      , frequency      = float(row[8]) if row[8] is not None else None
                      , max_duration   = float(row[9]) if row[9] is not None else None
                      , min_duration   = float(row[10]) if row[10] is not None else None
                      , time_between   = float(row[11]) if row[11] is not None else None
                        )
            s.save()

            # now get the sources
            s_id_prime = row[0]
            query = """
                    SELECT *
                    FROM targets
                    WHERE session_id = %s
                    """ % s_id_prime
            self.cursor.execute(query)

            # All Systems J2000!
            system = first(System.objects.filter(name = "J2000"))

            for t in self.cursor.fetchall():
                try:
                    vertical = float(t[4])
                except:
                    vertical = None
                    #print "Exception with row: ", t, s
                try:
                    horizontal = float(t[5])
                except:
                    horizontal = None
                    #print "Exception with row: ", t, s
                if vertical is not None and horizontal is not None:    
                    target = Target(session    = s
                              , system     = system
                              , source     = t[3]
                              , vertical   = float(t[4]) * (math.pi / 180)
                              , horizontal = float(t[5]) * (math.pi / 12)
                                )
                    target.save()

            # now get the windows & opportunities
            # TBF: initially, we thought there would be none of these, and
            # they'd all be determined via the Cadences!
            if self.use_transferred_windows:
                query = "SELECT * FROM windows WHERE session_id = %s" % s_id_prime
                self.cursor.execute(query)
                for w in self.cursor.fetchall():
                    win = Window(session = s, required = w[2])
                    win.save()
      
                    query = "SELECT * FROM opportunities WHERE window_id = %s" % w[0]
                    self.cursor.execute(query)
                    
                    for o in self.cursor.fetchall():
                        op = Opportunity(window = win
                                       , start_time = o[2]
                                       , duration = float(o[3])
                                       )
                        op.save()

            # now get the rcvrs
            query = "SELECT id FROM receiver_groups WHERE session_id = %s" % s_id_prime
            self.cursor.execute(query)

            for id in self.cursor.fetchall():
                rg = Receiver_Group(session = s)
                rg.save()

                query = """SELECT receivers.name
                           FROM rg_receiver
                           INNER JOIN receivers ON rg_receiver.receiver_id = receivers.id
                           WHERE group_id = %s
                        """ % id
                self.cursor.execute(query)

                for r_name in self.cursor.fetchall():
                    rcvr = first(Receiver.objects.filter(name = r_name[0]))
                    rg.receivers.add(rcvr)
                rg.save()
                
            # now get the observing parameters
            query = """SELECT * 
                       FROM observing_parameters 
                       WHERE session_id = %s
                    """ % s_id_prime
            self.cursor.execute(query)

            for o in self.cursor.fetchall():
                p  = first(Parameter.objects.filter(id = o[2]))
                if p.name == 'Instruments' and o[3] == "None":
                    pass
                    #print "Not passing over Observing Parameter = Instruments(None)"
                else:    
                    op = Observing_Parameter(
                    session        = s
                  , parameter      = p
                  , string_value   = o[3] if o[3] is not None else None
                  , integer_value  = o[4] if o[4] is not None else None 
                  , float_value    = float(o[5]) if o[5] is not None else None
                  , boolean_value  = o[6] == 1 if o[6] is not None else None
                  , datetime_value = o[7] if o[7] is not None else None
                )
                    op.save()

        #self.populate_windows()

    def transfer_authors(self):

        query = "SELECT * FROM authors"
        self.cursor.execute(query)

        for row in self.cursor.fetchall():
            row  = list(row)
            p_id = row.pop(1)
            u    = self.create_user(row)
            
            query = "SELECT pcode FROM projects WHERE id = %s" % p_id
            self.cursor.execute(query)
            pcode = self.cursor.fetchone()[0]
            p     = first(Project.objects.filter(pcode = pcode).all())

            if p is None:
                print "*****ERROR: project absent for pcode: ", pcode
                continue

            i = Investigators(project = p
                            , user    = u
                            , principal_contact      = row[6] == 1
                            , principal_investigator = row[5] == 1
                              )
            i.save()

    def transfer_projects(self):
        query = """
                SELECT *
                FROM projects
                INNER JOIN (semesters, project_types)
                ON projects.semester_id = semesters.id AND
                   projects.project_type_id = project_types.id
                """
        self.cursor.execute(query)
        
        rows = self.cursor.fetchall()
        for row in rows:
            semester = first(Semester.objects.filter(semester = row[12]))
            ptype    = first(Project_Type.objects.filter(type = row[14]))

            p = Project(semester     = semester
                      , project_type = ptype
                      , pcode        = row[4]
                      , name         = self.filter_bad_char(row[5])
                      , thesis       = row[6] == 1
                      , complete     = row[7] == 1
                      , start_date   = row[9]
                      , end_date     = row[10]
                        )
            p.save()

            f_id = row[3]
            if f_id != 0:
                query = "select peoplekey from friends where id = %s" % f_id
                self.cursor.execute(query)

                o_id   = int(self.cursor.fetchone()[0])
                friend = first(User.objects.filter(original_id = o_id))
                query = "select * from friends where id = %s" % f_id
                self.cursor.execute(query)

                if friend is not None:
                    i = Investigators(project = p
                                    , user    = friend
                                    , friend  = True
                                      )
                    i.save()

            query = """
                    SELECT projects.pcode, allotment.*
                    FROM `projects`
                    LEFT JOIN (projects_allotments, allotment)
                    ON (projects.id = projects_allotments.project_id AND
                        projects_allotments.allotment_id = allotment.id)
                    WHERE projects.pcode = '%s'
                    """ % p.pcode
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                try:
                    psc, total, max_sem, grade = map(float, row[2:])
                except TypeError:
                    if not self.silent:
                        print "No alloment for project", p.pcode
                else:
                    a = Allotment(psc_time          = psc
                                , total_time        = total
                                , max_semester_time = max_sem
                                , grade             = grade
                                  )
                    a.save()

                    pa = Project_Allotment(project = p, allotment = a)
                    pa.save()

    def transfer_friends(self):

        query = "SELECT * FROM friends"
        self.cursor.execute(query)
        
        for row in self.cursor.fetchall():
            _   = self.create_user(row)

    def create_user(self, row):

        # Check to see if the user is already in the system
        user = first(User.objects.filter(original_id = int(row[3])).all())

        # Skip to the next user if this one has been found
        if user is not None:
            row = self.cursor.fetchone()
            return user
            
        # TBF: we must support outrageous accents
        try:
            firstName = unicode(row[1])
        except:
            #print "exception with name: ", row[1]
            firstName = "exception"

        try:
            lastName = unicode(row[2])
        except:
            #print "exception with name: ", row[2]
            lastName = "exception"

        if len(row) > 7:
            pst_id = int(row[7])
            if pst_id == 0:
                pst_id = None
        else:
            pst_id = None

        u = User(original_id = int(row[3])
               , sanctioned  = False
               , first_name  = firstName #row[1]
               , last_name   = lastName #row[2]
               , pst_id      = pst_id 
               , role        = first(Role.objects.filter(role = "Observer"))
                 )
        u.save()

        for e in row[4].split(','):
            e = e.replace('\xad', '')
            # Check to see if the email address already exists.
            email = first(Email.objects.filter(email = e).all())

            # Create a new email record if email not found.
            if email is None:
                new_email = Email(user = u, email = e)
                #print "created email: ", e
                #print "for user: ", u
                #x = raw_input("check: ")
                new_email.save()

        return u
            
    def filter_bad_char(self, bad):
        good = bad.replace('\xad', '')
        return good
    


    

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
        empty = [p.delete() for p in ps]
        ss = Sesshun.objects.filter(name = sessionName)
        empty = [s.delete() for s in ss]

        # first, just set up the project and single session
        if semesterName == "09C":
            semesterStart = datetime(2009, 10, 1)
            semesterEnd = datetime(2010, 1, 31)
        else:
            semesterStart = datetime(2009, 6, 1)
            semesterEnd = datetime(2009, 9, 30)

        semester = first(Semester.objects.filter(semester = semesterName))
        ptype    = first(Project_Type.objects.filter(type = projectType))

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
        status = Status(enabled    = True 
                      , authorized = True
                      , complete   = False 
                      , backup     = False
                        )
        status.save()
        otype    = first(Observing_Type.objects.filter(type = observingType))
        stype    = first(Session_Type.objects.filter(type = "fixed"))
        s = Sesshun(project        = p
                  , session_type   = stype
                  , observing_type = otype
                  , allotment      = allot
                  , status         = status
                  , original_id    = 666 # TBF? 
                  , name           = sessionName 
                  , frequency      = 0.0 #None
                  , max_duration   = 12.0 #None
                  , min_duration   = 0.0 #None
                  , time_between   = 0.0 #None
                    )
        s.save()
        print s

        # TBF: put in a dummy target so that Antioch can pick it up!
        system = first(System.objects.filter(name = "J2000"))
        target = Target(session    = s
                      , system     = system
                      , source     = sessionName 
                      , vertical   = 0.0
                      , horizontal = 0.0
                    )
        target.save()

        # return the project, which links in the session
        return p

    def create_maintenance_session(self, semesterName):
        """
        Creates the maintenance session, but not the date
        """

        # clean up!
        ps = Project.objects.filter(pcode = "Maintenance")
        empty = [p.delete() for p in ps]
        ss = Sesshun.objects.filter(name = "Maintenance")
        empty = [s.delete() for s in ss]

        # first, just set up the project and single session
        if semesterName == "09C":
            semesterStart = datetime(2009, 10, 1)
            semesterEnd = datetime(2010, 1, 31)
        else:
            semesterStart = datetime(2009, 6, 1)
            semesterEnd = datetime(2009, 9, 30)

        semester = first(Semester.objects.filter(semester = semesterName))
        ptype    = first(Project_Type.objects.filter(type = "non-science"))

        p = Project(semester     = semester
                  , project_type = ptype
                  , pcode        = "Maintenance"
                  , name         = "Maintenance"
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
        status = Status(enabled    = True 
                      , authorized = True
                      , complete   = False 
                      , backup     = False
                        )
        status.save()
        otype    = first(Observing_Type.objects.filter(type = "maintenance"))
        stype    = first(Session_Type.objects.filter(type = "fixed"))
        s = Sesshun(project        = p
                  , session_type   = stype
                  , observing_type = otype
                  , allotment      = allot
                  , status         = status
                  , original_id    = 666 # TBF? 
                  , name           = "Maintenance" 
                  , frequency      = 0.0 #None
                  , max_duration   = 12.0 #None
                  , min_duration   = 0.0 #None
                  , time_between   = 0.0 #None
                    )
        s.save()

        # TBF: put in a dummy target so that Antioch can pick it up!
        system = first(System.objects.filter(name = "J2000"))
        target = Target(session    = s
                      , system     = system
                      , source     = "maintenance" 
                      , vertical   = 0.0
                      , horizontal = 0.0
                    )
        target.save()
        



    def create_testing_session(self, trimester):

        # create the test project w/ associated sessions.
        tooMuch = 10000.0
        semester = first(Semester.objects.filter(semester = trimester))
        ptype    = first(Project_Type.objects.filter(type = "non-science"))

        p = Project(semester     = semester
                      , project_type = ptype
                      , pcode        = "Tests"
                      , name         = "Tests" #self.filter_bad_char(row[5])
                      , thesis       = False 
                      , complete     = False 
                      , start_date   = None #datetime(2009, 6, 1, 0, 0, 0)
                      , end_date     = None #datetime(2009, 10,1, 0, 0, 0)
                        )
        p.save()
        a = Allotment(psc_time          = tooMuch
                    , total_time        = tooMuch
                    , max_semester_time = tooMuch
                    , grade             = 4.0
                      )
        a.save()
        pa = Project_Allotment(project = p, allotment = a)
        pa.save()
        p.project_allotment_set.add(pa)
        p.save()
           
        otype = first(Observing_Type.objects.filter(type = "testing"))
        stype = first(Session_Type.objects.filter(type = "fixed"))
        #project = first(Project.objects.filter(pcode = row[12]))

        allot = Allotment(psc_time          = tooMuch
                        , total_time        = tooMuch
                        , max_semester_time = tooMuch
                        , grade             = 4.0
                         )
        allot.save()
        status = Status(enabled    = True 
                      , authorized = True
                      , complete   = False
                      , backup     = False
                        )
        status.save()
        s = Sesshun(project       = p
                  , session_type   = stype
                  , observing_type = otype
                  , allotment      = allot
                  , status         = status
                  , original_id    = 999 
                  , name           = "testing"
                  , frequency      = 1.0
                  , max_duration   = tooMuch 
                  , min_duration   = 0.0 #tooMuch
                  , time_between   = 0.0 #tooMuch
                    )
        s.save()

        system = first(System.objects.filter(name = "J2000"))

        target = Target(session    = s
                              , system     = system
                              , source     = "test source"
                              , vertical   = 0.0 #float(t[4]) * (math.pi / 180)
                              , horizontal = 0.0 #float(t[5]) * (math.pi / 12)
                                )
        target.save()

            


    def transfer_fixed_periods(self, trimester):
        """
        We can dump Carl's DB into MySQL tables and use these to suck
        whatever info we need in addition to what is in the DB that
        Carl dumped to.
        Here we will take all 'scheduled dates' and replicate them
        as periods so that in the simulations they get translated
        into fixed periods that we pack around.
        """

        # Only transfer fixed periods from schedtime table that cover 
        if trimester == "09C":
            start = "20091001"
            end   = "20100201"
        else:
            raise "what trimester is that?"

        # prepare for transfering over fixed periods by creating the
        # necessary projects & session we know we'll need
        self.create_testing_session(trimester)
        self.create_maintenance_session(trimester)
        self.create_project_and_session( trimester 
                                       , "Shutdown"
                                       , "non-science"
                                       , "Shutdown"
                                       , "maintenance")
        
        times = []

        query = """
        SELECT etdate, startet, stopet, lengthet, type, pcode, vpkey
        FROM schedtime
        WHERE etdate >= %s AND etdate < %s
        ORDER BY etdate, startet
        """ % (start, end)

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            #print row

            # translate row 
            dt = row[0]
            year = int(dt[:4])
            month = int(dt[4:6])
            day = int(dt[6:])

            start_time = row[1]
            hour = int(start_time[:2])
            minutesTrue = int(start_time[2:])

            # DSS operates on hourly quarters: so minutes must be -
            # 0, 15, 30, 45
            # round down to avoid overlaps!
            if 0 <= minutesTrue and minutesTrue < 15:
                minute = 0
            elif 15 <= minutesTrue and minutesTrue < 30:
                minute = 15 
            elif 30 <= minutesTrue and minutesTrue < 45:
                minute = 30 
            else:
                minute = 45

            if minute != minutesTrue:
                print "minutes changed from %d to %d" % (minutesTrue, minute)
                print "for row: ", row

            durationHrs = float(row[3].strip())

            # DSS operates on hourly quarters: we need to truncate these
            # down to the nearest quarter to avoid overlaps
            duration = (int((durationHrs * 60) / 15) * 15 ) / 60.0

            if abs(duration - durationHrs) > 0.01:
                print "duration changed from %f to %f" % (durationHrs, duration)
                print "for row: ", row

            type = row[4].strip()
            pcode = row[5].strip()
            
            try:
                original_id = int(row[6])
            except:
                original_id = None

            # translate from ET to UT
            start = datetime(year, month, day, hour, minute) + \
                    timedelta(seconds = 4 * 60 * 60)

            testingTypes = ["Tests", "Commissioning", "Calibration"]

            # what session to link this to?
            # the vpkey CANNOT be used for Maintenance & Tests
            if type in testingTypes:
                s = first(Sesshun.objects.filter(name = "testing").all())
            elif type == "Maintenance":
                s = first(Sesshun.objects.filter(name = "Fixed Summer Maintenance").all())
            elif type == "Shutdown":
                s = first(Sesshun.objects.filter(name = "Shutdown").all())
            else: # just type == Astronomoy?
                # can we use the vpkey?
                if original_id is not None and original_id != 0:
                    s = first(Sesshun.objects.filter(original_id = original_id).all())
                elif pcode is not None and pcode != "":
                    print "Getting Session from pcode: ", pcode
                    p = first(Project.objects.filter(pcode = pcode).all())
                    s = p.sesshun_set.all()[0] # TBF: arbitrary!
                else:
                    # warn the user
                    print "Could not create session for row: "
                    print row
                    s = None

            # don't save stuff that will cause overlaps
            causesOverlap = self.findOverlap(start, duration, times)
            if s is not None:

                # check for problems
                # are we assigning fixed periods for open sessions?
                if s.session_type.type == 'open':
                    print "Session of type: ", s.session_type.type, s, start, duration
                    if duration > s.max_duration or duration < s.min_duration:
                        print "Open Session duration (%f) does not honor min/max: %f/%f"\
                            % (duration, s.min_duration, s.max_duration)
                        print s

                if causesOverlap:
                    print "Causes Overlap!: ", s, start, duration
                else:
                    #NOTE: we are no longer using windows
                    # instead, just saves these off as periods
                    p = Period(session  = s
                             , start    = start
                             , duration = duration
                             , score    = 0.0
                             , forecast = datetime.now()
                             , backup   = False)
                    p.save()         
                    #win = Window(session = s, required = True)
                    #win.save()
                    #op = Opportunity(window = win
                    #               , start_time = start
                    #               , duration = duration)
                    #op.save()
                    # keep track of this added one so we can 
                    # check for subsequent overlaps
                    times.append((s, start, duration))

    def findOverlap(self, start, dur, times):
        for time in times:
            if self.overlap(start, dur, time[1], time[2]):
                print "overlap: ", start, dur, time
                return True
        return False        

    def overlap(self, start1, dur1, start2, dur2):
        end1 = start1 + timedelta(seconds = dur1 * 60 * 60)
        end2 = start2 + timedelta(seconds = dur2 * 60 * 60)
        return start1 < end2 and start2 < end1
 


