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

from datetime                  import datetime
from django.contrib.auth.models import User as AuthUser
from django.db                 import models

from Role              import Role
from nell.utilities.database.external    import  UserInfo
from nell.utilities.database.external.BOSMirrorDB    import BOSMirrorDB 

class User(models.Model):
    original_id          = models.IntegerField(null = True, blank = True)
    pst_id               = models.IntegerField(null = True, blank = True)
    sanctioned           = models.BooleanField(default = False)
    first_name           = models.CharField(max_length = 32)
    last_name            = models.CharField(max_length = 150)
    contact_instructions = models.TextField(null = True, blank = True)
    roles                = models.ManyToManyField(Role, null = True)
    auth_user            = models.ForeignKey(AuthUser, null = True)

    staticContactInfo = None

    class Meta:
        db_table  = "users"
        app_label = "scheduler"

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def name(self):
        return self.__str__()

    def display_name(user):
        return "%s %s" % (user.first_name, user.last_name)

    def username(self):
        "This is no longer stored in the DB, but is pulled"
        return UserInfo().getUsername(self.pst_id)

    def addRole(self, role):
        """
        addRole(self, role): Add a role to the user.  'role' can be a
        Role object, or its name (i.e. "Observer").  If 'role' is none
        of these, an exception will be thrown: 'DoesNotExist' if the
        name is not that of a role, or 'TypeError' if something other
        than a string or Role is passed in.
        """
        role = self._get_role(role)

        if not self.hasRole(role):
            self.roles.add(role)

    def removeRole(self, role):
        """
        removeRole(self, role): Removes a role from the user. 'role'
        may be a Role object, or its name (i.e. "Administrator").  If
        'role' is none of these, an exception will be thrown:
        'DoesNotExist' if the name is not that of a role, or
        'TypeError' if something other than a string or Role is passed
        in.
        """
        role = self._get_role(role)

        if self.hasRole(role):
            self.roles.remove(role)

    def hasRole(self, role):
        """
        hasRole(self, role): Checks to see if 'role' (which may be a
        string or a Role object) is in the collection of this user's
        roles.
        """
        r = self._get_role(role)
        return r in self.roles.all()

    def isAdmin(self):
        """
        isAdmin(self): Checks to see if the 'Administrator' role is in
        this user's collection of roles.  Returns true if it is.
        """
        return self.hasRole("Administrator")

    def isOperator(self):
        """
        isOperator(self): Checks to see if the 'Operator' role is in
        this user's collection of roles.  Returns true if it is.
        """
        return self.hasRole("Operator")

    def isStaff(self):
        """
        isStaff(self): Checks to see if 'Staff' is in the user's
        roles.
        """
        return self.hasRole("Staff")
    
    def checkAuthUser(self):
        if self.auth_user_id is None:
            from django.contrib.auth.models import User as AuthUser
            try:
                au = AuthUser.objects.get(username = self.username())
                self.auth_user = au
                self.save()
            except AuthUser.DoesNotExist:
                pass

    def getEmails(self):
        """
        Retrieves the users emails from their contact info from the PST.
        If you want the official emails for this user, use this function.
        """
        return self.getStaticContactInfo()['emails']

    def getStaticContactInfo(self): 
        return UserInfo().getProfileByID(self) 

    def loadStaticContactInfo(self):
        self.staticContactInfo = UserInfo().getProfileByID(self)

    def getReservations(self): 
        """
        Use the PST to get the one of the User's types of IDs.  Then
        use that ID to get the reservations from the BOS.
        """
        if self.pst_id is None:
            return []
        bosId = UserInfo().getUserAuthenticationIdFromId(self.pst_id)
        return BOSMirrorDB().getReservationsByUserAuthId(bosId)

    def getPeriods(self):
        retval = []
        for i in self.investigator_set.all():
            retval.extend(i.project.getPeriods())
        return sorted(list(set(retval)))

    def getPeriodsByProject(self):
        """
        Returns a dictionary of project: [periods] associated with this
        user sorted by start date.
        """
        retval = {}
        for i in self.investigator_set.all():
            retval[i.project] = i.project.getPeriods()
        return retval

    def getUpcomingPeriods(self, dt = datetime.now()):
        "What periods might this observer have to observe soon?"
        return [p for p in self.getPeriods() if p.start >= dt]

    def getUpcomingPeriodsByProject(self, dt = datetime.now()):
        "What periods might this observer have to observe soon?"
        retval = {}
        for project, period in self.getPeriodsByProject().items():
            retval[project] = [p for p in period if p.start >= dt]
        return retval

    def getObservedPeriods(self, dt = datetime.now()):
        "What periods associated w/ this observer have been observed?"
        return [p for p in self.getPeriods() if p.start < dt]

    def getObservedPeriodsByProject(self, dt = datetime.now()):
        "What periods associated w/ this observer have been observed?"
        retval = {}
        for project, period in self.getPeriodsByProject().items():
            retval[project] = [p for p in period if p.start < dt]
        return retval

    def getFriendLastNames(self):
        "Returns a list of all the friends' names that are assisting this user."
        projects = [i.project for i in self.investigator_set.all()]
        return list(set([f.user.last_name for p in projects
                                    for f in p.friend_set.all()]))

    def getProjects(self):
        """
        Returns a list of all the project codes for which this user is an
        investigator.
        """
        return [i.project.pcode for i in self.investigator_set.all()]

    def getFriendedProjects(self):
        """
        Returns a list of all the projects for which this user is a friend.
        """
        return [f.project for f in self.friend_set.all()]

    def getIncompleteProjects(self):
        "Like getProjects, but only for those that are still not completed."
        return [i.project.pcode for i in self.investigator_set.all() \
            if not i.project.complete]

    def isInvestigator(self, pcode):
        "Is this user an investigator on the given project?"
        return pcode in [i.project.pcode for i in self.investigator_set.all()]

    def isFriend(self, pcode = None):
        """
        If 'pcode' is not given, check to see if this user is
        qualified as a friend.  If 'pcode' is given, checks to see if
        the user is a friend for the given project.
        """

        if pcode:
            return pcode in [f.project.pcode for f in self.friend_set.all()]
        else:
            return self.hasRole("Friend")

    def canViewProject(self, pcode):
        "A user can view project info if he's an inv, friend, admin, or op."
        return self.isInvestigator(pcode) \
            or self.isFriend(pcode) \
            or self.isAdmin() \
            or self.isOperator()

    def canViewUser(self, user):
        """
        A user can view another user if they share the same project (by being
        an investigator or friend), or if they are admin or op.
        """
        upcodes = [i.project.pcode for i in user.investigator_set.all()]
        shared_projects = [p for p in upcodes if self.isFriend(p) \
                                              or self.isInvestigator(p)]
        return shared_projects != [] or self.isAdmin() or self.isOperator()

    def hasIncompleteProject(self):
        return any([not i.project.complete \
            for i in self.investigator_set.all()])

    def _get_role(self, role):
        """
        _get_role(self, role): returns a Role object corresponding to
        'role'.  If 'role' is a string a db lookup is attempted on it,
        and if successful a Role object is returned, otherwise the
        original 'role' is assumed to be a 'Role' and is returned
        """
        if type(role).__name__ == 'str':
            r = Role.objects.get(role = role)
            role = r
        return role
