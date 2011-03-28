from test_utils              import NellTestCase
from nell.utilities.database              import DBReporter

class TestDBReporter(NellTestCase):

    def test_DBReporter(self):
        "imply make sure that no exceptions are raised."
        db = DBReporter(quiet=True)
        db.report()

