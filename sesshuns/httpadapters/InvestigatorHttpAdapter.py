from sesshuns.models import first, Project, User, Investigator

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
        project = first(Project.objects.filter(id = p_id)) or first(Project.objects.all())
        user    = first(User.objects.filter(id = u_id)) or first(User.objects.all())
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

        self.investigator.user.sanctioned        = fdata.get('remote', 'false').lower() == 'true'
        self.investigator.user.save()

    def update_from_post(self, fdata):
        self.init_from_post(fdata)
