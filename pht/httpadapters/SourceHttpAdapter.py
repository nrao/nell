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

from pht.models     import *
from pht.utilities  import *
from PhtHttpAdapter import PhtHttpAdapter

class SourceHttpAdapter(PhtHttpAdapter):

    def __init__(self, source = None):
        self.setSource(source)

    def setSource(self, source):
        self.source = source

    def jsonDict(self):

        sys = self.get(self.source.coordinate_system, 'system')
        epoch = self.get(self.source.coordinate_epoch, 'epoch')
        vUnits = self.get(self.source.velocity_units, 'type')
        con = self.get(self.source.convention, 'convention')
        ref = self.get(self.source.reference_frame, 'frame')

        return {'id'                      : self.source.id
              , 'pcode'                   : self.source.proposal.pcode
              , 'pst_source_id'           : self.source.pst_source_id
              , 'target_name'             : self.source.target_name
              , 'ra'                      : rad2sexHrs(self.source.ra)
              , 'dec'                     : rad2sexDeg(self.source.dec)
              , 'ra_range'                : rad2sexHrs(self.source.ra_range)
              , 'dec_range'               : rad2sexDeg(self.source.dec_range)
              , 'coordinate_system'       : sys
              , 'coordinate_epoch'        : epoch
              , 'velocity_units'          : vUnits 
              , 'velocity_redshift'       : self.source.velocity_redshift
              , 'convention'              : con
              , 'reference_frame'         : ref
              , 'observed'                : self.source.observed
              , 'allowed'                 : self.source.allowedToString()
              # raw pst field values (readonly)
              , 'pst_ra'                      : self.source.pst_ra
              , 'pst_dec'                     : self.source.pst_dec
              , 'pst_ra_range'                : self.source.pst_ra_range
              , 'pst_dec_range'               : self.source.pst_dec_range
               }


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
        self.source.velocity_redshift = data.get('velocity_redshift')
        self.source.observed = data.get('observed') == 'true'
        # allowed is a bool, but we get a string
        self.source.allowedFromString(data.get('allowed'))

        
        self.source.coordinate_system = self.getEnum(data
                                                   , 'coordinate_system'
                                                   , SourceCoordinateSystem
                                                   , 'system')
        self.source.coordinate_epoch = self.getEnum(data
                                                   , 'coordinate_epoch'
                                                   , SourceCoordinateEpoch
                                                   , 'epoch')
        self.source.velocity_units = self.getEnum(data
                                                , 'velocity_units'
                                                , SourceVelocityType
                                                , 'type')
        self.source.convention = self.getEnum(data
                                            , 'convention'
                                            , SourceConvention
                                            , 'convention')
        self.source.reference_frame = self.getEnum(data
                                                 , 'reference_frame'
                                                 , SourceReferenceFrame
                                                 , 'frame')

        self.source.ra = self.getSexHrs2rad(data, 'ra') 
        self.source.dec = self.getSexDeg2rad(data, 'dec')
        self.source.ra_range = self.getSexHrs2rad(data, 'ra_range')
        self.source.dec_range = self.getSexDeg2rad(data, 'dec_range')

        self.source.save()

