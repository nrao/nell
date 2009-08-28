from sesshuns.models import *
from datetime        import datetime, timedelta
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
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                            )
        self.cursor = self.db.cursor()
        self.silent = silent

        # TBF: right now some of Carl's tables have been dumped
        # directly to a *separate* DB
        self.db2 = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = "dss_rcreager"
                            )
        self.cursor2 = self.db2.cursor()

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
        self.transfer_project_blackouts_09B()

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

    def transfer_project_blackouts_09B(self):
        "Only needed for scheduling 09B: project blackouts will then go away."

        query = "SELECT * from blackouts"
        self.cursor.execute(query)
        blackoutRows = self.cursor.fetchall()

        for row in blackoutRows:
            start       = row[1]
            end         = row[2]
            description = row[3]
            pkey        = row[5]
            pcodes      = row[6]

            # the people key and the pcodes must be matched to the right
            # people and projects
            query = "SELECT * FROM authors WHERE peoplekey = %d" % pkey
            self.cursor.execute(query)
            authors = self.cursor.fetchall()
            if len(authors) > 0:
                authorRow = list(authors[0])
                # we need to pop off the project id in order to be able to
                # use the create_user method
                p_id = authorRow.pop(1) 
                u = self.create_user(authorRow)
            else:
                # TBF: the fact that this is happening seems like a big
                # bug to me, but Carl just left us for a month. WTF
                #print "WARNING: peoplekey in blackouts ~ in authors: ", pkey
                u = None

            # now what different projects is this for?
            pcodeList = pcodes.split(",")
            for pcode in pcodes.split(","):
                # each project gets its own project blackout!
                p = first(Project.objects.filter(pcode = pcode.strip()))
                if p is not None:
                    pb = Project_Blackout_09B(
                        project     = p
                      , requester   = u
                      , start_date  = start
                      , end_date    = end
                      , description = description
                    )
                    pb.save()

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
                new_email.save()

        return u
            
    def filter_bad_char(self, bad):
        good = bad.replace('\xad', '')
        return good
    
    def create_09B_rcvr_schedule(self):

        rcvrChanges = []

        # the first three days of 09B
        dt = datetime(2009, 5, 30, 0)
        rcvrs = ['L', 'C', 'X', 'S', 'RRI'] # TBF: bug w/ K band!
        rcvrChanges.append((dt, rcvrs))
     
        # June 2:
        # Ku Up, K down

        # A up, K down, U up (RRI down?)
        dt = datetime(2009, 6, 4, 16)
        rcvrs = ['L', 'C', 'X', 'S', 'Ku', '1070'] # TBF: which one is A band!
        rcvrChanges.append((dt, rcvrs))

        # A down, PF1*3 up
        dt = datetime(2009, 6, 10, 16)
        rcvrs = ['L', 'C', 'X', 'S', 'Ku', '342'] # TBF: which one is PF1*3 band!
        rcvrChanges.append((dt, rcvrs))

        # S up - cancelded!  it never came down 
        #dt = datetime(2009, 6, 11, 16)
        #rcvrs = ['L', 'C', 'X', 'Ku', '342', 'S'] 
        #rcvrChanges.append((dt, rcvrs))

        # PF1*3 down, PF1*8 up
        dt = datetime(2009, 6, 15, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down, PF1*3 up
        dt = datetime(2009, 7, 6, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*3 down, PF*8 up
        dt = datetime(2009, 7, 14, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down, RRI up
        dt = datetime(2009, 7, 22, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', 'RRI'] 
        rcvrChanges.append((dt, rcvrs))

        # RRI down, PF1*8 up 
        dt = datetime(2009, 7, 28, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # A down, PF1*3 up
        dt = datetime(2009, 8, 4, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*3 down, PF1*8 up
        dt = datetime(2009, 8, 11, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down RRI up
        dt = datetime(2009, 8, 26, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', 'RRI'] 
        rcvrChanges.append((dt, rcvrs))

        # RRI down, PF1*3 up
        dt = datetime(2009, 9, 2, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Sept 8 
        # PF1*3 down, PF1*4 up
        dt = datetime(2009, 9, 8, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '450'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*4 down, PF1*8 up
        dt = datetime(2009, 9, 16, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # PF1*8 down A up
        dt = datetime(2009, 9, 28, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        for dt, rcvrs in rcvrChanges:
            for rcvr in rcvrs:
                r = first(Receiver.objects.filter(abbreviation = rcvr))
                rs = Receiver_Schedule(receiver = r, start_date = dt)
                rs.save()
                #print rs

    
    def create_09C_rcvr_schedule(self):

        rcvrChanges = []

        # First week
        dt = datetime(2009, 10, 1, 16)
        rcvrs = ['L', 'C', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        # "prelimonary[sic] receiver schedule for Oct - Jan"

        # Oct 7: C -> K
        dt = datetime(2009, 10, 7, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        # Oct 14: 1070 -> 800
        dt = datetime(2009, 10, 14, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Oct 26: 800 -> 450
        dt = datetime(2009, 10, 26, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '450'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 2: 450 -> 600
        dt = datetime(2009, 11, 2, 16)
        rcvrs = ['L', 'K', 'X', 'Ku', 'S', 'Ku', 'Hol', 'Q', '600'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 4: Ku -> MBA? (Mustang)
        dt = datetime(2009, 11, 4, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '600'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 11: 600 -> 800
        dt = datetime(2009, 11, 11, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Nov 24: 800 -> 342
        dt = datetime(2009, 11, 24, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Dec 13: 342 -> 800
        dt = datetime(2009, 12, 13, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Dec 27: 800 -> 342
        dt = datetime(2009, 12, 27, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 5: 342 -> 800
        dt = datetime(2010, 1, 5, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 6 (or Jan 21) Q-band    down, KFPA      up
        dt = datetime(2010, 1, 6, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 21 (or Feb 1) KFPA      down, Q-band    up
        dt = datetime(2010, 1, 21, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '800'] 
        rcvrChanges.append((dt, rcvrs))

        # Jan 24: 800 -> 342
        dt = datetime(2010, 1, 24, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '342'] 
        rcvrChanges.append((dt, rcvrs))

        # Feb 1: 342 -> 1070
        dt = datetime(2010, 2, 1, 16)
        rcvrs = ['L', 'K', 'X', 'MBA', 'S', 'Ku', 'Hol', 'Q', '1070'] 
        rcvrChanges.append((dt, rcvrs))

        for dt, rcvrs in rcvrChanges:
            for rcvr in rcvrs:
                r = first(Receiver.objects.filter(abbreviation = rcvr))
                rs = Receiver_Schedule(receiver = r, start_date = dt)
                rs.save()
                #print rs

    def create_maintenance_session(self, semesterName):
        """
        Creates the maintenance session, but not the date
        """

        # clean up!
        ps = Project.objects.filter(pcode = "Maintenance")
        empty = [p.delete() for p in ps]
        ss = Sesshun.objects.filter(name = "Fixed Summer Maintenance")
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
                  , name           = "Fixed Summer Maintenance" 
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
                      , source     = "maintenance" 
                      , vertical   = 0.0
                      , horizontal = 0.0
                    )
        target.save()
        
    def create_maintenance_opts(self):
        """
        Create the summer maintenance dates needed for 09B.
        These aren't being transferred by Carl, so we must create them:
        June 1 - Sep. 30: Mon - Thr, starting at 7 AM for 10.5 Hrs
        Holiday Weekends: Mon - Thr, starting at 8 AM for 8.5  Hrs
        NRAO Holidays 09: July 3, Sep 7
        There will be some fixed sessions (VLBI, Radar) that will conflict
        with these - they should be managed by hand.
        """

        s = first(Sesshun.objects.filter(name = "Fixed Summer Maintenance"))

        # now create entries in Windows and Opportunities that can be
        # translated into Periods for this fixed session

        # some maintenance days can't be scheduled normaly because of 
        # radar runs and the like
        conflicts = [ datetime(2009, 6,  9, 11) ]
                    #, datetime(2009, 6, 16, 11)
                    #]

        # what weeks have NRAO holidays in them?
        # July 3, Friday!
        holidayWeek1 = [datetime(2009, 6, 29) + timedelta(days=i) for i in range(4)]
        holidayWeek2 = [datetime(2009, 9,  7) + timedelta(days=i) for i in range(4)]
        holidayWeeks = holidayWeek1
        holidayWeeks.extend(holidayWeek2)

        # first, loop through weeks
        for week in range(22): #18):
            # then loop through Mon - Thrs
            for day in range(4): 
                # TBF: what time zone are we using?  See what happens to these
                # times when we load them up in Antioch ...
                dt = semesterStart + timedelta(days = (week*7) + day)
                # do we need to adjust for NRAO holiday?
                if dt in holidayWeeks:
                    # holiday week
                    # watch for that pesky labor day - it falls on a Monday
                    start = dt + timedelta(seconds = 12 * 60 * 60) #12 == 8 AM
                    if start == datetime(2009, 9, 7):
                        # schedule monday's on friday!
                        start = datetime(2009, 9, 11)
                    dur = 8.5 # hrs
                else:
                    # normal week
                    start = dt + timedelta(seconds = 11 * 60 * 60) #11 == 7 AM ET

                    dur = 10.5 # hrs

                # create the table entries
                # don't do this past Sep 30!
                if start <= semesterEnd:
                    if start not in conflicts:
                        w = Window( session = s, required = True)
                        w.save()
                        o = Opportunity( window     = w
                                   , start_time = start
                                   , duration   = dur
                                   )
                        o.save()               
                        # create TP's for the first two weeks!
                        if start < scheduledUpTo:
                            period = Period( session = s
                                           , start_time = start
                                           , duration = dur
                                           , backup = False )
                    else:
                        # we have conflicts!
                        if start == datetime(2009, 6, 9, 11):
                            #dt1 = start + timedelta(seconds = int(7.75 * 60 * 60))
                            dt1 = start
                            durHrs1 = 6.75
                            dt2 = start + timedelta(seconds = int(8 * 60 * 60))
                            durHrs2 = 2.5
                        #elif start == datetime(2009, 6, 16, 11): 
                        #    dt1 = start
                        #    durHrs1 = 6.00
                        #    dt2 = start + timedelta(seconds = int(7.5 * 60 * 60))
                        #    durHrs2 = 3.0 
                        else:
                            raise "SHIT!"
                        for dt, duration in [(dt1,durHrs1),(dt2,durHrs2)]:
                            w = Window( session = s, required = True)
                            w.save()
                            o = Opportunity( window     = w
                               , start_time = dt
                               , duration   = duration
                               )
                            o.save()           
                            # create TP's for the first two weeks!
                            if start < scheduledUpTo:
                                period = Period( session = s
                                           , start_time = start
                                           , duration = dur 
                                           , backup = False )




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
        print p
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

    def create_other_fixed_opts(self):

        s = first(Sesshun.objects.fitler(name = "testing").all())
        print "session: ", s

        # project, session, date time, dur (Hrs)
        # dates are in UT (+4 from ET)
        fixed = [
         ("GBT08A-073", "GBT08A-073-01", datetime(2009, 6, 1, 23, 30), 1.0)
        ,("Tests", "testing", datetime(2009, 6, 2, 0, 30), 3.5) # RRI
        ,("Tests", "testing", datetime(2009, 6, 2, 4, 0), 7.0) # Point B
        ,("Tests", "testing", datetime(2009, 6, 2, 21, 30), 1.5) # RCO U
        ,("Tests", "testing", datetime(2009, 6, 3, 4, 0), 3.5) # GUPPI
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 3, 7, 30), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 3, 21, 30), 4.0) #RRI
        ,("Tests", "testing", datetime(2009, 6, 4, 21, 30), 1.5) # RCO*A
        ,("Tests", "testing", datetime(2009, 6, 6, 12, 30), 4.0) # GUPPI
        ,("BB240", "BB240-02", datetime(2009, 6, 6, 17, 30), 8.5)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 9, 17, 45), 1.25)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 10, 7, 0), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 10, 21, 30), 1.5) # RCO*3
        ,("GBT09B-044", "GBT09B-044-01", datetime(2009, 6, 11, 5, 0), 6.0)
        ,("GBT08C-014", "GBT08C-014-01", datetime(2009, 6, 12, 6, 45), 0.75)
        ,("GBT08C-023", "GBT08C-023-01", datetime(2009, 6, 12, 7, 30), 3.75)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 13, 17, 30), 1.25)
        ,("BB240", "BB240-01", datetime(2009, 6, 14, 2, 0), 8.5)
        ,("Tests", "testing", datetime(2009, 6, 14, 13, 0), 4.0) # GUPPI
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 14, 17, 30), 1.25)
        ,("GBT08A-037", "GBT08A-037-01", datetime(2009, 6, 15, 0, 30), 4.5)
        ,("GBT09B-006", "GBT09B-006-01", datetime(2009, 6, 15, 5, 0), 1.5)
        ,("Tests", "testing", datetime(2009, 6, 15, 21, 30), 1.5) # RCO*8
        ,("GBT09B-028", "GBT09B-028-01", datetime(2009, 6, 16, 1, 30), 5.5)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 17, 4, 45), 1.75)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 17, 6, 30), 2.0)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 18, 4, 45), 1.75)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 19, 4, 45), 1.75)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 19, 18, 0), 1.25)
        ,("Tests", "testing", datetime(2009, 6, 19, 19, 15), 4.0) # GUPPI
        ,("BB240", "BB240-03", datetime(2009, 6, 20, 3, 30), 8.5)
        ,("GBT08B-025", "GBT08B-025-01", datetime(2009, 6, 20, 16, 45), 5.5)
        ,("Tests", "testing", datetime(2009, 6, 21, 4, 0), 2.0) # Q HP
        ,("GBT08C-023", "GBT08C-023-02", datetime(2009, 6, 21, 6, 0), 1.0)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 21, 17, 0), 1.0)
        ,("GBT07A-087", "GBT07A-087-01", datetime(2009, 6, 21, 21, 30), 7.5)
        ,("GBT07A-087", "GBT07A-087-02", datetime(2009, 6, 22, 21, 30), 7.5)
        ,("Tests", "testing", datetime(2009, 6, 23, 5, 0), 4.0) # M&C Integ
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 23, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 24, 0, 30), 2.5)
        ,("GBT08C-014", "GBT08C-014-01", datetime(2009, 6, 24, 5, 15), 0.75)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 24, 6, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 24, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 25, 0, 30), 2.5)
        ,("Tests", "testing", datetime(2009, 6, 25, 5, 0), 4.0) # M&C Integ
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 25, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 26, 0, 30), 2.5)
        ,("GBT09B-018", "GBT09B-018-01", datetime(2009, 6, 26, 4, 45), 1.75)
        ,("GBT08C-023", "GBT08C-023-01", datetime(2009, 6, 26, 8, 15), 3.75)
        ,("Tests", "testing", datetime(2009, 6, 26, 13, 0), 4.0) # GUPPI
        ,("BB240", "BB240-04", datetime(2009, 6, 27, 0, 30), 8.5)
        ,("Tests", "testing", datetime(2009, 6, 27, 11, 15), 6.0) # M&C Integ
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 27, 17, 15), 1.25)
        ,("BM305", "BM305-01", datetime(2009, 6, 27, 21, 15), 8.5)
        ,("GBT09B-031", "GBT09B-031-01", datetime(2009, 6, 28, 9, 0), 2.0)
        ,("GBT09B-031", "GBT09B-031-03", datetime(2009, 6, 29, 0, 30), 2.5)
        ,("Tests", "testing", datetime(2009, 6, 29, 21, 30), 4.0) # M&C Integ
        ,("GBT09B-028", "GBT09B-028-01", datetime(2009, 6, 30, 4, 0), 2.0)
        ,("GBT09B-028", "GBT09B-028-01", datetime(2009, 7, 1, 4, 0), 1.75)
        ,("GLST011217", "GLST011217-01", datetime(2009, 7, 1, 5, 45), 1.75)
        ,("Tests", "testing", datetime(2009, 7, 1, 20, 30), 3.0) # OOF
        #("Project Name", "" unless "testing", start time (UT), Len)
        ]

        for pName, sName, start, durHrs in fixed:
            #p = first(Project.objects.filter( name = pName )
            print pName, sName, start, durHrs
            s = first(Sesshun.objects.filter( name = sName ))
            print "window for session: ", s
            
            win = Window(session = s, required = True)
            win.save()
            op = Opportunity(window = win
                           , start_time = start 
                           , duration = durHrs
                           )
            op.save()
            print op

    def create_history_09B(self):
        "The first few weeks of 09B have already been scheduled."

        fixed = [
         ("GBT08A-073", "GBT08A-073-01", datetime(2009, 6, 1, 23, 30), 1.0)
        ,("Tests", "testing", datetime(2009, 6, 2, 0, 30), 3.5) # RRI
        ,("Tests", "testing", datetime(2009, 6, 2, 4, 0), 7.0) # Point B
        ,("Tests", "testing", datetime(2009, 6, 2, 21, 30), 1.5) # RCO U
        ,("Tests", "testing", datetime(2009, 6, 3, 4, 0), 3.5) # GUPPI
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 3, 7, 30), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 3, 21, 30), 4.0) #RRI
        ,("Tests", "testing", datetime(2009, 6, 4, 21, 30), 1.5) # RCO*A
        ,("Tests", "testing", datetime(2009, 6, 6, 12, 30), 4.0) # GUPPI
        ,("BB240", "BB240-02", datetime(2009, 6, 6, 17, 30), 8.5)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 9, 17, 45), 1.25)
        ,("GLST011217", "GLST011217-01", datetime(2009, 6, 10, 7, 0), 2.0)
        ,("Tests", "testing", datetime(2009, 6, 10, 21, 30), 1.5) # RCO*3
        ,("GBT09B-044", "GBT09B-044-01", datetime(2009, 6, 11, 5, 0), 6.0)
        ,("GBT08C-014", "GBT08C-014-01", datetime(2009, 6, 12, 6, 45), 0.75)
        ,("GBT08C-023", "GBT08C-023-01", datetime(2009, 6, 12, 7, 30), 3.75)
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 13, 17, 30), 1.25)
        ,("BB240", "BB240-01", datetime(2009, 6, 14, 2, 0), 8.5)
        ,("Tests", "testing", datetime(2009, 6, 14, 13, 0), 4.0) # GUPPI
        ,("GBT09B-048", "GBT09B-048-01", datetime(2009, 6, 14, 17, 30), 1.25)
        ]

        for pName, sName, start, durHrs in fixed:
            #p = first(Project.objects.filter( name = pName )
            print pName, sName, start, durHrs
            s = first(Sesshun.objects.filter( name = sName ))
            print "period for session: ", s
            p = Period( session = s
                      , start = start
                      , duration = durHrs
                      , backup = False )
            p.save()           
            

    def set_fixed_projects(self):
        "temporary fix until carl's DB gets these as fixed."

        stype    = first(Session_Type.objects.filter(type = "fixed"))
        pcodes = ["GBT09A-092"
            , "GBT09A-093"
            , "GBT09A-094"
            , "GBT09A-096"
            , "GBT07C-013"
            , "GBT09B-006"
            , "GBT09B-031"
            , "GBT09B-029"]            
        for pcode in pcodes:
            p = first(Project.objects.filter(pcode = pcode).all())
            print p
            ss = p.sesshun_set.all()
            for s in ss:
                s.session_type = stype
                s.save()

    def create_opportunities(self, start, end):
        """
        We can dump Carl's DB into MySQL tables and use these to suck
        whatever info we need in addition to what is in the DB that
        Carl dumped to.
        Here we will take all 'scheduled dates' and replicate them
        as opportunities so that in the simulations they get translated
        into fixed periods that we pack around.
        """
        times = []

        query = """
        SELECT etdate, startet, stopet, lengthet, type, pcode, vpkey
        FROM schedtime
        WHERE etdate >= %s AND etdate < %s
        ORDER BY etdate, startet
        """ % (start, end)

        self.cursor2.execute(query)
        rows = self.cursor2.fetchall()

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

            # what session to link this to?
            # the vpkey CANNOT be used for Maintenance & Tests
            if type == "Tests":
                s = first(Sesshun.objects.filter(name = "testing").all())
            elif type == "Maintenance":
                s = first(Sesshun.objects.filter(name = "Fixed Summer Maintenance").all())
            else: # just type == Astronomoy?
                # can we use the vpkey?
                if original_id is not None and original_id != 0:
                    s = first(Sesshun.objects.filter(original_id = original_id).all())
                elif pcode is not None and pcode != "":
                    print "Getting Session from pcode: ", pcode
                    p = first(Project.objects.filter(pcode = pcode).all())
                    s = p.sesshun_set.all()[0] # TBF: arbitrary!
                else:
                    s = None

            # save this as a fixed period to the opts table
            #print s, start, duration

            # don't save stuff that will cause overlaps
            causesOverlap = self.findOverlap(start, duration, times)
            if s is not None and causesOverlap:
                print "Causes Overlap!: ", s, start, duration

            if s is not None and not causesOverlap:
                win = Window(session = s, required = True)
                win.save()
                op = Opportunity(window = win
                               , start_time = start
                               , duration = duration)
                op.save()
                #print "op: ", op
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
 
    def create_09B_database(self):
        self.transfer()
        self.create_09B_conditions()

    def create_09B_conditions(self):
        trimester = "09B"
        self.create_testing_session(trimester)
        self.create_maintenance_session(trimester)
        self.create_09B_rcvr_schedule()
        #self.create_other_fixed_periods()
        self.set_fixed_projects()
        start = "20090601"
        end   = "20091001"
        self.create_opportunities(start, end)

    def create_09C_database(self):
        self.transfer()
        self.create_09C_conditions()

    def create_09C_conditions(self):
        trimester = "09C"
        self.create_testing_session(trimester)
        self.create_maintenance_session(trimester)
        self.create_09C_rcvr_schedule()
        start = "20091001"
        end   = "20100201"
        self.create_opportunities(start, end)

