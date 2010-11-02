from datetime                  import datetime
from django.contrib.auth.models import User as AuthUser
from django.core.cache         import cache
from django.db                 import models
from nell.utilities            import UserInfo, NRAOBosDB
from sets                      import Set

from Role       import Role
from common     import first

class User(models.Model):
    original_id = models.IntegerField(null = True, blank = True)
    pst_id      = models.IntegerField(null = True, blank = True)
    sanctioned  = models.BooleanField(default = False)
    first_name  = models.CharField(max_length = 32)
    last_name   = models.CharField(max_length = 150)
    contact_instructions = models.TextField(null = True, blank = True)
    role                 = models.ForeignKey(Role)
    auth_user            = models.ForeignKey(AuthUser, null = True)

    class Meta:
        db_table  = "users"
        app_label = "sesshuns"

    def __str__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def name(self):
        return self.__str__()

    def display_name(user):
        return "%s %s" % (user.first_name, user.last_name)

    def username(self):
        "This is no longer stored in the DB, but is pulled"
        # TBF: use a simple cache?
        return UserInfo().getUsername(self.pst_id)

    def isAdmin(self):
        return self.role.role == "Administrator"

    def isOperator(self):
        return self.role.role == "Operator"

    def isStaff(self):
        return self.auth_user.is_staff

    def getStaticContactInfo(self, use_cache = True):
        return UserInfo().getProfileByID(self, use_cache)

    def getReservations(self, use_cache = True):
        try:
            return NRAOBosDB().getReservationsByUsername(self.username(), use_cache)
        except:
            return []

    def getPeriods(self):
        retval = []
        for i in self.investigator_set.all():
            retval.extend(i.project.getPeriods())
        return sorted(list(Set(retval)))

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

    def getFriends(self):
        "Returns a list of all the friends that are assisting this user."
        projects = [i.project for i in self.investigator_set.all()]
        return list(Set([p.friend.last_name if p.friend else "" for p in projects]))

    def getProjects(self):
        """
        Returns a list of all the project codes for which this user is an
        investigator.
        """
        return [i.project.pcode for i in self.investigator_set.all()]

    def getIncompleteProjects(self):
        "Like getProjects, but only for those that are still not completed."
        return [i.project.pcode for i in self.investigator_set.all() \
            if not i.project.complete]

    def isInvestigator(self, pcode):
        "Is this user an investigator on the given project?"
        return pcode in [i.project.pcode for i in self.investigator_set.all()]

    def isFriend(self, pcode):
        "Is this user a friend for the given project?"
        return pcode in [p.pcode for p in self.project_set.all()]

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
    def clearCachedInfo(self):
        cache.delete(self.username())
        cache.delete(str(self.pst_id)) # Keys are strings only.

    def hasIncompleteProject(self): 
        return any([not i.project.complete \
            for i in self.investigator_set.all()])
        
