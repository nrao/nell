from test_utils              import NellTestCase
from nell.utilities          import UpdateEphemeris
from scheduler.models         import *
from scheduler.tests.utils                   import create_sesshun

class TestUpdateEphemeris(NellTestCase):

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

