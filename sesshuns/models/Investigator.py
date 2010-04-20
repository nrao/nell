from datetime                  import datetime, timedelta, date
from math                      import asin, acos, cos, sin
from tools                     import TimeAccounting
from django.conf               import settings
from django.db                 import models
from django.http               import QueryDict
from utilities                 import TimeAgent, UserInfo, NRAOBosDB

import calendar
import pg
from sets                      import Set
import urllib2
import simplejson as json
import sys

from common     import *

from Project  import Project
from User     import User

class Investigator(models.Model):
    project                = models.ForeignKey(Project)
    user                   = models.ForeignKey(User)
    observer               = models.BooleanField(default = False)
    principal_contact      = models.BooleanField(default = False)
    principal_investigator = models.BooleanField(default = False)
    priority               = models.IntegerField(default = 1)

    def __unicode__(self):
        return "%s (%d) for %s; obs : %s, PC : %s, PI : %s" % \
            ( self.user
            , self.user.id
            , self.project.pcode
            , self.observer
            , self.principal_contact
            , self.principal_investigator )

    def name(self):
        return self.user

    def project_name(self):
        return self.project.pcode

    def projectBlackouts(self):
        return sorted([b for b in self.user.blackout_set.all()
                       if b.isActive()])
    
    class Meta:
        db_table  = "investigators"
        app_label = "sesshuns"

