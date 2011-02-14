# The reversion system does not work with unit tests, so, we must
# fake it: here's how it's done.

# The following helper classes need to only expose those objects and 
# fields from the reversion library that are used in PeriodChanges

class RevisionTester:

    def __init__(self, dt = None):

        self.date_created = dt

class VersionTester:

    def __init__(self, fields = {}, dt = None):

        self.field_dict = fields
        self.revision = RevisionTester(dt = dt)

    #def __str__(self):
    #    print "VersionTester: " #Keys = %s" % ",".join(self.field_dict.keys())


class RevisionUtilityTester:

    """
    Usage: init PeriodChanges with test = True, then supply the
    PeriodChange object's revision's versions and diffs with the 
    approprate dictionaries.
    """

    def __init__(self):

        self.versions = {}
        self.diffs = {}

    def getVersions(self, obj):
        return self.versions[obj]

    def getObjectDiffs(self, obj):
        return self.diffs[obj]



