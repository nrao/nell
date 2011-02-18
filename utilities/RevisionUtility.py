import reversion
from reversion.models import Version
from reversion import revision
from VersionDiff import VersionDiff

class RevisionUtility:

    """
    This class cotains utility functions to help working with the reversion library.
    It's main concern is producing sensible diffs between object versions.
    """

    def getVersions(self, obj):
        return list(Version.objects.get_for_object(obj))

    def getObjectDiffs(self, obj):
        "Returns a list of VersionDiff objects for given object"

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
            if not v1.field_dict.has_key(key) or not v2.field_dict.has_key(key):
                continue
            value1 = v1.field_dict[key]
            value2 = v2.field_dict[key]
            if not self.areEqual(value1, value2):
                dt = v2.revision.date_created #.strftime("%Y-%m-%d %H:%M:%S")
                diff = VersionDiff(dt = dt
                                 , field = key
                                 , value1 = value1
                                 , value2 = value2)
                diffs.append(diff)                                 
    
        return diffs


