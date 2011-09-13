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

from scheduler.models                    import Role
from nell.utilities.FormatExceptionInfo import formatExceptionInfo, printException

class UserHttpAdapter(object):

    def __init__(self, user):
        self.user = user

    def load(self, user):
        self.user = user

    def init_from_post(self, fdata):
        self.update_from_post(fdata)

    def update_from_post(self, fdata):
        self.user.original_id = int(float(fdata.get('original_id', 0)))
        pst_id_str            = fdata.get('pst_id', None)
        self.user.pst_id      = int(float(pst_id_str)) if pst_id_str is not None else None
        sanctioned            = fdata.get('sanctioned', "")
        self.user.sanctioned  = sanctioned.lower() == 'true' if sanctioned is not None else sanctioned
        self.user.first_name  = fdata.get('first_name', "")
        self.user.last_name   = fdata.get('last_name', "")
        self.user.contact_instructions   = fdata.get('contact_instructions', "")

        # Roles.  These should be updated individually *without* first
        # clearing out all the user's roles (using
        # user.roles.clear()), as the scheduler UI may not be handling
        # all possible roles and clearing them would delete roles not
        # handled by the UI.
        def update_role(user, fdata, role_key, role_name):
            try:
                if fdata.get(role_key, '') == 'true':
                    user.addRole(role_name)
                else:
                    user.removeRole(role_name)
            except:
                # printException(formatExceptionInfo())
                pass

        update_role(self.user, fdata, 'admin', 'Administrator')
        update_role(self.user, fdata, 'observer', 'Observer')
        update_role(self.user, fdata, 'operator', 'Operator')
        update_role(self.user, fdata, 'friend', 'Friend')
        update_role(self.user, fdata, 'staff', 'Staff')

        if self.user.auth_user is None:
            try:
                from django.contrib.auth.models import User as AuthUser
                # only in tests will we pass down a username
                username = fdata.get('username', '')
                if username == '' and self.user.pst_id is not None:
                    username = self.user.username()
                self.user.auth_user = \
                    AuthUser(username = username
                           , password = "!"
                            )
                self.user.auth_user.save()
                self.user.save()
                #  Note:  Why is this necessary?  Should be able to
                #  self.user.auth_user = self.user.auth_user?
                self.user.auth_user_id = self.user.auth_user.id
                self.user.save()
            except:
                pass
                #printException(formatExceptionInfo())

    def jsondict(self):
        projects = ','.join([i.project.pcode for i in self.user.investigator_set.all()])
        return {'id'                   : self.user.id
              , 'original_id'          : self.user.original_id
              , 'pst_id'               : self.user.pst_id
              , 'username'             : self.user.username() # read-only
              , 'sanctioned'           : self.user.sanctioned
              , 'first_name'           : self.user.first_name
              , 'last_name'            : self.user.last_name
              , 'contact_instructions' : self.user.contact_instructions
              , 'admin'                : self.user.hasRole("Administrator")
              , 'observer'             : self.user.hasRole("Observer")
              , 'operator'             : self.user.hasRole("Operator")
              , 'friend'               : self.user.hasRole("Friend")
              , 'staff'                : self.user.hasRole("Staff")
              , 'projects'             : projects
                }

