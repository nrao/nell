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

from test_utils              import NellTestCase
from tools          import UpdateEphemeris
from scheduler.models         import *
from scheduler.tests.utils                   import create_sesshun

class TestUpdateEphemeris(NellTestCase):

    # These aren't unit tests technically speaking - they interact
    # with websites to get some of the ephemeris
    def testUpdate(self):

        up = UpdateEphemeris.UpdateEphemeris()
        up.quietReport = True

        # the no-op
        up.update()
        self.assertEquals(0, len(up.updates))
        self.assertEquals(0, len(up.errors))

        # let's observe Mars!
        s = create_sesshun()
        s.target.system = System.objects.get(name = "Ephemeris")
        s.target.source = "Mars"
        s.target.save()

        # make sure we update it!
        up.update()
        self.assertEquals(1, len(up.updates))
        self.assertEquals(0, len(up.errors))

        # now let's observe a famouse comet
        s.target.source = "C/1995 O1 (Hale-Bopp)"
        s.target.save()
        up.update()
        self.assertEquals(1, len(up.updates))
        self.assertEquals(0, len(up.errors))

        # now let's observe a famouse asteroid
        s.target.source = "Ceres"
        s.target.save()
        up.update()
        self.assertEquals(1, len(up.updates))
        self.assertEquals(0, len(up.errors))

        # make sure we catch errors!
        s.target.source = "Mr. Nubbles!"
        s.target.save()
        up.update()
        self.assertEquals(0, len(up.updates))
        self.assertEquals(1, len(up.errors))

        # cleanup
        s.delete()

    def testUpdateResources(self):
        up = UpdateEphemeris.UpdateEphemeris()
        up.quietReport = True

        self.assertEquals(len(up.specialObjs.keys()), 0)

        up.updateResources()

        # this number may vary when the contents of this website varies
        #self.assertEquals(len(up.specialObjs.keys()), 256)
        self.assertTrue(len(up.specialObjs) > 0)

        # make sure we have something of both types
        types = []
        for key, value in up.specialObjs.items():
            if value[1] not in types:
                types.append(value[1])

        self.assertEquals(len(types), 2)
        self.assertTrue("Comets" in types)
        self.assertTrue("Asteroids" in types)
