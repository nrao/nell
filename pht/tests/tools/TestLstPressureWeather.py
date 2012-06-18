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

from django.test         import TestCase

from datetime import datetime, date, timedelta

from pht.utilities import *
from pht.tools.LstPressureWeather import LstPressureWeather
from pht.tools.LstPressureWeather import Pressures
from pht.models         import Proposal
from pht.models         import Session
from pht.models         import SessionGrade
from pht.httpadapters   import SessionHttpAdapter
from pht.models         import WeatherType
from pht.tests.utils    import *

import numpy

class TestLstPressureWeather(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']

    def setUp(self):

        self.lst = LstPressureWeather()

        # get the one proposal and it's one session
        proposal = Proposal.objects.all()[0]
        s = proposal.session_set.all()[0]

        # give it some values so it will show up in plot
        s.grade = SessionGrade.objects.get(grade = 'A')
        s.weather_type = WeatherType.objects.get(type = 'Poor')
        s.target.min_lst = 0.0
        s.target.max_lst = hr2rad(12.5)
        s.target.save()
        time = 6.5 # hrs
        s.allotment.allocated_time = time # hrs
        s.allotment.save()
        s.save()
        self.session = s

        ps = [0.0]*6
        ps.extend([1.0]*12)
        ps.extend([0.0]*6)
        self.sessPressure = numpy.array(ps)

        self.wPoor = WeatherType.objects.get(type = 'Poor')
        self.wGood = WeatherType.objects.get(type = 'Good')
        self.wExcellent = WeatherType.objects.get(type = 'Excellent')
   
    def createSession(self):
        "Create a new session for the tests"
        p = Proposal.objects.all()[0]
        return createSession(p)
    
    def test_binOpenSession(self):

        # make sure it shows up in poor
        ps = self.lst.binOpenSession(self.session, self.sessPressure)
        exp = Pressures(poor = self.sessPressure)
        self.assertEqual(exp, ps)

        # now make sure it shows up in good
        self.session.weather_type = self.wGood 
        ps = self.lst.binOpenSession(self.session, self.sessPressure)
        exp = Pressures(good = self.sessPressure)
        self.assertEqual(exp, ps)

    def test_binFixedSession(self):

        # make sure it shows up spread around 
        ps = self.lst.binFixedSession(self.session, self.sessPressure)
        exp = Pressures(poor = self.sessPressure*0.5
                      , good = self.sessPressure*0.25
                      , excellent = self.sessPressure*0.25
                        )
        self.assertEqual(exp, ps)

        # distribution is different for good weather
        self.session.weather_type = self.wGood
        ps = self.lst.binFixedSession(self.session, self.sessPressure)
        exp = Pressures(excellent = self.sessPressure*0.5
                      , good = self.sessPressure*0.5)
        self.assertEqual(exp, ps)

        # and pretty simple for excellent weather 
        self.session.weather_type = self.wExcellent
        ps = self.lst.binFixedSession(self.session, self.sessPressure)
        exp = Pressures(excellent = self.sessPressure)
        self.assertEqual(exp, ps)

    def test_binWindowedSession(self):

        self.session.monitoring.window_size = 2
        ps = self.lst.binWindowedSession(self.session, self.sessPressure)
        exp = Pressures(poor = self.sessPressure*0.5
                      , good = self.sessPressure*0.25
                      , excellent = self.sessPressure*0.25
                        )
        self.assertEqual(exp, ps)

        # now change the window size
        self.session.monitoring.window_size = 20
        ps = self.lst.binWindowedSession(self.session, self.sessPressure)
        self.assertEqual(ps.good.tolist(), ps.excellent.tolist())
        exp = Pressures(poor = self.sessPressure*0.75
                      , good = self.sessPressure*0.125
                      , excellent = self.sessPressure*0.125
                        )
        self.assertEqual(exp, ps)

    def test_binSession(self):

        # make sure it shows up in poor
        ps = self.lst.binSession(self.session, self.sessPressure)
        exp = Pressures(poor = self.sessPressure)
        self.assertEqual(exp, ps)


