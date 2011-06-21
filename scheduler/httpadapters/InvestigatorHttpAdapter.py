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

from scheduler.models import Project, User, Investigator

class InvestigatorHttpAdapter (object):

    def __init__(self, investigator):
        self.investigator = investigator

    def load(self, investigator):
        self.investigator = investigator

    def jsondict(self):
        return {"id"         : self.investigator.id
              , "name"       : "%s, %s" % (self.investigator.user.last_name, self.investigator.user.first_name)
              , "pi"         : self.investigator.principal_investigator
              , "contact"    : self.investigator.principal_contact
              , "remote"     : self.investigator.user.sanctioned
              , "observer"   : self.investigator.observer
              , "priority"   : self.investigator.priority
              , "project_id" : self.investigator.project.id
              , "user_id"    : self.investigator.user.id
               }

    def init_from_post(self, fdata):
        p_id    = int(float(fdata.get("project_id")))
        u_id    = int(float(fdata.get("user_id")))
        try:
            project = Project.objects.get(id = p_id)
        except Project.DoesNotExist:
            project = Project.objects.all()[0]
        try:
            user    = User.objects.get(id = u_id)
        except User.DoesNotExist:
            user    = User.objects.all()[0]
        pi      = fdata.get('pi', 'false').lower() == 'true'
        if pi:
            # Reset any other PIs to False
            for i in Investigator.objects.filter(project = project):
                i.principal_investigator = False
                i.save()
        self.investigator.project                = project
        self.investigator.user                   = user
        self.investigator.observer               = fdata.get('observer', 'false').lower() == 'true'
        self.investigator.principal_contact      = fdata.get('contact', 'false').lower() == 'true'
        self.investigator.principal_investigator = pi
        self.investigator.priority               = int(float(fdata.get('priority', 1)))
        self.investigator.save()

    def update_from_post(self, fdata):
        self.init_from_post(fdata)
        self.investigator.user.sanctioned        = fdata.get('remote', 'false').lower() == 'true'
        self.investigator.user.save()
