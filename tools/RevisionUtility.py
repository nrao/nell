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

import reversion
from reversion.models import Version
from reversion import revision
from utilities.VersionDiff import VersionDiff

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

    def removeFieldFromVersions(self, modelName, field):
        """
        A major flaw with the revision library: when a model changes
        there can be trouble interpreting the historical versions.
        Specifically, when a model drops a field, the old versions
        containing that field cause an excpetion when trying to 
        use some of the more useful methods.
        One can use this method to remove those legacy fields, but 
        of course, the history of that field is then lost.
        Note: model name should be of the form 'scheduler.allotment'.
        """

        count = 0
        vs = Version.objects.filter(serialized_data__contains = modelName)
        for v in vs:
            new_data = self.removeFieldName(v.serialized_data, field)
            if new_data is not None:
                v.serialized_data = new_data 
                v.save()
                count += 1
        print "Removed %d occurances of %s for model %s" % (count, field, modelName)

    def removeFieldName(self, serialized_data, field):
        return self.substituteFieldName(serialized_data, field, "")

    def substituteFieldName(self, serialized_data, field, substitute):
        """
        Ex: [{"pk": 504, "model": "scheduler.allotment",
             "fields": {"total_time": "42", "max_semester_time": "42",
             "ignore_grade": false, "psc_time": "42", "grade": "4"}}]
        May need  '"ignore_grade": false,' removed, because the 
        Allotment model no longer has that field.
        """
        # isolate the inner 'fields' dictionary
        fieldInd = serialized_data.find('fields')
        justFields = serialized_data[(fieldInd+10):-3]
        # split up the key value pairs of this dict
        keyValues = justFields.split(",")
        replace = None
        # look for the key we want to replace, and find what
        # i't key-value looks like
        for keyValue in keyValues:
            parts = keyValue.split(":")
            key = parts[0].strip()[1:-1]
            if key == field:
                replace = keyValue + ","
        if replace is not None:
            return serialized_data.replace(replace, substitute)
        else:    
            return replace    

    def changeModelNameInVersions(self, content_type_id, bad_name, good_name):
        """
        Ex: select * from reversion_version where id = 66415;
        66415 |       18992 | 678       |              62 | json   | [{"pk": 678, "mode
l": "auth.user", "fields": {"username": "jhewitt", "first_name": "John", "last_n
ame": "Hewitt", "sanctioned": false, "pst_id": 264, "original_id": null, "auth_u
ser": 216, "role": 2, "contact_instructions": null}}] | Hewitt, John |    1

        That model, auth.user is wrong! it should be changed to scheduler.user.
        """
        vs = Version.objects.filter(serialized_data__contains = bad_name
                                  , content_type = content_type_id
                                   )
        count = 0                           
        for v in vs:
            bad_field  = '"model": "%s"' % bad_name
            good_field = '"model": "%s"' % good_name
            new_serialized_data = v.serialized_data.replace(bad_field, good_field)
            if new_serialized_data is not None:
                v.serialized_data = new_serialized_data
                v.save()
                count += 1
        print "Updated %d model names for content_type_id %d" % (count, content_type_id)        
            
