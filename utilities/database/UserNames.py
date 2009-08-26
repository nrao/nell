from sesshuns.models import *
from datetime        import datetime, timedelta
import math
import MySQLdb as m
import logging, urllib2
from utilities import NRAOUserDB
from utilities.UserInfo import UserInfo
import lxml.etree as ET

class UserNames(object):

    """
    This class is simply a collection of different methods for managing
    issues related to usernames and IDs.
    """

    def confirmUserInfo(self, queryUser, queryPassword):
        "Checks contents of User table against info from PST service w/ pst ID."

        users = User.objects.all()
        ui = UserInfo()

        # keep records
        noPstId = []
        matched = []
        mismatched = []

        for u in users:
            if u.pst_id is not None:
                info = ui.getStaticContactInfoByID(u.pst_id
                                                 , queryUser
                                                 , queryPassword)
            
                # extract what the PST thinks about this user
                pstId        = int(info['id'])
                pstUsername  = info['account-info']['account-name'].strip()
                pstFirstName = info['name']['first-name'].strip()
                pstLastName  = info['name']['last-name'].strip()

                assert (pstId == u.pst_id)
                assert (pstUsername == u.username)
                # just check for names
                #if pstId != u.pst_id or pstUsername != u.username or \
                if pstFirstName != u.first_name or \
                   pstLastName != u.last_name:
                    print "PST: %s %s vs. DSS: %s %s" % (pstFirstName
                                                       , pstLastName
                                                       , u.first_name
                                                       , u.last_name)
                    mismatched.append(u)
                else:
                    matched.append(u)
            else:
                noPstId.append(u)

        # report
        print "len(users): ", len(users)
        print "len(noPstId): ", len(noPstId)
        print "len(matched): ", len(matched)
        print "len(mismatched): ", len(mismatched)

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
        filename = "user_table.txt"
        f = open(filename, 'r')
        lines = f.readlines()

        # keep some records
        matched = []
        mismatched = []

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
            if first_name != ourUser.first_name or \
               last_name != ourUser.last_name:
                print "mismatch: ", ourUser, first_name, last_name
                mismatched.append((ourUser, first_name, last_name))   
                ourUser.first_name = first_name
                ourUser.last_name = last_name
            # pass over the usernames and ids:
            matched.append(ourUser)
            ourUser.username = username
            ourUser.pst_id   = pst_id
            ourUser.save()
    
        print "mismatched: ", mismatched
        print "len(mismatched): ", len(mismatched)
        print "len(matched): ", len(matched)
        print "len(ourUsers): ", len(User.objects.all())

    def getUserNamesFromIDs(self, queryUser, queryPassword):

        # use query services
        ui = UserInfo()

        # get all users
        users = User.objects.all()

        missing = []
        saved = []
        agree = []

        # for each user, get their static contact info
        for user in users:

            id = user.pst_id

            if id is None:
                print "skipping user, no pst_id: ", user
                missing.append(user)
                continue

            # save off the username
            info = ui.getStaticContactInfoByID(id, queryUser, queryPassword)
            #print info
            username = info['account-info']['account-name']

            if user.username is not None:
                if user.username == username:
                    #no-op
                    print "usernames agree for: ", user
                    agree.append(user)
                else:
                    raise "user.username != username! " + user.username + "!=" + username
            else:
                saved.append(user)
                print "saving username: ", user, username
                user.username = username
                user.save()
        
        print "saved: ", saved
        print "missing: ", missing

        print "num agreed: ", len(agree)
        print "num saved: ", len(saved)
        print "num no pst_id: ", len(missing)

    def getUserNames(self, username, password):
        "DEPRECATED: but may be useful for testing query services"

        skipping = []

        # use service to get all users with this last name
        udb = NRAOUserDB.NRAOUserDB( \
            'https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
          , username
          , password
          , opener=urllib2.build_opener())

        key = 'usersByLastNameLike'

        users = self.getUsersUniqueByLastName()

        #users =  User.objects.all()
        for user in users:
            print user.last_name

            if "'" in user.last_name:
                skipping.append(user)
                print "SKIP: ", user
                continue

            el = udb.get_data(key, user.last_name)
            print ET.tostring(el, pretty_print=True)

            # name
            first_name  = el[0][1].text
            #middle_name = el[0][2].text
            #last_name   = el[0][3].text
            #assert (last_name == user.last_name)

            # account name
            accountName = el[4][0].text

            # save it off!
            #user.username = accountName
            print accountName
        
        print "skipped: ", skipping

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
        
        print "Users that share the same last name: "
        print notUniques

        return uniques

    def getUserNamesFromProjects(self, username, password):
        """
        Here is a method for getting all usernames by first getting
        author information from the proposal web services.
        """

        # get all projects
        ps = Project.objects.all()

        # use service to get all users with this last name
        #url = "https://mirror.nrao.edu/nrao-2.0/secure/QueryFilter.htm"
        url = "https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm"
        udb = NRAOUserDB.NRAOUserDB( \
            url  
          , username
          , password
          , opener=urllib2.build_opener())

        key = 'authorsByProposalId'

        # for keeping track of our progess
        failures = []
        notInPST = []
        usersAbsent = []
        usersMultiple = []
        usersFound = []

        # for each project, try to retrieve author info:
        # NOTE - not all projects are available
        for p in ps:

            # format project name
            id = "%s/%s" % (p.pcode[:3], p.pcode[3:])

            # use the service!
            print "id: ", id
            try:
                el = udb.get_data(key, id)
            except:
                print "EXCEPTION w/ id: ", id
                failures.append(p)
                continue
            print el
            print len(el)
            #print ET.tostring(el, pretty_print=True)

            numAuthors = len(el)

            # a bunch of our proposals aren't in the PST
            if numAuthors == 0:
                notInPST.append(p)

            # for each author, try to use the info we got
            for i in range(numAuthors):
                # get an author
                a = el[i]
                # get it's info
                last_name  = self.findTag(a, "last_name")
                first_name = self.findTag(a, "first_name")
                unique_id  = self.findTag(a, "unique_id")
                accnt_name = self.findTag(a, "account-name")
                email      = self.findTag(a, "email")

                # find this author in OUR DB
                users = User.objects.filter(first_name = first_name
                                          , last_name = last_name).all()
                # if that failed, try email:
                if len(users) == 0:
                    email = first(Email.objects.filter(email = email).all())
                    if email is not None:
                        print "Using email %s for user %s, last: %s, first: %s" % (email.email, email.user, last_name, first_name)
                        users = [email.user]

                numUsers = len(users)
                entry = (first_name, last_name, email, numUsers)

                # Only save to the DB if we got one unique user                 
                if numUsers == 1:
                    u = users[0]        
                    if (u, unique_id, accnt_name) not in usersFound:
                            usersFound.append((u, unique_id, accnt_name))
                    # save what we've learned to the DB!!!        
                    u.username = accnt_name
                    u.pst_id = unique_id
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
        print "USERS found: "
        for user in usersFound:
            print user

        print "Users Absent: "
        for user in usersAbsent:
            print user

        print "Projects NOT in PST:"
        for p in notInPST:
            print p

        uniqueUsers = []
        redundantUsers = []
        for user, id, username in usersFound:
            if user not in uniqueUsers:
                uniqueUsers.append(user)
            else:
                redundantUsers.append((user, id, username))

        print "redundant users: "
        for r in redundantUsers:
            print r

        # print summary
        print "total # of projects: %d" % len(ps)
        print "total # of projects that were NOT in PST: %d" % len(notInPST)
        print "total # of project that caused exceptions: %d" % len(failures)
        print ""
        print "total # of users found: %d" % len(usersFound)
        print "total # of users not in our DB: %d" % len(usersAbsent)
        print "total # of users in our DB that share first & last name: %d" % len(usersMultiple)

    def findTag(self, node, tag):
        value = None
        value_tag = node.find(tag)
        if value_tag is not None:
            value = value_tag.text
        return value    

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
        print "User %s now has username: %s" % (victim, username)
