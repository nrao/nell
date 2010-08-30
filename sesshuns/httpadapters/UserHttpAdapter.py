from sesshuns.models                    import Role
from sesshuns.models.common             import first
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
        self.user.pst_id      = int(float(fdata.get('pst_id', 0)))
        self.user.username    = fdata.get('username', "")
        sanctioned            = fdata.get('sanctioned', "")
        self.user.sanctioned  = sanctioned.lower() == 'true' if sanctioned is not None else sanctioned
        self.user.first_name  = fdata.get('first_name', "")
        self.user.last_name   = fdata.get('last_name', "")
        self.user.contact_instructions   = fdata.get('contact_instructions', "")
        role                  = first(Role.objects.filter(role = fdata.get('role', 'Observer')))
        self.user.role        = role
        self.user.save()

        if self.user.auth_user is None:
            try:
                from django.contrib.auth.models import User as AuthUser
                self.user.auth_user = \
                    AuthUser(username = fdata.get('username', "")
                           , password = "!"
                            )
                self.user.auth_user.save()
                self.user.save()
                #  TBF  Why is this necessary?
                self.user.auth_user_id = self.user.auth_user.id
                self.user.save()
            except:
                printException(formatExceptionInfo())

        staff = fdata.get('staff')
        self.user.auth_user.is_staff = staff.lower() == 'true' if staff is not None else False
        self.user.auth_user.save()

    def jsondict(self):
        projects = ','.join([i.project.pcode for i in self.user.investigator_set.all()])
        return {'id' : self.user.id
              , 'original_id' : self.user.original_id
              , 'pst_id'      : self.user.pst_id
              , 'username'    : self.user.username
              , 'sanctioned'  : self.user.sanctioned
              , 'first_name'  : self.user.first_name
              , 'last_name'   : self.user.last_name
              , 'contact_instructions'  : self.user.contact_instructions
              , 'role'        : self.user.role.role
              , 'staff'       : self.user.auth_user.is_staff if self.user.auth_user is not None else False
              , 'projects'    : projects
                }

