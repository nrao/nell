from sesshuns.models import *
from reversion.models import Version
from revisionReport import RevisionReport

class ProjectRevReport(RevisionReport):

    def reportProject(self, pcode, time = None, field = None):
        p = first(Project.objects.filter(pcode = pcode))
        self.reportObject(p, time, field)
        #reportObjectDiffs(p)
    
    def reportAllotments(self, pcode, time = None, field = None):
        p = first(Project.objects.filter(pcode = pcode))
        for a in p.allotments.all():
            self.reportObject(a, time, field)
            #reportObjectDiffs(a)
    
    def reportProjectDiffs(self, pcode):
    
        diffs = []
        p = first(Project.objects.filter(pcode = pcode))
        diffs.extend(self.getObjectDiffs(p)) 
        for a in p.allotments.all():
            diffs.extend(self.getObjectDiffs(a))
        for i in p.investigator_set.all():
            diffs.extend(self.getObjectDiffs(i))
        diffs.sort()    
        for d in diffs:
            print "(%s) field %s: %s -> %s" % (d[0], d[1], d[2], d[3])
    
    def reportDeletedProject(self, pcode):
        # we could get the obj we want if we had the PK ID! but we don't ...
        deleted_list = Version.objects.get_deleted(Project)
        for d in deleted_list:
            if d.object_version.object.pcode == pcode:
                self.reportVersion(d)

