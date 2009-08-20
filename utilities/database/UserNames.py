from sesshuns.models import *
from datetime        import datetime, timedelta
import math
import MySQLdb as m
import logging, urllib2
from utilities import NRAOUserDB
import lxml.etree as ET

class UserNames(object):

#    def __init__(self, host = "trent.gb.nrao.edu"
#                     , user = "dss"
#                     , passwd = "asdf5!"
#                     , database = "dss_pmargani_test"
#                     , silent   = True
#                 ):
#        self.db = m.connect(host   = host
#                          , user   = user
#                          , passwd = passwd
#                          , db     = database
#                            )
#        self.cursor = self.db.cursor()

    def getUserNames(self, username, password):

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
