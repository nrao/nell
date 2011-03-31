from test_utils              import NellTestCase
from sesshuns.models         import *
from scheduler.models        import *


class TestMaintenanceActivity(NellTestCase):
    def setUp(self):
        super(TestMaintenanceActivity, self).setUp()
        self.location = "Upstairs, Downstairs"
        self.subject = "Test Maintenance Activity"
        self.desc = "Doing a bunch of impossible stuff!"
        # receivers for receiver swap
        old_receiver = Receiver.objects.filter(id = 8)[0]
        new_receiver = Receiver.objects.filter(name = "Rcvr26_40")[0]
        #zpectrometer backend
        zpect_be = Backend.objects.filter(abbreviation = "Zpect")[0]
        # a couple of users...
        u = User()
        u.username = "ncreager"
        u.last_name = "Creager"
        u.first_name = "Nona"
        u.role = Role.objects.all()[0]
        u.save()
        u = User()
        u.username = "pcreager"
        u.last_name = "Creager"
        u.first_name = "Phaedra"
        u.role = Role.objects.all()[0]
        u.save()
        #create a maintenance activity
        ma = Maintenance_Activity(subject = self.subject)
        ma.save()
        ma.set_location(self.location)
        ma.set_telescope_resource(Maintenance_Telescope_Resources.objects.filter(id = 6)[0])
        ma.set_software_resource(Maintenance_Software_Resources.objects.filter(id = 5)[0])
        ma.add_receiver(old_receiver)
        ma.add_receiver(new_receiver)
        ma.add_backend("DCR") # can name the backend, or...
        ma.add_backend(zpect_be) # add a backend object
        ma.add_receiver_change(old_receiver, new_receiver)
        ma.set_description(self.desc)
        ma.contacts = self.get_user_name(u)
        ma.save()

    def get_user_name(self, u):
        if u:
            if u.first_name and u.last_name:
                user = u.last_name + ", " + u.first_name
            else:
                user = u.username()
        else:
            user = "anonymous"

        return user


    def tearDown(self):
        super(TestMaintenanceActivity, self).tearDown()

    def test_subject(self):
        ma = Maintenance_Activity.objects.all()[0]
        subject = ma.get_subject()
        self.assertEqual(subject, self.subject)
        new_subject = "New Maintenance Subject"
        ma.set_subject(new_subject)
        ma2 = Maintenance_Activity.objects.get(id = ma.id)
        # subject should still be old subject, 'set_subject' doesn't save
        self.assertEqual(ma2.get_subject(), self.subject)
        ma.save()
        ma2 = Maintenance_Activity.objects.get(id = ma.id)
        self.assertEqual(ma2.get_subject(), new_subject)

    def test_location(self):
        ma = Maintenance_Activity.objects.all()[0]
        location = ma.get_location()
        self.assertEqual(location, self.location)
        new_location = "attic"
        ma.set_location(new_location)
        ma2 = Maintenance_Activity.objects.get(id = ma.id)
        # location should still be old location, 'set_location' doesn't save
        self.assertEqual(ma2.get_location(), self.location)
        ma.save()
        ma2 = Maintenance_Activity.objects.get(id = ma.id)
        self.assertEqual(ma2.get_location(), new_location)

    def test_telescope_resource(self):
        ma = Maintenance_Activity.objects.all()[0]
        resource = ma.get_telescope_resource()
        self.assertEqual(resource.id, 6)

    def test_software_resource(self):
        ma = Maintenance_Activity.objects.all()[0]
        resource = ma.get_software_resource()
        self.assertEqual(resource.id, 5)

    def test_receivers(self):
        ma = Maintenance_Activity.objects.all()[0]
        rcvrs = ma.get_receivers()
        self.assertEqual(len(rcvrs), 2)
        self.assertEqual(rcvrs[0].name, "Rcvr1_2")
        self.assertEqual(rcvrs[1].name, "Rcvr26_40")

    def test_backends(self):
        ma = Maintenance_Activity.objects.all()[0]
        be = ma.get_backends()
        self.assertEqual(len(be), 2)
        self.assertEqual(be[0].abbreviation, "DCR")
        self.assertEqual(be[1].abbreviation, "Zpect")

    def test_receiver_changes(self):
        ma = Maintenance_Activity.objects.all()[0]
        rc = ma.get_receiver_changes()
        self.assertEqual(len(rc), 1)
        self.assertEqual(rc[0].down_receiver.name, "Rcvr1_2")
        self.assertEqual(rc[0].up_receiver.name, "Rcvr26_40")

    def test_description(self):
        ma = Maintenance_Activity.objects.all()[0]
        desc = ma.get_description()
        self.assertEqual(desc, self.desc)

    def test_contacts(self):
        ma = Maintenance_Activity.objects.all()[0]
        contacts = ma.contacts
        self.assertEqual(contacts, "Creager, Phaedra")

    def _add_approval(self):
        ma = Maintenance_Activity.objects.all()[0]
        u = User.objects.filter(first_name = "Nona")[0]
        ma.add_approval(u)
        ma.save()

    def _add_modification(self):
        ma = Maintenance_Activity.objects.all()[0]
        u = User.objects.filter(first_name = "Phaedra")[0]
        ma.add_modification(u)
        ma.save()

    def test_approval(self):
        ma = Maintenance_Activity.objects.all()[0]
        self.assertEqual(ma.approved, False)
        self.assertEqual(len(ma.get_approvals()), 0)
        self._add_approval()
        ma = Maintenance_Activity.objects.all()[0]
        self.assertEqual(ma.approved, True)
        self.assertEqual(len(ma.get_approvals()), 1)

    def test_modification(self):
        self._add_approval()
        ma = Maintenance_Activity.objects.all()[0]
        self.assertEqual(ma.approved, True)
        self._add_modification()
        ma = Maintenance_Activity.objects.all()[0]
        self.assertEqual(ma.approved, False)
        self.assertEqual(len(ma.get_modifications()), 1)

