from sesshuns.models import *
from reversion.models import Version
from RevisionReport import RevisionReport

class ProjectRevReport(RevisionReport):

    def __init__(self, filename = None):
        super(ProjectRevReport, self).__init__(filename)
        #RevisionReport.__init__(self)
       
        self.relatedClasses = ['Investigator'
                             , 'Allotment'
                              ]

    def reportProject(self, pcode, time = None, field = None):
        self.add("Revision Report for Project: %s\n\n" % pcode)
        p = first(Project.objects.filter(pcode = pcode))
        self.reportObject(p, time, field)
        self.add("\nDiffs:\n")
        self.reportProjectDiffs(pcode)
        self.write()

    def reportProjectForTime(self, pcode, timeStr):
        self.add("Project: %s at %s\n\n" % (pcode, timeStr))
        p = first(Project.objects.filter(pcode = pcode))
        self.reportObjectForTime(p, timeStr)
        self.write()    

    #def reportAllotments(self, pcode, time = None, field = None):
    #    p = first(Project.objects.filter(pcode = pcode))
    #    for a in p.allotments.all():
    #        self.reportObject(a, time, field)
    #        #reportObjectDiffs(a)
    
    def reportProjectDiffs(self, pcode):

        self.add("Differences for Project: %s \n\n" % pcode)
        diffs = []
        p = first(Project.objects.filter(pcode = pcode))
        diffs.extend(self.getObjectDiffs(p)) 
        for a in p.allotments.all():
            diffs.extend(self.getObjectDiffs(a))
        for i in p.investigator_set.all():
            diffs.extend(self.getObjectDiffs(i))
        diffs.sort()    
        for d in diffs:
            self.add("%s\n" % d)
        self.write()    
    
    def reportDeletedProject(self, pcode):
        # we could get the obj we want if we had the PK ID! but we don't ...
        deleted_list = Version.objects.get_deleted(Project)
        for d in deleted_list:
            if d.object_version.object.pcode == pcode:
                self.reportVersion(d)
        self.write()
