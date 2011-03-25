from nell.utilities             import TimeAccounting
from scheduler.models        import Allotment, Project_Allotment, Project_Type, Semester, User

class ProjectHttpAdapter (object):

    def __init__(self, project):
        self.project = project

    def load(self, project):
        self.project = project

    def init_from_post(self, fdata):
        self.update_from_post(fdata)

    def update_from_post(self, fdata):
        fproj_type = fdata.get("type", "science")
        p_type     = Project_Type.objects.get(type = fproj_type)
        fsemester  = fdata.get("semester", "09C")
        semester   = Semester.objects.get(semester = fsemester)
        try:
            f_lname, f_fname = fdata.get("friend", "").split(", ")
        except ValueError:
            f_lname, f_fname = ("", "")

        self.project.semester         = semester
        self.project.project_type     = p_type
        self.project.pcode            = fdata.get("pcode", "")
        self.project.name             = fdata.get("name", "")
        self.project.thesis           = fdata.get("thesis", "false") == "true"
        self.project.complete         = fdata.get("complete", "false") == "true"
        self.project.blackouts        = fdata.get("blackouts", "false") == "true"
        self.project.notes            = fdata.get("notes", "")
        self.project.schedulers_notes = fdata.get("schd_notes", "")

        self.project.save()

        totals   = map(float, [t for t in fdata.get("total_time", "0.0").split(', ') if t != ''])
        num_new = len(totals)
        pscs     = map(float, [p for p in fdata.get("PSC_time", "0.0").replace(' ', '').split(',') if p != ''])
        max_sems = map(float, [m for m in fdata.get("sem_time", "0.0").split(', ') if m != ''])
        grades   = map(float, [g for g in fdata.get("grade", "4.0").split(', ') if g != ''])
        
        assert num_new == len(pscs) and \
               num_new == len(max_sems) and \
               num_new == len(grades)

        num_cur = self.project.allotments.count()
        if num_new > num_cur:
            for i in range(num_new - num_cur):
                a = Allotment(psc_time = 0.0
                            , total_time = 0.0
                            , max_semester_time = 0.0
                            , grade             = 0.0
                              )
                a.save()

                pa = Project_Allotment(project = self.project, allotment = a)
                pa.save()
        elif num_new < num_cur:
            for a in self.project.allotments.all()[:(num_cur - num_new)]:
                a.delete()
                
        allotment_data = zip(totals, pscs, max_sems, grades)
        for data, a in zip(allotment_data, self.project.allotments.all()):
            t, p, m, g = data
            a.total_time        = t
            a.psc_time          = p
            a.max_semester_time = m
            a.grade             = g
            a.save()
        
        self.project.save()

    def jsondict(self):
        totals   = ', '.join([str(a.total_time) for a in self.project.allotments.all()])
        pscs     = ', '.join([str(a.psc_time) for a in self.project.allotments.all()])
        max_sems = ', '.join([str(a.max_semester_time) for a in self.project.allotments.all()])
        grades   = ', '.join([str(a.grade) for a in self.project.allotments.all()])

        pi = '; '.join([i.user.name() for i in self.project.investigator_set.all()
                        if i.principal_investigator])
        co_i = '; '.join([i.user.name() for i in self.project.investigator_set.all()
                        if not i.principal_investigator])
        friends =  "; ".join([f.user.name() for f in self.project.friend_set.all()])

        return {"id"           : self.project.id
              , "semester"     : self.project.semester.semester
              , "type"         : self.project.project_type.type
              , "total_time"   : totals
              , "PSC_time"     : pscs
              , "sem_time"     : max_sems
              , "remaining"    : TimeAccounting().getTimeRemaining(self.project)
              , "grade"        : grades
              , "pcode"        : self.project.pcode
              , "name"         : self.project.name
              , "thesis"       : self.project.thesis
              , "blackouts"    : self.project.blackouts
              , "complete"     : self.project.complete
              , "pi"           : pi
              , "co_i"         : co_i
              , "friends"      : friends
              , "notes"        : self.project.notes if self.project.notes is not None else ""
              , "schd_notes"   : self.project.schedulers_notes \
                                 if self.project.schedulers_notes is not None else ""
                }

