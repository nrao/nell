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
