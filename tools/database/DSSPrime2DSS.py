# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from datetime                          import datetime, timedelta
from DBReporter                        import DBReporter
from nell.scheduler.models             import *
import math
import MySQLdb as m

def safeUnicode(string):
    try:
        uni = unicode(string)
    except UnicodeDecodeError:
        if len(string) == 1:
            uni = ''
        else:
            uni = ''.join([safeUnicode(s) for s in string])
    return uni

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

        # How are we to handle transferring windows?
        # Currently this code supports two ways of transferring window
        # info from DSSPrime; but the 'windows' table doesn't seem to
        # get used anymore.  Thus the default below is False.  
        # However, we need to resolve this.
        # Story: https://www.pivotaltracker.com/story/show/14428941
        self.use_transferred_windows = False

        # for gathering information during the transfer
        self.new_projects = []
        self.old_projects = []

        self.new_sessions = []
        self.old_sessions = []

        self.new_users = []
        self.old_users = []

        self.user_matches = []

        self.quiet = False

    def __del__(self):
        self.cursor.close()

    def check_db(self):
        "Assorted checks on dss_prime to look for problems"

        # look for redundant pcodes
        query = "SELECT pcode FROM projects"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        pcodes = []
        redundants = []
        for r in rows:
            pcode = r[0]
            if pcode not in pcodes:
                pcodes.append(pcode)
            else:
                redundants.append(pcode)
        if len(redundants) != 0:
            print "ERROR: Redundant project codes!!!"
            print "    pcodes: ", len(pcodes)
            print "    redundants: "
            for p in redundants:
                print "    ", p

        # what else?

    def transfer(self):
        """
        This top-level function transfers ALL information into a DSS DB
        that is assumed to be pristine.
        """
        self.transfer_friends()
        self.transfer_projects()
        self.transfer_authors()
        self.transfer_sessions()
        self.normalize_investigators()
        self.set_sanctioned_flags()

    def transfer_only_new(self):
        """
        This top-level function transfers only information for projects
        that are not yet in the DSS DB.
        """

        # this method uses self.create_user, which checks for person
        # pre-existence, so it is safe to call here
        self.transfer_friends()

        self.transfer_new_projects()

        # now that we've transferred over the new projects, we
        # can import info only that pertains to those new projects
        self.transfer_new_proj_authors(self.new_projects)
        self.transfer_new_proj_sessions(self.new_projects)

        # keep a record of what you did
        self.report_transfer_only_new()

        # also print out the mimic of carl's report
        dbr = DBReporter(filename = "DBReport.txt", quiet = self.quiet)
        dbr.reportProjectSummaryByPcode(self.new_projects)

    def set_sanctioned_flags(self):
        # Get the list of sanctioned users 
        f = open("/home/dss/data/sanctioned_users.txt", "r")
        sanctioned = []
        for line in f:
            first, x = line.split(',')
            last = x.rstrip('\n')
            sanctioned.append((first, last))

        # Set sanctioned flag in the database if both last names match
        for s in sanctioned:
            users = User.objects.all()
            succeed = False
            for u in users:
                if s[1] == u.last_name:
                    if s[0] == u.first_name:
                        u.sanctioned = True
                        u.save()
                        succeed = True
                        break
            # Print differences if last name matches, but not first
            if not succeed:
                for u in users:
                    if s[1] == u.last_name:
                        if s[0] != u.first_name:
                            if not self.quiet:
                                print "Is 08B sanctioned user %s %s possibly the same as 09C user %s %s?" % (s[0], s[1], u.first_name, u.last_name)

    def get_sessions(self, pcode = None):

        # are we getting just sessions from the given pcode, or all sessions?
        if pcode is None:
            where_clause = ""
        else:
            where_clause = "WHERE projects.pcode = '%s'" % pcode

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
                %s
                ORDER BY sessions.id
                """ % where_clause
        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        if pcode is None:
            # Just run a quick query to check that we got all the sessions
            self.cursor.execute("SELECT id FROM sessions %s" % where_clause)
            results = self.cursor.fetchall()
            assert len(results) == len(rows)

        return rows

    def transfer_sessions(self):
        "for backwards compatibility"
        self.transfer_all_sessions()

    def transfer_all_sessions(self):
        """
        Transfers all sessions encountered.
        """

        rows = self.get_sessions()
        for row in rows:
            self.add_session(row)

    def transfer_new_proj_sessions(self, pcodes):
        """
        Transfers over only those sessions that belong to the given projects.
        """

        for pcode in pcodes:
            rows = self.get_sessions(pcode)
            for row in rows:
                self.add_session(row)

    def add_session(self, row):
        """
        Adds a new session to the DB using the given information.
        Note: the given info is in the form of raw sql results, derived
        from the sql used in get_session().
        """
        otype = Observing_Type.objects.get(type = row[23])
        stype = Session_Type.objects.get(type = row[24])
        project = Project.objects.get(pcode = row[12])

        if project is None:
            print "*********Transfer Sessions Error: no project for pcode: ", row[12]
            return

        allot = Allotment(psc_time          = float(row[14])
                        , total_time        = float(row[15])
                        , max_semester_time = float(row[16])
                        , grade             = float(row[17])
                          )
        allot.save()

        # For now, make sure all new sessions are not enabled/authorized
        status = Status(enabled    = False #row[19] == 1
                      , authorized = False #row[20] == 1
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
        system = System.objects.get(name = "J2000")

        # The DSS database now enforces only one target per session.
        # however this code exists so we can run unit tests w/ DB's
        # where this was not enforced.
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            #if len(rows) > 1:
            #    print "Too many target rows for session: ", s_id_prime
            t = rows[0]
        else:
            t = None

        if t is not None:
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
                rcvr = Receiver.objects.get(name = r_name[0])
                rg.receivers.add(rcvr)
            rg.save()

        self.add_backends(s)

        # now get the observing parameters
        query = """SELECT op.string_value, op.integer_value, op.float_value,
                          op.boolean_value, op.datetime_value, parameters.name
                   FROM observing_parameters as op, parameters
                   WHERE session_id = %s and parameters.id = op.parameter_id
                """ % s_id_prime
        self.cursor.execute(query)

        # key: o[0] = string_value
        #      o[1] = integer_value
        #      o[2] = float_value
        #      o[3] = boolean_value
        #      o[4] = datetime_value
        #      o[5] = parameters.name

        for o in self.cursor.fetchall():
            # we have started to diverge from Carl's original set of
            # observing parameters, to our new DSS ones.
            param_name = o[5]
            if param_name == "Night-time Flag":
                # this has been replaced w/ "Time of Day"
                p = Parameter.objects.get(name = "Time Of Day")
                # Time Of Day is now an enumeration, of which, Carl's
                # 'Night-time Flag' maps to the RfiNight choice.
                o = ("RfiNight", None, None, None, None, 'Time Of Day')
            else:    
                p  = Parameter.objects.get(name = param_name)
            if p.name == 'Instruments' and o[0] == "None":
                #print "Not passing over Observing Parameter = Instruments(None)"
                pass
            else:
                op = Observing_Parameter(
                session        = s
              , parameter      = p
              , string_value   = o[0] if o[0] is not None else None
              , integer_value  = o[1] if o[1] is not None else None
              , float_value    = float(o[2]) if o[2] is not None else None
              , boolean_value  = o[3] == 1 if o[3] is not None else None
              , datetime_value = o[4] if o[4] is not None else None
            )
                op.save()

        # now create windows from cadences
        self.create_windows(s, s_id_prime)

        self.new_sessions.append(s)

    def add_backends(self, s):
        # now get the backends
        bg = Backend_Group(session = s)
        bg.save()
        query = "SELECT backends from dispositions where pcode = '%s'" % s.project.pcode
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result is not None:
            for b in result[0]:
                backend = Backend.objects.filter(rc_code = b)[0]
                bg.backends.add(backend)
            bg.save()

    def normalize_investigators(self):
        for p in Project.objects.all():
            p.normalize_investigators()

    def transfer_authors(self):

        query = "SELECT * FROM authors"
        self.cursor.execute(query)

        rows = self.cursor.fetchall()
        for row in rows:
            self.add_author(row)

    def transfer_new_proj_authors(self, pcodes):
        """
        Transfers users/investigators only for those given projects.
        """

        for pcode in pcodes:
            # get the project id for this pcode
            query = "SELECT id FROM projects WHERE pcode = '%s'" % pcode
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            pid = rows[0][0]

            # now get the authors for this project
            query = "SELECT * from authors WHERE project_id = %d" % pid
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            for row in rows:
                self.add_author(row)

    def add_author(self, row):
        """
        Creates a User object if need be, then creates an Investigator
        object to linke this User and it's Project.
        """

        row  = list(row)
        p_id = row.pop(1)
        # get the user
        u    = self.create_user(row)

        # get the project
        query = "SELECT pcode FROM projects WHERE id = %s" % p_id
        self.cursor.execute(query)
        pcode = self.cursor.fetchone()[0]
        p     = Project.objects.get(pcode = pcode)

        if p is None:
            print "*****ERROR: project absent for pcode: ", pcode
            return

        # create the Investigator relation w/ the project & user
        i, _ = Investigator.objects.get_or_create(project=p, user=u)
        if i:
            i.principal_contact      = row[6] == 1
            i.principal_investigator = row[5] == 1
        i.save()

    def transfer_projects(self):
        "maintains old interface"
        self.transfer_all_projects()

    def get_all_pushed_projects(self):
        """
        Query the DB for ALL the projects that have been pushed there,
        and return the raw query result
        """

        query = """
                SELECT *
                FROM projects
                INNER JOIN (semesters, project_types)
                ON projects.semester_id = semesters.id AND
                   projects.project_type_id = project_types.id
                """
        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        return rows

    def transfer_all_projects(self):
        "Get 'em all, transfer 'em all."

        # to be used when initializing a new DB
        rows = self.get_all_pushed_projects()
        for row in rows:
            self.add_project(row)

    def transfer_new_projects(self):
        "Get 'em all, but only tranfer the ones we don't have yet."

        # to be use when making incremental updates
        rows = self.get_all_pushed_projects()
        for row in rows:
            # check pcode - if we have it, don't transfer it.
            pcode = row[4]
            try:
                p = Project.objects.get(pcode = pcode)
            except Project.DoesNotExist:
                self.add_project(row)
                self.new_projects.append(pcode)
            else:
                self.old_projects.append(pcode)

    def add_project(self, row):
        """
        Adds a new project to the DB based off the given list of values.
        Note: these values are the raw result of a DB query.
        Note: assumes all friends are in DSS DB already.
        """

        # first the project
        semester = Semester.objects.get(semester = row[12])
        ptype    = Project_Type.objects.get(type = row[14])
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

        self.add_disposition(p)

        # then the related objects:
        # friends: friend_id from DSS' projects table
        f_id = row[3]
        if f_id != 0:
            query = "select * from friends where id = %s" % f_id
            self.cursor.execute(query)
            friend_row = self.cursor.fetchone()
            friendUser = self.find_user(friend_row)
            friend = Friend(user = friendUser, project = p)
            friend.save()


        # allotments:
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
            self.add_project_allotment(p, row)

    def add_disposition(self, p):
        # Get project's disposition
        query = "SELECT disposition, abstract from dispositions where pcode = '%s'" % p.pcode
        self.cursor.execute(query)
        dis = self.cursor.fetchone()

        if dis is not None:
            p.disposition = safeUnicode(dis[0])
            p.abstract    = safeUnicode(dis[1])
            p.save()

    def add_project_allotment(self, project, row):
        """
        Add to the DSS DB the allotments for the given project.
        The given allotment information is the raw result of a
        DB query.
        """

        try:
            psc, total, max_sem, grade = map(float, row[2:])
        except TypeError:
            if not self.silent:
                print "No alloment for project", project.pcode
        else:
            a = Allotment(psc_time          = psc
                        , total_time        = total
                        , max_semester_time = max_sem
                        , grade             = grade
                          )
            a.save()

            pa = Project_Allotment(project = project, allotment = a)
            pa.save()

    def transfer_friends(self):

        query = "SELECT * FROM friends"
        self.cursor.execute(query)

        for row in self.cursor.fetchall():
            _   = self.create_user(row)

    def find_user(self, row):
        """
        Given a row of user info (first, last name, original id, emails),
        can we find this user in the production DB?
        First try to match the original id, then use the rest of the
        info.
        NOTE: originally, we were only using the original id, and were
        thus creating lots of new entries for users that were already
        in the system.  The addition of the other checks has greatly
        reduced this problem, but matching users between DSS and
        Carls system is still a pain.
        """

        # parse the user info first
        # we must support outrageous accents
        try:
            firstName = unicode(row[1])
        except:
            firstName = "exception"

        try:
            lastName = unicode(row[2])
        except:
            lastName = "exception"

        original_id = int(row[3])
        emails = [e.replace('\xad', '') for e in row[4].split(',')]

        # Check to see if the user is already in the system
        # Step 1: use the original id
        try:
            user = User.objects.get(original_id = int(row[3]))
        except User.DoesNotExist:
            user = None
        # make sure we at least have the same last name
        if user is not None and user.last_name == lastName:
            return user

        # Step 2: still no match? look for users w/ same last name
        others = User.objects.filter(last_name = lastName)
        #others = [o for o in othersMaybe if o.id != u.id]
        if len(others) == 0:
           # sorry, no candidates found
           return None
        # Step 3: for same last name, look for email OR first name match
        match = False
        for o in others:
            info = o.getStaticContactInfo()
            otherEmails = info['emails']
            for existingEmail in otherEmails:
                for e in emails:
                    if e.strip() == existingEmail.strip():
                        match = True
            # check for first name match
            if o.first_name == firstName:
                match = True
            if match:
                return o
                        
        # if we've gotten this far, none of the users that share the 
        # same last name provide a clear match
        return None



    def create_user(self, row):

        
        # Check to see if the user is already in the system
        #user = User.objects.filter(original_id = int(row[3]))[0]
        user = self.find_user(row)

        # Skip to the next user if this one has been found
        if user is not None:
            # for reporting
            if (row, user) not in self.user_matches:
                self.user_matches.append((row, user))    
            if user not in self.old_users and user not in self.new_users:
                self.old_users.append(user)
            # skip to the next one    
            row = self.cursor.fetchone()
            return user

        try:
            firstName = unicode(row[1])
        except:
            firstName = "exception"

        try:
            lastName = unicode(row[2])
        except:
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
                 )
        u.save()

        # for reporting
        self.new_users.append(u)

        return u

    def filter_bad_char(self, bad):
        good = bad.replace('\xad', '')
        return good

    def report_transfer_only_new(self):
        """
        Presents information gathered during transfer process.
        Right now this is tailer made for 'transfer_only_new'
        """

        # lines to print
        ls = ""

        # review
        ls += "Transfered %d new projects and ignored %d old\n" % \
            (len(self.new_projects), len(self.old_projects))

        ls += "Transfered %d new sessions and ignored %d old\n" % \
            (len(self.new_sessions), len(self.old_sessions))

        ls += "Transfered %d new users and ignored %d old\n" % \
            (len(self.new_users), len(self.old_users))


        # project level details
        for pcode in self.new_projects:
            ls += "\nProject: \n"
            project = Project.objects.get(pcode = pcode)
            ls += "%s\n" % project
            ls += "Friends: %s\n" % ",".join([f.user.name() for f in project.friend_set.all()])
            ls += "Users:\n"
            for inv in project.investigator_set.all():
                new = inv.user in self.new_users
                ls += "    new: %s, %s\n" % (new, inv.user)
            ls += "Sessions:\n"
            for s in project.sesshun_set.all():
                ls += "    %s\n" % s

        ls += "\nMatched User Info: %d\n" % len(self.user_matches)
        for r, u in self.user_matches:
            try:
                ls += "    Row: %s, %s, %s, %s Matched to User: %s, %d, %s\n" % (r[1], r[2], r[3], r[4], u, u.original_id, u.getEmails()) 
            except:
                ls += "Exception in reporting\n"

        ls += "\nNew Users Added: %d\n" % len(self.new_users)
        for new in self.new_users:
            ls += "    %s\n" % new
           
        # report on any problems reading names of these users   
        outrageousAccents = [u for u in self.new_users \
            if u.last_name == "exception" or u.first_name == "exception"]
        if len(outrageousAccents) > 0:
            ls += "\nNew Users whos names could not be read:\n"
            for u in outrageousAccents:
                ls += "    %s\n" % u

        if not self.quiet:
            print ls

        f = open("DSSPrime2DSS_report.txt", 'w')
        f.writelines(ls)
        f.close()

    def transfer_only_windows(self, ignore_cmp = True, ignore_before = None):
        """
        This method is for 'back filling' the windows - the case where we've
        already transfered project info, but didn't grab the cadence info; i.e.
        this is to be called by itself.
        """

        # get all the sessions that have cadences
        query = "SELECT session_id FROM cadences"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        ids = [int(r[0]) for r in rows]

        # for each pair of sesshun and it's dss_prime PK, create it's windows
        for session_dss_prime_id in ids:
            # which session in DSS does this refer to?
            query = "SELECT original_id FROM sessions WHERE id = %d" \
                % (session_dss_prime_id)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            assert len(rows) == 1
            original_id = int(rows[0][0])
            # get our DSS session
            sesshun = Sesshun.objects.get(original_id = original_id)
            # finally, transfer the windows
            if sesshun is not None:
                self.create_windows(sesshun
                                  , session_dss_prime_id
                                  , ignore_cmp
                                  , ignore_before)

    def create_windows(self
                     , sesshun
                     , session_dss_prime_id
                     , ignore_cmp = True
                     , ignore_before = None):

        # 1. skip this step if the session is completed (no point!)
        if ignore_cmp and sesshun.status.complete:
            return # no point - who cares

        rows = self.get_cadence(session_dss_prime_id)

        # Note: really should only be one per session
        for row in rows:
            windows = self.cadence2windows(row)
            for wstart, dur in windows:
                # 2. don't add windows that end before we care (no point!)
                if ignore_before is not None:
                    if w.last_date() < ignore_before: # start of 10A
                        #w.delete() # no point
                        pass
                        # we don't need to delete them because they haven't
                        # been saved yet!
                    else:
                        w = Window(session = sesshun)
                        w.save()
                        wr = WindowRange(window = w
                                       , start_date = wstart
                                       , duration = dur)
                        wr.save()               
                else:
                    w = Window(session = sesshun)
                    w.save()
                    wr = WindowRange(window = w
                                   , start_date = wstart
                                   , duration = dur)
                    wr.save()               
                # NOTE: we can't do this yet, because we don't have
                # the periods yet.  That comes later, outside of this class
                # now we have to match up the correct periods to the windows
                #self.assign_periods_to_window(w)


    def get_cadence(self, session_id):

        query = """
        SELECT session_id, start_date, repeats, full_size, intervals
        FROM cadences WHERE session_id = %d
        """ % session_id
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def string2int_list(self, string_value, length):
        if string_value.find(',') == -1:
            # scalar intervals - regular!
            values = [int(string_value)] * length
        else:
            # vector intervals - irregular! ex: '1,2,1,5'
            values = string_value.strip().split(',')
            values = [int(v) for v in values]
            if len(values) != length:
                print "length vs. values off ", string_value, length, values
        return values

    def cadence2windows(self, row):
        """
        Converts a row from the cadence table to a window object, but
        does NOT assign the session nor the default_period.
        """
        windows = []

        # row needs to conform to: session_id, start, repeats, full_size, interval

        # convert this ET time that is supposed to represent a UT date
        # i.e. 2009-10-2 19:00:00 => 2009-10-3
        #starttime = datetime.strftime(row[1], "%Y-%m-%d %H:%M:%S")
        starttime = row[1]
        start = (starttime + timedelta(days = 1)).date() if starttime is not None else None
        repeats = int(row[2])
        full_sizes = self.string2int_list(row[3], repeats)
        # the precence of full_size values of 0 means these are 0-based
        # but we want a one day window to have a duration of 1 day.
        full_sizes = [f+1 for f in full_sizes]
        intervals = self.string2int_list(row[4], repeats)

        # avoid nulls
        if start is None or repeats is None or full_sizes is None or intervals is None:
            windows = []
        else:
            for i in range(repeats):
                # but Jules is actually treating the start date as
                # the midpoint of the window!  so adjust it!
                wstart = start - timedelta(days = (full_sizes[i]/2))
                windows.append((wstart, full_sizes[i]))
                start += timedelta(days = intervals[i])

        return windows
