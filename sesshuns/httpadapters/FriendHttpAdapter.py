from sesshuns.models import first, Project, User, Friend

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
        project = first(Project.objects.filter(id = p_id)) or first(Project.objects.all())
        user    = first(User.objects.filter(id = u_id)) or first(User.objects.all())
        self.friend.project  = project
        self.friend.user     = user
        self.friend.required = fdata.get('required', 'false').lower() == 'true'

        self.friend.save()

    def update_from_post(self, fdata):
        self.init_from_post(fdata)
