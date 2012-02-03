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

from pht.models import *
from pht.utilities import *

class SourceHttpAdapter(object):

    def __init__(self, source = None):
        self.setSource(source)

    def setSource(self, source):
        self.source = source

    def jsonDict(self):
        return {'id'                      : self.source.id
              , 'pcode'                   : self.source.proposal.pcode
              , 'pst_source_id'           : self.source.pst_source_id
              , 'target_name'             : self.source.target_name
              , 'coordinate_system'       : self.source.coordinate_system
              , 'ra'                      : rad2sexHrs(self.source.ra)
              , 'dec'                     : rad2sexDeg(self.source.dec)
              , 'ra_range'                : rad2sexHrs(self.source.ra_range)
              , 'dec_range'               : rad2sexDeg(self.source.dec_range)
              , 'velocity_units'          : self.source.velocity_units
              , 'velocity_redshift'       : self.source.velocity_redshift
              , 'convention'              : self.source.convention
              , 'reference_frame'         : self.source.reference_frame
              , 'observed'                : self.source.observed
              , 'allowed'                 : self.source.allowedToString()
              # raw pst field values (readonly)
              , 'pst_ra'                      : self.source.pst_ra
              , 'pst_dec'                     : self.source.pst_dec
              , 'pst_ra_range'                : self.source.pst_ra_range
              , 'pst_dec_range'               : self.source.pst_dec_range
               }

    def getFloat(self, data, key):
        "Entries for floats can often be blank strings"
        value = None
        value = data.get(key, None)
        if value is None or value == '':
            return None
        else:
            try:
                value = float(value)
            except:
                value = None
            finally:
                return value

    def getSexHrs2rad(self, data, key):
        v = data.get(key, '')
        return sexHrs2rad(v) if v != '' else None

    def getSexDeg2rad(self, data, key):
        v = data.get(key, '')
        return sexDeg2rad(v) if v != '' else None

    def initFromPost(self, data):

        # init new objects before filling in their fields
        self.source = Source()

        # now fill in their fields
        self.updateFromPost(data)

    def updateFromPost(self, data):

        # we can change which proposal this source belongs to
        pcode = data.get('pcode')
        proposal = Proposal.objects.get(pcode = pcode)
        self.source.proposal = proposal

        self.source.pst_source_id = data.get('pst_source_id', 0)
        self.source.target_name = data.get('target_name')
        self.source.coordinate_system = data.get('coordinate_system')
        self.source.velocity_units = data.get('velocity_units')
        self.source.velocity_redshift = data.get('velocity_redshift')
        self.source.convention = data.get('convention')
        self.source.reference_frame = data.get('reference_frame')
        self.source.observed = data.get('observed') == 'true'
        # allowed is a bool, but we get a string
        self.source.allowedFromString(data.get('allowed'))

        self.source.ra = self.getSexHrs2rad(data, 'ra') 
        self.source.dec = self.getSexDeg2rad(data, 'dec')
        self.source.ra_range = self.getSexHrs2rad(data, 'ra_range')
        self.source.dec_range = self.getSexDeg2rad(data, 'dec_range')

        self.source.save()

