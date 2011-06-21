# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

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



