import unittest
import pg
from sesshuns.models import *
from nell_server import settings

class TestSesshun(unittest.TestCase):

    def setUp(self):
        dbname = "test_" + settings.DATABASE_NAME
        c = pg.connect(user = "dss", dbname = dbname)
        sql = open("populate_db.sql").read()
        c.query(sql)
        c.close()
        
    def test_create(self):
        fdata = {"total_time": "3"
               , "req_max": "6"
               , "name": "Low Frequency With No RFI"
               , "grade": "4"
               , "science": "pulsar"
               , "orig_ID": "0"
               , "between": "0"
               , "proj_code": "GBT09A-001"
               , "PSC_time": "2"
               , "sem_time": 0.0
               , "req_min": "2"
               , "freq": "6"
               , "type": "open"
               , "id": 2}
        s = Sesshun()
        s.init_from_json(fdata)
        s.save()
        self.assertEqual(s.allotment.total_time, fdata["total_time"])
        self.assertEqual(s.name, fdata["name"])

