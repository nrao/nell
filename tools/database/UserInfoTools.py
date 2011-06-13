from scheduler.models    import *
from datetime           import datetime, timedelta
import math
import MySQLdb as m
import logging, urllib2
from nell.utilities.database.external import NRAOUserDB, UserInfo, PSTMirrorDB
import lxml.etree as ET
import sys

class UserInfoTools(object):

    """
    This class is simply a collection of different methods for managing
    issues related to usernames and IDs.
    """

    def __init__(self, output_file = None):

        # should print outs go to the screen, or a file?
        if output_file == None:
            self.out = sys.stdout
        else:
            self.out = output_file
            
    def findUserMatches(self):
        """
        Lists all DSS users who do not currently have a pst_id, and lists possible candidates
        from the PST.  This report can be used to make decisions manually on how to assign
        the pst_id.
        """

        mirror = PSTMirrorDB()

        # get all users who don't have a pst_id
        users = User.objects.filter(pst_id = None)

        for u in users:
            # what DSS user is this, and what projects are they on?
            invs = Investigator.objects.filter(user = u)
            projs = ",".join([i.project.pcode for i in invs])
            print >> self.out, ""
            print >> self.out, "User: %s, Projects: %s" % (u, projs)
            # who could we match these up with?
            others = mirror.findPeopleByLastName(u.last_name)
            print >> self.out, "%20s %20s %5s %5s %30s" % ('First', 'Username', 'PSTID', 'Enbld', 'Emails')
            for oldId, username, firstName, enabled, pst_id in others:
                emails, descs = mirror.getEmails(pst_id)
                es = ",".join(emails)
                print >> self.out, "%20s %20s %5s %5s %30s" % (firstName, username, pst_id, enabled, es)


    def reportUserInfo(self):
        "Checks contents of User table against info from PST service w/ pst ID and reports diffs."

        print >> self.out, "Comparing DSS Users to their info (first, last names) in the PST"

        users = User.objects.all()

        # keep records
        noPstId = []
        matched = []
        mismatched = []
        badBothNames = []
        justBadFirstNames = []
        justBadLastNames = []

        ui = UserInfo()
        
        for i, u  in enumerate(users):

            # if the DSS user doesn't have a PST id, we can't check it against the PST
            if u.pst_id is not None:

                # what does the PST think of the owner of this pst_id?
                info = ui.getProfileByID(u)
                pstId        = u.pst_id 
                pstUsername  = info['username'] 
                # catch excpetions having to do with bad characters
                try:
                    pstFirstName = unicode(info['first_name']) 
                except:
                    pstFirstName = "UnicodeExp"
                try:
                    pstLastName  = unicode(info['last_name']) 
                except:
                    pstLastName = "UnicodeExp"

                # if the names match up exactly, it's a match, if not,
                # what kind of mismatch is it?
                if pstFirstName != u.first_name or \
                   pstLastName != u.last_name:
                    #print >> self.out, "PST: %s %s vs. DSS: %s %s" % (pstFirstName
                    #                                   , pstLastName
                    #                                   , u.first_name
                    #                                   , u.last_name)

                    # get more specific                                   
                    if u.last_name != pstLastName and u.first_name != pstFirstName:
                        badBothNames.append((u, pstFirstName, pstLastName))
                    if u.last_name != pstLastName and u.first_name == pstFirstName:
                        justBadLastNames.append((u, pstFirstName, pstLastName))
                    if u.last_name == pstLastName and u.first_name != pstFirstName:
                        justBadFirstNames.append((u, pstFirstName, pstLastName))

                    # be more general    
                    mismatched.append((u, pstFirstName, pstLastName))
                else:
                    matched.append(u)
            else:
                # not much to do here
                noPstId.append(u)

        # report details
        if len(badBothNames) > 0:
            print >> self.out, "Both names bad: "
        for b in badBothNames:
            print >> self.out, b
        if len(justBadFirstNames) > 0:
            print >> self.out, "First names bad: "
        for b in justBadFirstNames:
            print >> self.out, b
        if len(justBadLastNames) > 0:
            print >> self.out, "Last names bad: "
        for b in justBadLastNames:
            print >> self.out, b

        # report summary
        print >> self.out, "Summary: "
        print >> self.out, "len(users): ", len(users)
        print >> self.out, "len(noPstId): ", len(noPstId)
        print >> self.out, "len(matched): ", len(matched)
        print >> self.out, "len(mismatched): ", len(mismatched)
        print >> self.out, "len(badBothNames): ", len(badBothNames)
        print >> self.out, "len(justBadFirstNames): ", len(justBadFirstNames)
        print >> self.out, "len(justBadLastNames): ", len(justBadLastNames)

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

        observer = Role.objects.get(role = "Observer")

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
            ourUser = User.objects.filter(original_id=original_id)[0]
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


    def reconcileUsersWithSamePstId(self, sharedPstId, finalUserId):
        """
        Distinct from reconcileRedundantUsers.  Here we aren't searching
        for redundancies, we already know what they are, we just want
        this function to do all the dirty work for us.
        Use the given PST id to find all the redundant user, and move all
        info to the given final user.
        """

        # normally, this would return just one user
        us = User.objects.filter(pst_id = sharedPstId)
        assert len(us) > 1

        # only one of these user objects will be kept
        assert finalUserId in [u.id for u in us]

        finalUser = User.objects.get(id = finalUserId)

        print >> self.out, "Final User originally looks like: ", finalUser, finalUser.id
        print >> self.out,  "Projects: ", finalUser.getProjects()
        print >> self.out, "Blackouts: ", finalUser.blackout_set.all()

        usersToDelete = [u for u in us if u.id != finalUserId]

        # before deleting each redundant user record, copy over
        # their projects and blackouts
        for u in usersToDelete:
            # projects
            invs = u.investigator_set.all()
            for inv in invs:
                print >> self.out, "    Moving project: ", inv.project
                inv.user = finalUser
                inv.save()
            # blackouts
            for b in u.blackout_set.all():
                print >> self.out, "    Moving Blackout: ", b
                b.user = finalUser
                b.save()
            # now we can delete
            print >> self.out, "Deleting User Record: ", u, u.id
            u.delete()
            
        print >> self.out, "Final User finally looks like: ", finalUser, finalUser.id
        print >> self.out, "Projects: ", finalUser.getProjects()
        print >> self.out, "Blackouts: ", finalUser.blackout_set.all()
        
        us = User.objects.filter(pst_id = sharedPstId)
        assert len(us) == 1

    def reconcileRedundantUsers(self):
        """
        This method is only needed if something very bad happens: users are entered duplicate times,
        and reconciliation needs to be done.
        """

        existing = []
        matches = []

        # get all users w/ out a pst_id
        noIds = User.objects.filter(pst_id = None).order_by("id")

        # look for duplicates: users w/ the same last name and email
        for u in noIds:
            match = False
            othersMaybe = User.objects.filter(last_name = u.last_name)

            # here's the other users that share the same last name
            others = [o for o in othersMaybe if o.id != u.id]

            # if there are any users that share the same last name for this user
            # record this user
            if len(others) > 0:
                print >> self.out, ""
                print >> self.out, "existing for : ", u, [e.email for e in u.email_set.all()]
                existing.append(u)

            # for each one of these other users that share the same last name    
            for o in others:
                print >> self.out, "    ", o, o.pst_id, o.username()
                # check for email match
                info = o.getStaticContactInfo()
                emails = info['emails']
                match = False
                for existingEmail in emails:
                    for e in u.email_set.all():
                        if e.email.strip() == existingEmail.strip():
                            match = True # emails match!
                # check for first name match
                if o.first_name == u.first_name:
                    match = True
                # if we found a match, record this    
                if match:
                    print >> self.out, "Match!!!!: ", emails, [e.email for e in u.email_set.all()]
                    matches.append((u, o))
                    
                    break

        # for each pair of duplicates, make sure the projects get transfered over
        # and that one of the duplicates gets nuked
        for bad, old in matches:
            print >> self.out, "deleting: ", bad, bad.id
            # delete old investigators
            invs = Investigator.objects.filter(user = bad)
            for i in invs:
                print >> self.out, "    Switching Project observer: ", i.project.pcode
                n =  Investigator(project = i.project
                                , user    = old
                                , principal_contact      = i.principal_contact
                                , principal_investigator = i.principal_investigator
                                  )            
                n.save()                              
                i.delete()
    
            # switch old friends
            ps = Project.objects.filter(friend = bad)
            for p in ps:
                print "    Switching Friend on: ", p.pcode
                p.friend = old
                p.save()
            
            # delete bad user
            bad.delete()

        print >> self.out, "Of %d users w/ NO pst_id, %d share last name w/ existing user." % (len(noIds), len(existing))        
        print >> self.out, "%d matches" % len(matches)
        noPstStill = User.objects.filter(pst_id = None).order_by("id")
        print "%d remaining users w/ NO pst_id" % len(noPstStill)

    def assignPstIds(self):
        """
        This method's goal is to find DSS Users w/ out PST id's (probably newly added to the DSS),
        and assign them one.  It does this by finding a PST user with the same last and first name
        as the DSS user, and using this PST id.
        It also reports on these matches and the users who could not get assigned a PST id.
        """

        ui = UserInfo()
        mirror = PSTMirrorDB()
        users = User.objects.all() 

        missing = [u for u in users if u.pst_id is None] 

        self.match = []
        self.noMatch = []
        self.duplicates = []

        for user in missing:
            print >> self.out, "Looking for matches for DSS user: %s" % user

            # skip problem users - this can be added to if problems arise
            if user.last_name in ['Ivanova', 'Jone'] or "'" in user.last_name:
                print >> self.out, "Skipping DSS user: %s" % user
                continue

            # find all the PST users that are enabled and share the same last name as
            # our DSS user
            infos = []
            lastNames = mirror.findPeopleByLastName(user.last_name)
            for old_id, username, firstName, enabled, pst_id in lastNames:
                if enabled:
                    infos.append((firstName, username, pst_id))
                else:
                    print >> self.out, "Disabled PST user: ", user.last_name, firstName
            matchingInfo = [i for i in infos if i[0] == user.first_name]

            # if we found just one PST user that shares names w/ our DSS user, then
            # we have found our pst_id
            if len(matchingInfo) == 1:
                first_name, username, id = matchingInfo[0]
                print >> self.out, "Found pst_id for user: ", user, username, id
                user.pst_id = id
                user.save()
                self.match.append((user, username, id))
            elif len(matchingInfo) > 1:
                # we found more then one PST user for our DSS user; there could possibly
                # be duplicates in the PST
                print >> self.out, "Duplicate PST entry for user: ", user
                self.duplicates.append((user, matchingInfo))
            else:
                # no matches were found!
                print >> self.out, "Did NOT find pst_id for user: ", user
                self.noMatch.append((user, infos))

        # report the results
        print >> self.out, "Results: "
        print >> self.out, "Number of DSS users originally missing pst_id: ", len(missing)
        print >> self.out, "Matches found (pst_id assigned): ", len(self.match)
        for u, un, id in self.match:
            print >> self.out, "    ", u, un, id
        print >> self.out, "No matches found (no pst_id assigned): ", len(self.noMatch)
        for u, i in self.noMatch:
            print >> self.out, "    ", u, i
        print >> self.out, "Duplicate PST entries? (no pst_id assigned): ", len(self.duplicates)
        for u, i in self.duplicates:
            print >> self.out, "    ", u, i

        # now see how many users still need pst_ids
        users = User.objects.all() 
        missing = [u for u in users if u.pst_id is None] 
        print >> self.out, "NOW number of DSS users missing pst_id: ", len(missing)

            

