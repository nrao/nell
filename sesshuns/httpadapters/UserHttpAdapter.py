from sesshuns.models        import Role
from sesshuns.models.common import first

class UserHttpAdapter (object):

    def __init__(self, user):
        self.user = user

    def load(self, user):
        self.user = user

    def update_from_post(self, fdata):
        role  = first(Role.objects.filter(role = fdata.get('role')))
        self.user.role        = role
        self.user.username    = fdata.get('username')
        sanctioned       = fdata.get('sanctioned')
        self.user.sanctioned  = sanctioned.lower() == 'true' if sanctioned is not None else sanctioned
        self.user.first_name  = fdata.get('first_name')
        self.user.last_name   = fdata.get('last_name')
        self.user.contact_instructions   = fdata.get('contact_instructions')
        self.user.save()

    def jsondict(self):
        projects = ','.join([i.project.pcode for i in self.user.investigator_set.all()])
        return {'id' : self.user.id
              , 'username'   : self.user.username
              , 'first_name' : self.user.first_name
              , 'last_name'  : self.user.last_name
              , 'sanctioned' : self.user.sanctioned
              , 'projects'   : projects
              , 'role'       : self.user.role.role
                }

