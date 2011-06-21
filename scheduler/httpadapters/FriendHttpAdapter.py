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

from scheduler.models import Project, User, Friend

class FriendHttpAdapter (object):

    def __init__(self, friend):
        self.friend = friend

    def load(self, friend):
        self.friend = friend

    def jsondict(self):
        return {"id"         : self.friend.id
              , "name"       : "%s, %s" % (self.friend.user.last_name, self.friend.user.first_name)
              , "required"   : self.friend.required
              , "project_id" : self.friend.project.id
              , "user_id"    : self.friend.user.id
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
        self.friend.project  = project
        self.friend.user     = user
        self.friend.required = fdata.get('required', 'false').lower() == 'true'

        self.friend.save()

    def update_from_post(self, fdata):
        self.init_from_post(fdata)
