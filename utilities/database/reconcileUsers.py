#!/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)


from sesshuns.models import *


def reconcileUser(user):

    (ln, fn) = user

    # how many users?
    users = User.objects.filter(last_name = ln, first_name = fn)

    if len(users) != 2:
        print "cant handle %d users: %s, %s" % (len(users), ln, fn)
        return

    u1 = users[0]
    u2 = users[1]

    ps1sems = getSemesters(u1)
    ps2sems = getSemesters(u2)

    if ps1sems == ['10C']:
        badUser = u1
        goodUser = u2
    elif ps2sems == ['10C']:
        badUser = u2
        goodUser = u1
    else: 
        print "no semster 10C projects for user: %s, %s, ids: %d, %d" % (ln, fn, u1.id, u2.id)
        return

    assert badUser.username is None
    assert goodUser.username is not None
    #assert len(getProjects(goodUser)) > 0

    print "User %s, %s: %d -> %d" % (ln, fn, badUser.id, goodUser.id)    
    print "Moving projects: ", [p.pcode for p in getProjects(badUser)]
    print "To join projects: ", [p.pcode for p in getProjects(goodUser)]
    print ""

    # shut up and do it
    for p in getProjects(badUser):
        inv = Investigator(user = goodUser, project = p)
        inv.save()
    # bye bye duplicates!    
    badUser.delete()

def getProjects(user):

    invs = Investigator.objects.filter(user = user)
    return [inv.project for inv in invs]

def getSemesters(user):

    #ps = user.project_set.all()
    invs = Investigator.objects.filter(user = user)
    sems = []
    #for p in ps:
    #    sem = p.semester.semester
    for inv in invs:
        sem = inv.project.semester.semester
        if sem not in sems:
            sems.append(sem)
    return sems        

def checkForDuplicateUsers():

    print "Checking for Duplicate accounts: "

    users  = list(User.objects.order_by("last_name"))
    values = []
    for u in users:
        users.remove(u)
        for i in users:
            if i.last_name == u.last_name and i.first_name == u.first_name:
                values.append(u)
    for v in values:
        print "Duplicate Accounts for: ", v

def reconcileUsers():

    # TBF: update this as needs be
    # TBF: modifiy checkForDuplicateUsers to create this list dynamically
    users = [('Bartel', 'Norbert')
            , ('Bietenholz', 'Michael')
            , ('Bolton', 'Rosie')
            , ('Cherinka', 'Brian')
            , ('Hankins', 'Timothy')
            , ('Keane', 'Evan')
            , ('Korngut', 'Phil')
            , ('Langston', 'Glen')
            , ('Lo', 'Fred')
            , ('Panessa', 'Francesca')
            , ('Reese', 'Erik')
            , ('Urquhart', 'James')
            , ('Willett', 'Kyle')
            ]

    # get rid of duplicates
    for u in users:
        reconcileUser(u)

    # check again
    checkForDuplicateUsers()

if __name__ == '__main__':
    reconcileUsers()
    #checkForDuplicateUsers()
