from test_utils.NellTestCase import NellTestCase
from sesshuns.models         import Sesshun, Receiver
from sesshuns.httpadapters   import SessionHttpAdapter

class TestReceiver(NellTestCase):

    def setUp(self):
        super(TestReceiver, self).setUp()
        s = Sesshun()
        adapter = SessionHttpAdapter(s)
        adapter.init_from_post({})
        s.save()

    def test_get_abbreviations(self):
        nn = Receiver.get_abbreviations()
        self.assertTrue(len(nn) > 17)
        self.assertEquals([n for n in nn if n == 'Ka'], ['Ka'])

    def test_save_receivers(self):
        s = Sesshun.objects.all()[0]
        rcvr = ''
        adapter = SessionHttpAdapter(s)
        adapter.save_receivers(rcvr)
        rgs = s.receiver_group_set.all()
        self.assertEqual(0, len(rgs))
        rcvr = 'L'
        adapter.save_receivers(rcvr)
        rgs = s.receiver_group_set.all()
        self.assertEqual(1, len(rgs))
        self.assertEqual(rcvr, rgs[0].receivers.all()[0].abbreviation)

        s.receiver_group_set.all().delete()
        adapter.save_receivers('L | (X & S)')
        rgs = s.receiver_group_set.all().order_by('id')
        #print rgs
        # TBF WTF? now it is S, then it is X??
        #print rgs[0].receivers.all()[1].abbreviation
        self.assertEqual(2, len(rgs))
        #print rgs[0].receivers.all()[0].abbreviation
        #print rgs[0].receivers.all()[1].abbreviation
        #print rgs[1].receivers.all()[0].abbreviation
        #print rgs[1].receivers.all()[1].abbreviation
        rs = rgs[0].receivers.all().order_by('id')
        self.assertEqual('L', rs[0].abbreviation)
        self.assertEqual('X', rs[1].abbreviation)
        rs = rgs[1].receivers.all().order_by('id')
        self.assertEqual('L', rs[0].abbreviation)
        self.assertEqual('S', rs[1].abbreviation)

