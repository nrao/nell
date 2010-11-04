from test_utils.NellTestCase import NellTestCase
from nell.tools              import DBReporter

class TestDBReporter(NellTestCase):

    def test_DBReporter(self):
        "imply make sure that no exceptions are raised."
        db = DBReporter(quiet=True)
        db.report()

