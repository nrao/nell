from datetime                  import datetime, timedelta, date
from math                      import asin, acos, cos, sin
from tools                     import TimeAccounting
from django.conf               import settings
from django.db                 import models
from django.http               import QueryDict
from utilities                 import TimeAgent, UserInfo, NRAOBosDB
from utilities                 import ScorePeriod

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

    def jsondict(self):
        return {"id"         : self.id
              , "name"       : "%s, %s" % (self.user.last_name, self.user.first_name)
              , "pi"         : self.principal_investigator
              , "contact"    : self.principal_contact
              , "remote"     : self.user.sanctioned
              , "observer"   : self.observer
              , "priority"   : self.priority
              , "project_id" : self.project.id
              , "user_id"    : self.user.id
               }

    def init_from_post(self, fdata):
        p_id    = int(float(fdata.get("project_id")))
        u_id    = int(float(fdata.get("user_id")))
        project = first(Project.objects.filter(id = p_id)) or first(Project.objects.all())
        user    = first(User.objects.filter(id = u_id)) or first(User.objects.all())
        pi      = fdata.get('pi', 'false').lower() == 'true'
        if pi:
            # Reset any other PIs to False
            for i in Investigator.objects.filter(project = project):
                i.principal_investigator = False
                i.save()
        self.project                = project
        self.user                   = user
        self.observer               = fdata.get('observer', 'false').lower() == 'true'
        self.principal_contact      = fdata.get('contact', 'false').lower() == 'true'
        self.principal_investigator = pi
        self.priority               = int(float(fdata.get('priority', 1)))
        self.save()

        self.user.sanctioned        = fdata.get('remote', 'false').lower() == 'true'
        self.user.save()

    def update_from_post(self, fdata):
        self.init_from_post(fdata)

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

