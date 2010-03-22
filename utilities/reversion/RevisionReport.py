from sesshuns.models import *
import reversion
from reversion.models import Version
from reversion import revision

def tryThis():
    s = getSession("BB240", "BB240-02") 
    vs = Version.objects.get_for_object(s) 
    for v in vs:
        print ""
        print "revision on: ", v.revision.date_created
        for vv in v.revision.version_set.all():
            print "    ", v

class RevisionReport:

    def __init__(self):

        self.relatedClasses = []

    def reportObjectForTime(self, obj, timeStr):
    
        # ex: 010-03-19 09:35:45
        dt = datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
        self.reportObjectAtTime(obj, time = dt)
    
    def reportObject(self, obj, time = None, field = None):
    
        if time is None:
            self.reportObjectHistory(obj, field)
        else:
            self.reportObjectAtTime(obj, time, field)
    
    def reportObjectAtTime(self, obj, time, field = None):
    
        try:
            v = Version.objects.get_for_date(obj, time)
        except:
            print "could not find obj at time: ", time
            print "retrieving initial version: "
            v = Version.objects.get_for_object(obj)[0]
    
        self.reportVersion(v, field)
    
    def reportObjectHistory(self, obj, field = None):
    
        vs = Version.objects.get_for_object(obj)
    
        for v in vs:
            self.reportVersion(v, field)
    
    def getObjectDiffs(self, obj):
    
        diffs = []
    
        vs = Version.objects.get_for_object(obj)
    
        if len(vs) < 2:
            #print "No diffs to compute"
            return diffs
    
        vprev = vs[0]
        for v in vs[1:]:
            ds = self.diffVersions(vprev, v)
            for d in ds:
                diffs.append(d)
            vprev = v
    
        return diffs    
    
    def reportObjectDiffs(self, obj):
    
        diffs = self.getObjectDiffs(obj)
        for d in diffs:
            print "(%s) field %s: %s -> %s" % (d[0], d[1], d[2], d[3])
    
    def areEqual(self, v1, v2):
        "Simple compare, unless these are floats"
        epsilon = 1e-5
        floatType = type(3.14)
        if type(v1) == floatType:
            return abs(v1 - v2) < epsilon
        else:
            return v1 == v2
    
    def diffVersions(self, v1, v2):
    
        diffs = []
        keys = v1.field_dict.keys()
        for key in keys:
            value1 = v1.field_dict[key]
            value2 = v2.field_dict[key]
            if not self.areEqual(value1, value2):
                dt = v2.revision.date_created.strftime("%Y-%m-%d %H:%M:%S")
                diffs.append((dt, key, value1, value2))
    
        return diffs
    
    def reportVersion(self, v, field = None):
    
        vs = [v]
        vs.extend(self.getRelatedVersions(v))
        for v in vs:
            self.reportTheVersion(v, field)

    def getRelatedVersions(self, ver):

        vs = []
        rvs = ver.revision.version_set.all()
        for v in rvs:
            #print v.object_version.object.__class__.__name__
            if v.object_version.object.__class__.__name__ in self.relatedClasses:
                vs.append(v)
        return vs

    def reportTheVersion(self, v, field = None):

        dt = v.revision.date_created.strftime("%Y-%m-%d %H:%M:%S")
        cmt = v.revision.comment
        info = None
        if field is None:
            #info = "%s" % v.object_version.object
            info = v.field_dict
        else:
            info = v.field_dict.get(field, None)
            if info is not None:
                info = "%s : %s" % (field, info)
        if info is not None:
            print ""
            print "WHEN: %s" % dt
            print "%s" % cmt
            print "WHAT: %s" % v.object_version.object.__class__.__name__
            if field is None:
                print "Details:"
                for k, v in info.items():
                    print "%s : %s" % (k, v)
            else:
                print "%s" % info
            #print "%15s %20s %s" % (dt, cmt, info)
    
    def getRcvr(self, rcvrId):
        return first(Receiver.objects.filter(id = rcvrId))
    
    def getRcvrAbbr(self, rcvrId):
        return self.getRcvr(rcvrId).abbreviation
    
    def interpretRcvrGrpDiff(self, diff):
        start = diff[0]
        key = diff[1]
        rg1 = self.interpretRcvrGrp(diff[2])
        rg2 = self.interpretRcvrGrp(diff[3])
        return (start, key, rg1, rg2)
    
    def interpretRcvrGrp(self, rg):
        return [self.getRcvrAbbr(r) for r in rg]
    

        
            
                    
