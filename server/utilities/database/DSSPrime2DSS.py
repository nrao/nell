from sesshuns.models import *
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

    def __del__(self):
        self.cursor.close()

    def transfer(self):
        self.transfer_friends()
        self.transfer_projects()
        self.transfer_authors()
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

            s_id_prime = row[0]
            query = """
                    SELECT *
                    FROM targets
                    WHERE session_id = %s
                    """ % s_id_prime
            self.cursor.execute(query)

            # System not set in DBase export!
            system = first(System.objects.filter(name = "J2000"))
            for t in self.cursor.fetchall():
                target = Target(session    = s
                              , system     = system
                              , source     = t[3]
                              , vertical   = float(t[4])
                              , horizontal = float(t[5])
                                )
                target.save()

            query = "SELECT * FROM cadences WHERE session_id = %s" % s_id_prime
            self.cursor.execute(query)

            for c in self.cursor.fetchall():
                cad = Cadence(session = s
                            , start_date = c[2]
                            , end_date   = c[3]
                            , repeats    = c[4]
                            , intervals  = c[5]
                              )
                cad.save()

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

            i = Investigators(project = p
                            , user    = u
                            , principal_contact = row[5] == 1
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
                      , ignore_grade = row[8] == 1
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
                    p.allotments.add(a)

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
            
        u = User(original_id = int(row[3])
               , sancioned   = False
               , first_name  = row[1]
               , last_name   = row[2]
                 )
        u.save()

        for e in row[4].split(','):
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
    
