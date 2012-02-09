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

from datetime import datetime

from pht.models    import *
from pht.utilities import *

class SessionHttpAdapter(object):

    def __init__(self, session = None):
        self.setSession(session)

    def setSession(self, session):
        self.session = session

    def jsonDict(self, detailed = False):
        sessType = self.session.session_type.type if self.session.session_type is not None else None
        wthrType = self.session.weather_type.type if self.session.weather_type is not None else None
        semester = self.session.semester.semester if self.session.semester is not None else None
        separation = self.session.separation.separation if self.session.separation is not None else None
        grade = self.session.grade.grade if self.session.grade is not None else None
        include, exclude = self.session.get_lst_string()
        
        data = {'id'                      : self.session.id
              , 'name'                    : self.session.name
              , 'pcode'                   : self.session.proposal.pcode
              , 'pst_session_id'          : self.session.pst_session_id
              , 'semester'                : semester 
              , 'session_type'            : sessType
              , 'weather_type'            : wthrType
              , 'separation'              : separation
              , 'grade'                   : grade
              , 'interval_time'           : self.session.interval_time
              , 'constraint_field'        : self.session.constraint_field
              , 'comments'                : self.session.comments
              , 'scheduler_notes'         : self.session.scheduler_notes
              , 'session_time_calculated' : self.session.session_time_calculated
              # allotment
              , 'requested_time'          : self.session.allotment.requested_time
              , 'repeats'                 : self.session.allotment.repeats
              , 'allocated_time'          : self.session.allotment.allocated_time
              , 'semester_time'           : self.session.allotment.semester_time
              , 'period_time'             : self.session.allotment.period_time
              , 'low_freq_time'           : self.session.allotment.low_freq_time
              , 'hi_freq_1_time'          : self.session.allotment.hi_freq_1_time
              , 'hi_freq_2_time'          : self.session.allotment.hi_freq_2_time
              # target
              , 'ra'                      : rad2sexHrs(self.session.target.ra)
              , 'dec'                     : rad2sexDeg(self.session.target.dec)
              , 'center_lst'              : rad2sexHrs(self.session.target.center_lst)
              , 'lst_width'               : rad2sexHrs(self.session.target.lst_width)
              , 'min_lst'                 : rad2sexHrs(self.session.target.min_lst)
              , 'max_lst'                 : rad2sexHrs(self.session.target.max_lst)
              , 'elevation_min'           : rad2sexHrs(self.session.target.elevation_min)
              # session flags
              , 'thermal_night'           : self.session.flags.thermal_night
              , 'rfi_night'               : self.session.flags.rfi_night
              , 'optical_night'           : self.session.flags.optical_night
              , 'transit_flat'            : self.session.flags.transit_flat
              , 'guaranteed'              : self.session.flags.guaranteed
              # hardware
              , 'backends'                : self.session.get_backends()
              , 'receivers'               : self.session.get_receivers()
              , 'receivers_granted'       : self.session.get_receivers_granted()
              # session params
              , "lst_ex"                  : exclude or ""
              , "lst_in"                  : include or ""
              # raw pst field values (readonly)
              , 'pst_min_lst'             : self.session.target.pst_min_lst
              , 'pst_max_lst'             : self.session.target.pst_max_lst
              , 'pst_elevation_min'       : self.session.target.pst_elevation_min
               }
        return data

    def initFromPost(self, data):

        # init new objects before filling in their fields
        self.session = Session()
        # TBF: why do I have to do it this verbose way?
        allotment = Allotment()
        allotment.save()
        self.session.allotment = allotment
        target = Target()
        target.save()
        self.session.target = target 
        flags = SessionFlags()
        flags.save()
        self.session.flags = flags

        # now fill in their fields
        self.updateFromPost(data)

    def getType(self, data, key, fnc, default):
        "Entries for floats & ints can often be blank strings"
        value = None
        value = data.get(key, None)
        if value is None or value == '':
            return default
        else:
            try:
                value = fnc(value)
            except:
                value = default
            finally:
                return value

    def getInt(self, data, key, default = None):
        "Entries for integers can often be blank strings"
        return self.getType(data, key, int, default )

    def getFloat(self, data, key, default = None):
        "Entries for floats can often be blank strings"
        return self.getType(data, key, float, default )

    def getBool(self, data, key):
        "Booleans come in as strings"
        return data.get(key) == 'true'

    def getSexHrs2rad(self, data, key):
        v = data.get(key, '')
        return sexHrs2rad(v) if v != '' else None

    def getSexDeg2rad(self, data, key):
        v = data.get(key, '')
        return sexDeg2rad(v) if v != '' else None


    def updateFromPost(self, data):

        # we can change which proposal this session belongs to
        pcode = data.get('pcode')
        proposal = Proposal.objects.get(pcode = pcode)
        self.session.proposal = proposal

        grade = data.get('grade', '')
        grade = SessionGrade.objects.get(grade = grade) if grade != '' else None
        self.session.grade = grade
        sep = SessionSeparation.objects.get(separation = data.get('separation'))
        self.session.separation = sep
        sessionType = SessionType.objects.get(type = data.get('session_type'))
        self.session.session_type = sessionType
        weatherType = WeatherType.objects.get(type = data.get('weather_type'))
        self.session.weather_type = weatherType
        semester = Semester.objects.get(semester = data.get('semester'))
        self.session.semester = semester
        
        self.session.pst_session_id = self.getInt(data, 'pst_session_id', default = 0) 
        self.session.name = data.get('name')
        self.session.interval_time = self.getFloat(data,'interval_time')
        self.session.constraint_field = data.get('constraint_field')
        self.session.comments = data.get('comments')
        self.session.scheduler_notes = data.get('scheduler_notes')
        self.session.session_time_calculated = self.getBool(data, 'session_time_calculated')
        self.session.save()

        # allotment
        self.session.allotment.repeats = self.getFloat(data, 'repeats') #data.get('repeats')
        self.session.allotment.requested_time = self.getFloat(data, 'requested_time')
        self.session.allotment.allocated_time = self.getFloat(data, 'allocated_time')
        self.session.allotment.semester_time = self.getFloat(data, 'semester_time')
        self.session.allotment.period_time = self.getFloat(data, 'period_time')
        self.session.allotment.low_freq_time = self.getFloat(data, 'low_freq_time')
        self.session.allotment.hi_freq_1_time = self.getFloat(data, 'hi_freq_1_time')
        self.session.allotment.hi_freq_2_time = self.getFloat(data, 'hi_freq_2_time')
        self.session.allotment.save()

        # target
        self.session.target.ra = self.getSexHrs2rad(data,'ra')
        self.session.target.dec = self.getSexDeg2rad(data, 'dec')
        self.session.target.center_lst = self.getSexHrs2rad(data, 'center_lst')
        self.session.target.lst_width = self.getSexHrs2rad(data, 'lst_width')
        self.session.target.min_lst = self.getSexHrs2rad(data, 'min_lst')
        self.session.target.max_lst = self.getSexHrs2rad(data, 'max_lst')
        self.session.target.elevation_min = self.getSexHrs2rad(data, 'elevation_min')
        self.session.target.save()

        # flags
        self.session.flags.thermal_night = self.getBool(data, 'thermal_night')
        self.session.flags.rfi_night = self.getBool(data, 'rfi_night')
        self.session.flags.optical_night = self.getBool(data, 'optical_night')
        self.session.flags.transit_flat =  self.getBool(data, 'transit_flat')
        self.session.flags.guaranteed =  self.getBool(data, 'guaranteed')
        self.session.flags.save()

        # more complex stuff:
        # like LST ranges
        self.update_lst_parameters('lst_ex', data.get('lst_ex'))
        self.update_lst_parameters('lst_in', data.get('lst_in'))
        self.update_backends(data)
        self.update_rcvrs(data)
        self.update_rcvrs_granted(data)

        # done!
        self.session.save()

    def update_rcvrs_granted(self, data):
        "Converts comma-separated string to objects."

        update, rcvrs = self.update_resource_check('receivers_granted'
                                                 , self.session.get_receivers_granted()
                                                 , Receiver
                                                 , data
                                                   )
        if update:                                         
            for r in self.session.receivers_granted.all():
                self.session.receivers_granted.remove(r)
            for r in rcvrs:
                self.session.receivers_granted.add(r)
                self.session.save()

    def update_rcvrs(self, data):
        update, rcvrs = self.update_resource_check('receivers'
                                                 , self.session.get_receivers()
                                                 , Receiver
                                                 , data
                                                   )
        if update:                                         
            for r in self.session.receivers.all():
                self.session.receivers.remove(r)
            for r in rcvrs:
                self.session.receivers.add(r)
                self.session.save()


    def update_backends(self, data):
        update, bcks = self.update_resource_check('backends'
                                                 , self.session.get_backends()
                                                 , Backend
                                                 , data
                                                   )
        if update:                                         
            for b in self.session.backends.all():
                self.session.backends.remove(b)
            for b in bcks:
                self.session.backends.add(b)
                self.session.save()

    def update_resource_check(self, key, currentResource, klass, data):
        """
        Given a list of resources (front or back end), do we
        need to update this session?
        """
        # first, get the string
        resources = data.get(key, None)
        if resources is None:
            return (False, [])
        # we can get a string or a list.
        if resources.__class__.__name__ == 'list':
            rscString = ','.join(resources)
        else:
            rscString = resources
            resources = resources.split(',')
        # if the string sent is identical to what we have, don't do anything
        if rscString == currentResource:
            return (False, [])
        # we'll have to update, so get the new resources
        rs = [klass.objects.get(abbreviation = r.strip()) for r in resources if r != '']
        return (True, rs)

    def update_lst_parameters(self, param, ranges):
        """
        Converts the json representation of the LST include/exclude ranges
        to the model representation.
        """

        if param is None:
            return
        
        pName    = "Exclude" if param == 'lst_ex' else "Include"
        lowParam = Parameter.objects.get(name="LST %s Low" % pName)
        hiParam  = Parameter.objects.get(name="LST %s Hi" % pName)
        for op in self.session.sessionparameter_set.filter(parameter = lowParam):
            op.delete()
        for op in self.session.sessionparameter_set.filter(parameter = hiParam):
            op.delete()
        if ranges is None:
            return

        ranges   = [map(float, r.split('-')) for r in ranges.split(',') if r != '']

        def checkRange(range):
            low, hi = range
            if low >= hi:
                raise NameError("Range not supported: %s >= %s" % (low, hi))
        map(checkRange, ranges)

        # Check for overlaps.
        if any([(low >= low2 and low <= hi2) or (hi <= hi2 and hi >= low2) 
           for low, hi in ranges for low2, hi2 in ranges if low != low2 and hi != hi2]):
           raise NameError("Overlaping ranges are not supported.")
        for low, hi in ranges:
            low_p = SessionParameter.objects.create(session     = self.session
                                                   , parameter   = lowParam
                                                   , float_value = low
                                                   )
            hi_p  = SessionParameter.objects.create(session     = self.session
                                                   , parameter   = hiParam
                                                   , float_value = hi
                                                   )
        
