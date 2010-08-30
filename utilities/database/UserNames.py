from sesshuns.models    import *
from datetime           import datetime, timedelta
import math
import MySQLdb as m
import logging, urllib2
from nell.utilities     import NRAOUserDB, UserInfo
import lxml.etree as ET

class UserNames(object):

    """
    This class is simply a collection of different methods for managing
    issues related to usernames and IDs.
    """

    def __init__(self, output_file = None):
        if output_file == None:
            self.out = sys.stdout
        else:
            self.out = output_file
            
    def findMissingUsers(self, files = None):
        "Interactive method that uses XML dump to find missing users."

        users = User.objects.filter(pst_id = None).all()
        print >> self.out, "num missing users to find: ", len(users) 
        print >> self.out, ""
        
        infos = self.loadUserInfoFromDump(files)
        print >> self.out, "loaded user xml dump"

        for user in users:
            print >> self.out, "looking for user: ", user
            print >> self.out, ""
            self.findUser(user.last_name, infos)
            id = raw_input("What id to use: ")
            username = raw_input("What username to use: ")
            try:
                user.pst_id = int(id)
                user.username = username
            except:
                user.pst_id = None
                user.username = None
            user.save()
            print >> self.out, ""


            
    def loadUserInfoFromDump(self, files = None):
        "Uses a textual xml dump of PST to assign usernames/ids"
        if files is None:
            files = ["nrao.xml"]
        users = []
        for f in files:        
            parsed = ET.parse(f)
            elements = parsed.getroot()
            for element in elements:
                users.append(UserInfo().parseUserXML(element))
        return users

    def findUser(self, last_name, users):

        for user in users:
           userInfo = UserInfo().parseUserDict(user)
           if user['name']['last-name'] == last_name:
               first_name = user['name']['last-name']
               last       = user['name']['first-name']
               username = user['account-info']['account-name']
               id       = user['id']
               print >> self.out, "Found user of name: %s %s" % (first_name, last)
               print >> self.out, "Emails: ", userInfo['emails']
               print >> self.out, "username: %s, ID: %s" % (username, id)
               print >> self.out, ""
               

    def confirmUserInfo(self):
        "Checks contents of User table against info from PST service w/ pst ID."

        users = User.objects.all()

        # keep records
        noPstId = []
        matched = []
        mismatched = []
        badIds = []
        badUsernames = []

        for u in users:
            if u.pst_id is not None:
                info = UserInfo().getStaticContactInfoByID(u.pst_id
                                                         , use_cache = False)
            
                # extract what the PST thinks about this user
                pstId        = int(info['id'])
                pstUsername  = info['account-info']['account-name'].strip()
                pstFirstName = info['name']['first-name'].strip()
                pstLastName  = info['name']['last-name'].strip()

                if (pstId != u.pst_id):
                    badIds.append((u, u.pst_id, pstId))
                if (pstUsername != u.username):
                    badUsernames.append((u, u.username, pstUsername))
                # just check for names
                #if pstId != u.pst_id or pstUsername != u.username or \
                if pstFirstName != u.first_name or \
                   pstLastName != u.last_name:
                    print >> self.out, "PST: %s %s vs. DSS: %s %s" % (pstFirstName
                                                       , pstLastName
                                                       , u.first_name
                                                       , u.last_name)
                    mismatched.append(u)
                else:
                    matched.append(u)
            else:
                noPstId.append(u)

        print >> self.out, "badIds: "
        for b in badIds:
            print >> self.out, b

        print >> self.out, "badUsernames: "
        for b in badUsernames:
            print >> self.out, b

        # report
        print >> self.out, "len(users): ", len(users)
        print >> self.out, "len(noPstId): ", len(noPstId)
        print >> self.out, "len(matched): ", len(matched)
        print >> self.out, "len(mismatched): ", len(mismatched)
        print >> self.out, "len(badIds): ", len(badIds)
        print >> self.out, "len(badUsernames): ", len(badUsernames)

    def transferUserNamesByOriginalID(self):
        """
        What if you already have a DB that already has usernames & IDs 
        correctly reconciled?  Use this script to transfer that information
        to the settings.py DB.
        NOTE: simply using an SQL dump to transfer the User table from one
        DB to the other might be risky, since 
        users are linked by primary key to projects, etc.
        """

        # reading from another Postgres DB is a pain, so just read in 
        # a text dump of the sanctioned table
        filename = "utilities/database/user_table.txt"
        f = open(filename, 'r')
        lines = f.readlines()

        # keep some records
        matched = []
        mismatched = []
        missing = []

        observer = first(Role.objects.filter(role = "Observer"))

        for line in lines:
            parts = line.split('\t')
            # columns: (id, original_id, pst_id, username, sanctioned, 
            # first_name, last_name, contact_instructions, role_id) 
            original_id = int(parts[1])
            pst_id      = int(parts[2])
            username    = parts[3]
            first_name  = parts[5]
            last_name   = parts[6]
            # use the original id to map
            ourUser = first(User.objects.filter(original_id=original_id).all())
            # does this make sense?
            if ourUser is None:
                print >> self.out, "missing user: ", line
                ourUser = User(
                    original_id = original_id
                  , pst_id      = pst_id
                  , username    = username
                    #, sanctioned  = models.BooleanField(default = False)
                  , first_name  = first_name
                  , last_name   = last_name
                    #, contact_instructions = models.TextField(null = True)
                    , role                 = observer
                               )
                ourUser.save()
                missing.append((ourUser, first_name, last_name))   
                continue
            elif first_name != ourUser.first_name or \
               last_name != ourUser.last_name:
                print >> self.out, "mismatch: ", ourUser, first_name, last_name
                mismatched.append((ourUser, first_name, last_name))   
                ourUser.first_name = first_name
                ourUser.last_name = last_name
            # pass over the usernames and ids:
            matched.append(ourUser)
            ourUser.username = username
            ourUser.pst_id   = pst_id
            ourUser.save()
    
        print >> self.out, "mismatched: ", mismatched
        print >> self.out, "missing: ", missing
        print >> self.out, "len(mismatched): ", len(mismatched)
        print >> self.out, "len(matched): ", len(matched)
        print >> self.out, "len(missing): ", len(missing)
        print >> self.out, "len(ourUsers): ", len(User.objects.all())

    def getUserNamesFromIDs(self):

        # get rid of this banner once other print statements are gone
        print >> self.out, "********** Retrieving usernames using PST IDs. *********"

        noUsernames = User.objects.filter(username = None).all()
        print >> self.out, "num w/ no username  now : ", len(noUsernames)

        # get all users
        users = User.objects.all()

        missing = []
        saved = []
        agree = []

        # for each user, get their static contact info
        for user in users:

            id = user.pst_id

            if id is None:
                print >> self.out, "skipping user, no pst_id: ", user
                missing.append(user)
                continue

            # save off the username
            #print "getting id for: ", user, id
            ##<<<<<<< local
            #info = UserInfo().getStaticContactInfoByID(id, use_cache = False)
            #print info
            #username = info['account-info']['account-name']
            #=======
            info = user.getStaticContactInfo(use_cache = False) #UserInfo().getStaticContactInfoByID(id)
            print >> self.out, id, info
            username = info['username'] #info['account-info']['account-name']getStaticContactInfo

            if user.username is not None:
                if user.username == username:
                    #no-op
                    #print "usernames agree for: ", user
                    agree.append(user)
                else:
                    usernameStr = username if username is not None else ""
                    print >> self.out, "user.username != username! " + user.username + "!=" + usernameStr
            else:
                saved.append(user)
                #print "saving username: ", user, username
                user.username = username
                user.save()
        
        print >> self.out, "saved: ", saved
        print >> self.out, "missing: ", missing

        print >> self.out, "num agreed: ", len(agree)
        print >> self.out, "num saved: ", len(saved)
        print >> self.out, "num no pst_id: ", len(missing)

        noUsernames = User.objects.filter(username = None).all()
        print >> self.out, "num w/ no username still : ", len(noUsernames)

    def assignUserNames(self, username, password):
        "Where we can, get usernames for those users who don't have 'em"

        # We will query PST using last name where we can.

        ui = UserInfo()

        # use service to get all users with this last name
        #url = 'https://mirror.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
        url = 'https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
        #udb = NRAOUserDB.NRAOUserDB( \
        udb = NRAOUserDB( \
            url
          , username
          , password
          , opener=urllib2.build_opener())

        key = 'usersByLastNameLike'

        users = self.getUsersUniqueByLastName()

        missing = [u for u in users if (u.pst_id is None and u.username is None)] 

        print "num missing users: ", len(missing)

        self.match = []
        self.noMatch = []
        self.duplicates = []

        for user in missing:
            print user
            if user.last_name in ['Ivanova', 'Jone']:
                continue

            if "'" in user.last_name:
                print >> self.out, "SKIP: ", user
                continue             

            el = udb.get_data(key, user.last_name)
            #print >> self.out, ET.tostring(el, pretty_print=True)

            #print "parsing xMl:"
            infos = []
            xmlUsers = el.getchildren()
            print "xmlUsers: ", xmlUsers
            for xmli in range(len(xmlUsers)):
                e = xmlUsers[xmli]
                print e
                info = ui.parseUserXMLWorker(e)

                print xmli
                print info
                first_name = info['name']['first-name']
                username = info['account-info']['account-name']
                id = int(info['id'])

                infos.append((first_name, username, id))


            matchingInfo = [i for i in infos if i[0] == user.first_name]

            #if first_name == user.first_name:
            if len(matchingInfo) == 1:
                print "got for user: ", user, username, id
                user.username = username
                user.pst_id = id
                user.save()
                self.match.append((user, username, id))
            elif len(matchingInfo) > 1:
                print "duplicate PST entry", user
                self.duplicates.append((user, matchingInfo))
            else:
                print "no match!", user
                self.noMatch.append((user, infos))



        print "matches: ", len(self.match)
        for u, un, id in self.match:
            print u, un, id
        print "no matches: ", len(self.noMatch)
        for u, i in self.noMatch:
            print u, i
        print "duplicates: ", len(self.duplicates)
        for u, i in self.duplicates:
            print u, i

        users = self.getUsersUniqueByLastName()
        missing = [u for u in users if (u.pst_id is None and u.username is None)] 
        print "NOW num missing users: ", len(missing)


    def getUserNames(self, username, password):
        "DEPRECATED: but may be useful for testing query services"

        #ui = UserInfo.UserInfo()
        ui = UserInfo()

        skipping = []

        # use service to get all users with this last name
        #url = 'https://mirror.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
        url = 'https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
        #udb = NRAOUserDB.NRAOUserDB( \
        udb = NRAOUserDB( \
            url
          , username
          , password
          , opener=urllib2.build_opener())

        key = 'usersByLastNameLike'

        users = self.getUsersUniqueByLastName()

        #users =  User.objects.all()
        for user in users:

            # users not in PST
            if user.last_name in ['Ivanova']:
                continue

            if user.pst_id is not None:
                print >> self.out, "users has pst_id: ", user
                continue

            print >> self.out, user.last_name

            if "'" in user.last_name:
                skipping.append(user)
                print >> self.out, "SKIP: ", user
                continue

            el = udb.get_data(key, user.last_name)
            print >> self.out, ET.tostring(el, pretty_print=True)

            print "parsing xMl:"
            print ui.parseUserXML(el)
            
            #els = el.getchildren()
            #assert len(els) == 1
            #el = els[0]

            #items = el.items()
            #id = [int(i[1]) for i in items if i[0] == 'id'][0]
            #print >> self.out, "pst_id: ", id

            # name
            #first_name  = el[0][1].text
            #middle_name = el[0][2].text
            #last_name   = el[0][3].text
            #assert (last_name == user.last_name)

            # account name
            #accountName = el[4][0].text

            # pst id

            # save it off!
            #user.username = accountName
            #print >> self.out, accountName
        
        print >> self.out, "skipped: ", skipping

    def getUsersUniqueByLastName(self):
        
        users = User.objects.all()
        uniques = []
        notUniques = []

        for user in users:
            sameLastName = User.objects.filter(last_name = user.last_name).all()
            if len(sameLastName) == 1:
                uniques.append(user)
            else:
                notUniques.append(user)
        
        print >> self.out, "num Users that share the same last name: "
        print >> self.out, len(notUniques)
        print >> self.out, "out of a total of: " 
        print >> self.out, len(users)

        return uniques

    def addNewUsersFromProject(self, pcode, username, password):
        """
        Here, for the given project code, get it's authors list, and simply
        create the basic User entries for these authors.
        """

        ps = Project.objects.filter(pcode = pcode)
        assert len(ps) == 1
        p = ps[0]

        url = "https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm"
        udb = NRAOUserDB( \
            url  
          , username
          , password
          , opener=urllib2.build_opener())

        key = 'authorsByProposalId'

        id = "%s/%s" % (p.pcode[:3], p.pcode[3:])

        el = udb.get_data(key, id)

        subel = el.getchildren()
        authors = subel[0].getchildren()
        numAuthors = len(authors)

        # for each author, try to use the info we got
        for i in range(numAuthors):
            # get an author
            a = authors[i]
            # get it's info
            last_name  = self.findTag(a, "last_name")
            first_name = self.findTag(a, "first_name")
            unique_id  = int(self.findTag(a, "unique_id"))
            accnt_name = self.findTag(a, "account-name")
            emailStr   = self.findTag(a, "email")
            # find this author in OUR DB
            users = User.objects.filter(first_name = first_name
                                          , last_name = last_name).all()

            if len(users) == 0:
                # add new user!
                u = User( sanctioned = False 
                        , first_name  = first_name 
                        , last_name   = last_name #row[2]
                        , role        = first(Role.objects.filter(role = "Observer"))
                 )
                u.save()   
                print >> self.out, "Added User: ", u
            else:
                print >> self.out, "User already in DB?: "
                for u in users:
                    print >> self.out, u
            
    def getUserNamesFromProjects(self, username, password):
        """
        Here is a method for getting all usernames by first getting
        author information from the proposal web services.
        """

        # get rid of this banner once other print statements are gone
        print >> self.out, "********** Retrieving usernames from project authors. *********"

        # get all projects
        ps = Project.objects.all()

        # use service to get all users with this last name
        #url = "https://mirror.nrao.edu/nrao-2.0/secure/QueryFilter.htm"
        url = "https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm"
        udb = NRAOUserDB( \
            url  
          , username
          , password
          , opener=urllib2.build_opener())

        key = 'authorsByProposalId'
        global_id_key = 'userByGlobalId'

        ui = UserInfo()

        # for keeping track of our progess
        failures = []
        notInPST = []
        usersAbsent = []
        usersMultiple = []
        usersFound = []
        badIds = []

        # for each project, try to retrieve author info:
        # NOTE - not all projects are available
        for p in ps:

            # format project name
            id = "%s/%s" % (p.pcode[:3], p.pcode[3:])

            # use the service!
            try:
                el = udb.get_data(key, id)
            except:
                print >> self.out, "EXCEPTION w/ id: ", id
                failures.append(p)
                continue
            #print ET.tostring(el, pretty_print=True)

            subel = el.getchildren()
            authors = subel[0].getchildren()
            numAuthors = len(authors)

            # a bunch of our proposals aren't in the PST
            if numAuthors == 0:
                notInPST.append(p)

            # for each author, try to use the info we got
            for i in range(numAuthors):
                # get an author
                a = authors[i]
                # get it's info
                last_name  = self.findTag(a, "last_name")
                first_name = self.findTag(a, "first_name")
                # TBF WTF!
                # This 'unique_id' is really the global_id, not the 'id'
                # that we are using throughout our code!
                # That means this is not a suitable way of setting the
                # pst_id anymore! so save it and move on.
                global_id  = int(self.findTag(a, "unique_id"))
                accnt_name = self.findTag(a, "account-name")
                emailStr   = self.findTag(a, "email")

                # now, turn around and get OUR id from the global_id
                try:
                    el = udb.get_data(global_id_key, global_id)
                    globalInfo = ui.parseUserXML(el)
                    pst_id = globalInfo['id']
                except:
                    print >> self.out, "EXCEPTION w/ global_id: ", global_id  
                    failures.append(p)
                    continue

                # find this author in OUR DB
                users = User.objects.filter(first_name = first_name
                                          , last_name = last_name).all()
                # if that failed, try email:
                if len(users) == 0:
                    email = first(Email.objects.filter(email = emailStr).all())
                    if email is not None:
                        #print "Using email %s for user %s, last: %s, first: %s" % (email.email, email.user, last_name, first_name)
                        users = [email.user]

                #print "tried to match: ", first_name, last_name, emailStr
                #print "users: ", users
                #x = raw_input("hold on.")

                numUsers = len(users)
                entry = (first_name, last_name, emailStr, numUsers)

                # Only save to the DB if we got one unique user                 
                if numUsers == 1:
                    u = users[0]        
                    if (u, pst_id, accnt_name) not in usersFound:
                            usersFound.append((u, pst_id, accnt_name))
                    if u.pst_id is not None:
                        if u.pst_id != pst_id:
                            badIds.append((u, u.pst_id, pst_id))
                            print >> self.out, "BAD ID!!!!!!!!!!!!!!!!!!!"
                            print >> self.out, u.pst_id, pst_id
                            continue
                    # save what we've learned to the DB!!!        
                    if u.pst_id is None:
                        print >> self.out, "Saving to: ", u
                        print >> self.out, accnt_name, pst_id
                        u.username = accnt_name
                        u.pst_id = pst_id
                        u.save()
                elif numUsers == 0:
                    # no users - do we care if what's in the PST isn't all
                    # in our system?
                    if entry not in usersAbsent:
                        usersAbsent.append(entry)
                else:
                    # multiplies!
                    if entry not in usersMultiple:
                        usersMultiple.append(entry)
            
        # who has been left out?
        
        # print list of problems    
        print >> self.out, "USERS found: "
        for user in usersFound:
            print >> self.out, user

        print >> self.out, "Users Absent: "
        for user in usersAbsent:
            print >> self.out, user

        print >> self.out, "Projects NOT in PST:"
        for p in notInPST:
            print >> self.out, p

        uniqueUsers = []
        redundantUsers = []
        for user, id, username in usersFound:
            if user not in uniqueUsers:
                uniqueUsers.append(user)
            else:
                redundantUsers.append((user, id, username))

        print >> self.out, "redundant users: "
        for r in redundantUsers:
            print >> self.out, r

        print >> self.out, "bad ids users: "
        for r in badIds:
            print >> self.out, r

        # print summary
        print >> self.out, "total # of projects: %d" % len(ps)
        print >> self.out, "total # of projects that were NOT in PST: %d" % len(notInPST)
        print >> self.out, "total # of project that caused exceptions: %d" % len(failures)
        print >> self.out, ""
        print >> self.out, "total # of users found: %d" % len(usersFound)
        print >> self.out, "total # of users not in our DB: %d" % len(usersAbsent)
        print >> self.out, "total # of users in our DB that share first & last name: %d" % len(usersMultiple)
        print >> self.out, "total # of bad Ids: %d" % len(badIds)

    def findTag(self, node, tag):
        value = None
        value_tag = node.find(tag)
        if value_tag is not None:
            value = value_tag.text
        return value    

    def createMissingUsers(self):
        "Creates users who probably aren't on a GBT proposal in the PST"

        # add this to the list whenever you come across users who aren't
        # in the DB, but you know they should be
        # first, last name, username, pst_id
        admins = [("Paul", "Marganian", "pmargani",   823)
                , ("Mark", "Clark",     "windyclark", 1063)
                , ("Amy",  "Shelton",   "ashelton",   556 )
                , ("Dan",  "Perera",    'dperera',    2705)
                , ("Todd", "Hunter",    'trhunter',   495)
                , ("Glen", "Langston",  'glangsto',   45)
                # TBF: these folks in the schedtime table, so WTF?
                , ("Steve", "White",     None,        None) 
                , ("Galen", "Watts",     None,        None) 
                , ("John",  "Ford",      None,        None) 
                # who else?
                 ]

        for first_name, last, user, id in admins:
            # don't make'm unless you have to
            u = first(User.objects.filter(first_name = first_name
                                        , last_name  = last)) 
            if u is not None:
                continue
            # you have to
            u = User(original_id = 0
               , sanctioned  = True
               , first_name  = first_name 
               , last_name   = last 
               , username    = user
               , pst_id      = id 
               #, role        = first(Role.objects.filter(role = "Administrator"))
               , role        = first(Role.objects.filter(role = "Observer"))
                 )
            u.save()

    def setAdminRoles(self):
        "Simply set the given list of staff as admins."

        # list of last names
        staff = ["Braatz"  # first astronomers
               , "Balser"
               , "O'Neil"
               , "Minter"
               , "Harnett"
               , "Maddalena"
               , "Ghigo"
               , "Marganian" # then the real smart people
               , "Clark"
               , "Shelton"
               , "McCarty"
               , "Sessoms"
               ]

        admin = first(Role.objects.filter(role = "Administrator"))

        # set them!
        users = User.objects.all()
        for u in users:
            if u.last_name in staff:
                u.role = admin
                u.save()

    def setUserName(self, username, userLastName):
        "This is for testing only: if username is in PST but not in DSS, the use username for given user"
        victim = first(User.objects.filter(last_name = userLastName).all())
        victim.username = username
        victim.save()
        print >> self.out, "User %s now has username: %s" % (victim, username)

    def save_project_observers(self):

        f = open('observers.txt', 'w')
        lines = []
        ps = Project.objects.order_by('pcode').all()
        for p in ps:
            users = [inv.user for inv in p.investigator_set.all()]
            names = [u.last_name for u in users]
            names.sort()
            nameStr = ','.join(names)
            line = "%s:%s\n" % (p.pcode, nameStr)
            lines.append(line)
        f.writelines(lines)    
        f.close()

    def create_dss_user(self):

        role = first(Role.objects.filter(role = "Administrator"))
        u = User(first_name = 'dss'
               , last_name  = 'account'
               , username   = 'dss'
               , pst_id     = 3259
               , role       = role
               )
        u.save()       
