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


from pht.utilities  import *
import settings, urllib, urllib2
from django.db import transaction

class PhtHttpAdapter(object):

    @transaction.commit_manually
    def notify(self, proposal):
        transaction.commit()

        try:
            fh = urllib2.urlopen(settings.PHT_UPDATES_URL + '?proposalIds=' + str(proposal.id))
            #fh = urllib2.urlopen(settings.PHT_UPDATES_URL
            #                   , data = urllib.urlencode({'proposalIds' : proposal.id}))
        except urllib2.URLError:
            pass

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

    def getEnum(self, data, dataField, klass, field):
        """
        Common code used for grabbing a value from the response,
        getting the proper enumerated object from the DB (or None)
        and returning it.
        """
        v = data.get(dataField, '')
        if v is not None and v != '':
            # would do an objects.get if we could
            v = klass.objects.extra(where=["%s = '%s'" % (field, v)])
            assert len(v) == 1 
            v = v[0]    
        else:
            v = None
        return v
        
    def getSexHrs2rad(self, data, key):
        v = data.get(key, '')
        return sexHrs2rad(v) if v != '' else None

    def getSexDeg2rad(self, data, key):
        v = data.get(key, '')
        return sexDeg2rad(v) if v != '' else None

    def cleanPostData(self, data):
        bad_keys = [k for k, v in data.iteritems() if v == '']
        for bk in bad_keys:
            data.pop(bk)
        return data

    def get(self, obj, attr):
        "Can't get something from nothing.  Really."
        return obj.__getattribute__(attr) if obj is not None else None

    def formatDate(self, dt):
        return str(dt.strftime('%m/%d/%Y'))
