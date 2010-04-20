from sesshuns.models        import Allotment, Project_Allotment, Project_Type, Semester
from sesshuns.models.common import first

class ProjectHttpAdapter (object):

    def __init__(self, project):
        self.project = project

    def load(self, project):
        self.project = project

    def init_from_post(self, fdata):
        self.update_from_post(fdata)

    def update_from_post(self, fdata):
        fproj_type = fdata.get("type", "science")
        p_type     = first(Project_Type.objects.filter(type = fproj_type))
        fsemester  = fdata.get("semester", "09C")
        semester   = first(Semester.objects.filter(semester = fsemester))

        self.project.semester         = semester
        self.project.project_type     = p_type
        self.project.pcode            = fdata.get("pcode", "")
        self.project.name             = fdata.get("name", "")
        self.project.thesis           = fdata.get("thesis", "false") == "true"
        self.project.complete         = fdata.get("complete", "false") == "true"
        self.project.notes            = fdata.get("notes", "")
        self.project.schedulers_notes = fdata.get("schd_notes", "")

        self.project.save()

        totals   = map(float, fdata.get("total_time", "0.0").split(', '))
        pscs     = map(float, fdata.get("PSC_time", "0.0").split(', '))
        max_sems = map(float, fdata.get("sem_time", "0.0").split(', '))
        grades   = map(float, fdata.get("grade", "4.0").split(', '))
        
        assert len(totals) == len(pscs) and \
               len(totals) == len(max_sems) and \
               len(totals) == len(grades)

        num_new = len(totals)
        num_cur = len(self.project.allotments.all())
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

        return {"id"           : self.project.id
              , "semester"     : self.project.semester.semester
              , "type"         : self.project.project_type.type
              , "total_time"   : totals
              , "PSC_time"     : pscs
              , "sem_time"     : max_sems
              , "remaining"    : self.project.getTimeRemaining()
              , "grade"        : grades
              , "pcode"        : self.project.pcode
              , "name"         : self.project.name
              , "thesis"       : self.project.thesis
              , "complete"     : self.project.complete
              , "pi"           : pi
              , "co_i"         : co_i
              , "notes"        : self.project.notes if self.project.notes is not None else ""
              , "schd_notes"   : self.project.schedulers_notes \
                                 if self.project.schedulers_notes is not None else ""
                }

