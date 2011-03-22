from scheduler.models import *
import reversion
from reversion.models import Version
from reversion import revision
#from VersionDiff import VersionDiff
from nell.utilities.RevisionUtility import RevisionUtility

class RevisionReport(object):

    def __init__(self, filename = None):

        # related to actual reporting
        self.reportLines = []
        self.quietReport = False
        self.filename = filename

        # related to object revisions
        self.relatedClasses = []

        self.timeFormat = "%Y-%m-%d %H:%M:%S"

        self.revUtil = RevisionUtility()

    def add(self, lines):
        "For use with printing reports"
        if not self.quietReport:
            print lines
        self.reportLines += lines

    def write(self):        
        "For use with printing reports"
        # write it out
        if self.filename is not None:
            f = open(self.filename, 'w')
            f.writelines(self.reportLines)

    def reportObjectForTime(self, obj, timeStr):
        "Zoom in on the object at just the given time (YY-mm-dd HH:MM:SS)"
    
        # ex: 010-03-19 09:35:45
        dt = datetime.strptime(timeStr, self.timeFormat)
        self.reportObject(obj, time = dt)
    
    def getVersionAtTime(self, obj, time):
    
        try:
            v = Version.objects.get_for_date(obj, time)
        except:
            print "could not find obj at time: ", time
            print "retrieving initial version: "
            v = Version.objects.get_for_object(obj)[0]
        return v    
    
    def reportObject(self, obj, time = None, field = None):
    
        vs = self.getAllVersions(obj, time)
        for v in vs:
            self.reportVersion(v, field)
    
    def getAllVersions(self, obj, time = None):
        "Get all versions related to the given object, full hist. or at time"

        if time is None:
            vs = list(Version.objects.get_for_object(obj))
        else:
            vs = [self.getVersionAtTime(obj, time)]

        
        # what are the versions related by revision?
        related = []
        for v in vs:
            related.extend(self.getRelatedVersions(v))

        # what are the verions of related objs in other revisions?
        children = self.getRelatedObjectVersions(obj, time)

        # put'm all togethor - avoid duplicates
        for c in children:
            if c.id not in [v.id for v in vs]:
                vs.append(c)
        for r in related:
            if r.id not in [v.id for v in vs]:
                vs.append(r)

        # sort by revision date
        vs.sort(key=lambda x: x.revision.date_created)

        return vs

    def getRelatedObjectVersions(self, obj, time = None):
        "Abstract class."
        # Example, if a session is enabled/disabled, this doesn't affect
        # the sesshun obj, but the status obj, so you need to look for 
        # the status versions too
        return []

    def getRelatedVersions(self, ver):
        """
        Usually we want to know about other objects that are part of this
        version's revision.  For example, when a session is modified through
        its JSON service, all it's related objects are of interest also.
        """
        rvs = ver.revision.version_set.all()
        vs = [v for v in rvs if v.object_version.object.__class__.__name__  in \
            self.relatedClasses]
        return vs

    def getObjectDiffs(self, obj):
        self.revUtil.getObjectDiffs(obj)    
  
    
    def reportObjectDiffs(self, obj):
    
        diffs = self.getObjectDiffs(obj)
        for d in diffs:
            self.add("%s\n" % d)
        #    print "(%s) field %s: %s -> %s" % (d[0], d[1], d[2], d[3])
    
    def areEqual(self, v1, v2):
        self.revUtil.areEqual(v1, v2)
    
    def diffVersions(self, v1, v2):
        self.revUtil.diffVersions(v1, v2)
    
    def reportVersion(self, v, field = None):
        "Prints out all the details for a given version."

        dt = v.revision.date_created.strftime(self.timeFormat)
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
        return Receiver.objects.get(id = rcvrId)
    
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

    def getSession(self, pcode, name):
        return Sesshun.objects.get(name = name, project__pcode = pcode)

    def runFromCommandLine(self, args):
        """
        Abstract method that takes sys.args and finds the right top level
        method of this class to call.
        """
        pass 

    def parseOptions(self, args, keys):
        "For use with runFromCommandLine"
        options = {}
        for arg in args:
            parts = arg.split("=")
            if len(parts) != 2:
                return (options, "argument invalid: %s" % arg)
            key = parts[0][1:]
            options[key] = parts[1]
        # do the args passed in match expectations?    
        #for k in options.keys():
        #    if k not in keys:
        #       return (options, "unexpected arg: %s" % k)
        # do the args have all the necessary ones?
        for k in keys:
            if k not in options.keys():
                return (options, "args missing: %s" % k)
        return (options, None)    
    

        
            
                    
