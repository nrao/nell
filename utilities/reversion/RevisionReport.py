from sesshuns.models import *
import reversion
from reversion.models import Version
from reversion import revision
from VersionDiff import VersionDiff

class RevisionReport(object):

    def __init__(self, filename = None):

        # related to actual reporting
        self.reportLines = []
        self.quietReport = False
        self.filename = filename

        # related to object revisions
        self.relatedClasses = []

    def add(self, lines):
        "For use with printing reports"
        if not self.quietReport:
            print lines
        self.reportLines += lines

    def write(self):        
        # write it out
        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)

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
    
        self.reportVersions(v, field)
    
    def reportObjectHistory(self, obj, field = None):
    
        vs = Version.objects.get_for_object(obj)
    
        for v in vs:
            self.reportVersions(v, field)
    
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
            self.add("%s\n" % d)
        #    print "(%s) field %s: %s -> %s" % (d[0], d[1], d[2], d[3])
    
    def areEqual(self, v1, v2):
        "Simple compare, unless these are floats"
        epsilon = 1e-5
        floatType = type(3.14)
        if type(v1) == floatType:
            return abs(v1 - v2) < epsilon
        else:
            return v1 == v2
    
    def diffVersions(self, v1, v2):
        "Are there any fields in these two versions which are different?"
        diffs = []
        keys = v1.field_dict.keys()
        for key in keys:
            value1 = v1.field_dict[key]
            value2 = v2.field_dict[key]
            if not self.areEqual(value1, value2):
                dt = v2.revision.date_created #.strftime("%Y-%m-%d %H:%M:%S")
                diff = VersionDiff(dt = dt
                                 , field = key
                                 , value1 = value1
                                 , value2 = value2)
                diffs.append(diff)                                 
                #diffs.append((dt, key, value1, value2))
    
        return diffs
    
    def reportVersions(self, v, field = None):
        "Reports this version and 'related' versions"
        vs = [v]
        vs.extend(self.getRelatedVersions(v))
        for v in vs:
            self.reportVersion(v, field)

    def getRelatedVersions(self, ver):
        """
        Usually we want to know about other objects that are part of this
        version's revision.  For example, when a session is modified through
        its JSON service, all it's related objects are of interest also.
        """
        #vs = []
        rvs = ver.revision.version_set.all()
        vs = [v for v in rvs if v.object_version.object.__class__.__name__  in \
            self.relatedClasses]
        #for v in rvs:
        #    if v.object_version.object.__class__.__name__ in \
        #        self.relatedClasses:
        #        vs.append(v)
        return vs

    def reportVersion(self, v, field = None):

        dt = v.revision.date_created.strftime("%Y-%m-%d %H:%M:%S")
        cmt = v.revision.comment
        info = None
        if field is None:
            info = v.field_dict
        else:
            info = v.field_dict.get(field, None)
            if info is not None:
                info = "%s : %s" % (field, info)
        if info is not None:
            self.add("\n")
            self.add("WHEN: %s\n" % dt)
            self.add("%s\n" % cmt)
            self.add("WHAT: %s\n" % v.object_version.object.__class__.__name__)
            if field is None:
                self.add("Details:\n")
                for k, v in info.items():
                    self.add("%s : %s\n" % (k, v))
            else:
                self.add("%s\n" % info)
    
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
    

        
            
                    
