from test_utils.NellTestCase import NellTestCase
from utils                   import create_sesshun, fdata
from sesshuns.models         import *
from sesshuns.httpadapters   import *

class TestSesshun(NellTestCase):

    def setUp(self):
        super(TestSesshun, self).setUp()
        self.sesshun = create_sesshun()

    def test_get_ha_limit_blackouts(self):
        # With default target.
        startdate = datetime.utcnow()
        days      = 5
        r = self.sesshun.get_ha_limit_blackouts(startdate, days)

        t = Target(session    = self.sesshun
                 , system     = first(System.objects.filter(name = "J2000"))
                 , source     = "test source"
                 , vertical   = 2.3
                 , horizontal = 1.0)
        t.save()

        # TBF: Need to write test.

        t.delete()

    def test_create(self):
        expected = first(Sesshun.objects.filter(id = self.sesshun.id))
        self.assertEqual(expected.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(expected.name, fdata["name"])

    def test_init_from_post(self):
        s = Sesshun()
        fdata["receiver"] = "((K & Ku) & L)"
        SessionHttpAdapter(s).init_from_post(fdata)

        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.get_LST_exclusion_string(),fdata["lst_ex"])

        # does this still work if you requery the DB?
        ss = Sesshun.objects.all()
        self.assertEqual(2, len(ss))
        s = ss[1]
        # notice the change in type when we compare this way!
        self.assertEqual(s.allotment.total_time, float(fdata["total_time"]))
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])

    def test_update_from_post(self):
        ss = Sesshun.objects.all()
        s = Sesshun()
        adapter = SessionHttpAdapter(s)
        adapter.init_from_post(fdata)

        self.assertEqual(s.frequency, fdata["freq"])
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.get_LST_exclusion_string(), fdata["lst_ex"])

        # change a number of things and see if it catches it
        ldata = dict(fdata)
        ldata["freq"] = "10"
        ldata["source"] = "new source"
        ldata["total_time"] = "99"
        ldata["enabled"] = "true"
        ldata["transit"] = "true"
        ldata["nighttime"] = "false"
        ldata["lst_ex"] = "2.00-4.00"
        ldata["receiver"] = "(K & (X | (L | C)))"
        ldata["xi_factor"] = 1.76
        adapter.update_from_post(ldata)

        # now get this session from the DB
        ss = Sesshun.objects.all()
        s = ss[1]
        self.assertEqual(s.frequency, float(ldata["freq"]))
        self.assertEqual(s.allotment.total_time, float(ldata["total_time"]))
        self.assertEqual(s.target_set.get().source, ldata["source"])
        self.assertEqual(s.status.enabled, ldata["enabled"] == "true")
        self.assertEqual(s.transit(), ldata["transit"] == "true")
        self.assertEqual(s.nighttime(), None)
        self.assertEqual(s.get_LST_exclusion_string(), ldata["lst_ex"])
        self.assertEqual(s.get_min_eff_tsys_factor(), ldata["xi_factor"])
        self.assertEqual(s.get_elevation_limit(),fdata["el_limit"])
        rgs = s.receiver_group_set.all().order_by('id')
        self.assertEqual(2, len(rgs))
        self.assertEqual(['K']
                       , [r.abbreviation for r in rgs[0].receivers.all().order_by('id')])
        self.assertEqual(['L', 'C', 'X']
                       , [r.abbreviation for r in rgs[1].receivers.all().order_by('id')])

    def test_update_from_post2(self):
        ss = Sesshun.objects.all()
        s = Sesshun()
        adapter = SessionHttpAdapter(s)
        adapter.init_from_post(fdata)

        self.assertEqual(s.frequency, fdata["freq"])
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.target_set.get().source, fdata["source"])
        self.assertEqual(s.status.enabled, fdata["enabled"])
        self.assertEqual(s.original_id, int(fdata["orig_ID"]))

        # check to see if we can handle odd types
        ldata = dict(fdata)
        ldata["freq"] = "10.5"
        ldata["source"] = None
        ldata["total_time"] = "99.9"
        ldata["orig_ID"] = "0.0"
        ldata["enabled"] = "true"
        adapter.update_from_post(ldata)

        # now get this session from the DB
        ss = Sesshun.objects.all()
        s = ss[1]
        self.assertEqual(s.frequency, float(ldata["freq"]))
        self.assertEqual(s.allotment.total_time, float(ldata["total_time"]))
        self.assertEqual(s.target_set.get().source, ldata["source"])
        self.assertEqual(s.status.enabled, True) # "True" -> True
        self.assertEqual(s.original_id, 0) #ldata["orig_ID"]) -- "0.0" -> Int

