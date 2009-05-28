from sesshuns.models import *
from datetime        import datetime, timedelta
import math
import MySQLdb as m

class DSS2DSSPrime(object):
    """
    This class is reponsible for transferring specific info from the DSS
    database (perhaps a result of simulations) to the original 'stepping
    stone' DB, DSS'.  
    The original motivation for this has been the request to get the
    Periods created by DSS simulations back into Carl's system.  Carl
    has requested that this information be put in a MySQL DB, so why
    not DSS'?
    """

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "dss"
                     , passwd = "asdf5!"
                     , database = "dss_prime"
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                            )
        self.cursor = self.db.cursor()

    def transfer(self):
        self.transfer_periods()

    def transfer_periods(self):
        """
        Periods in the DSS are most likely the result of running simulations.
        The challenge in transferring them here is to make sure that the 
        Periods' Foriegn Keys to Sessions are correct.
        """

        ps = Period.objects.all()
        for p in ps:
            print p

            # what is the correct session for this period in DSS'?
            s = p.session
            print s.name
            if s.name in ['Fixed Summer Maintenance', 'testing']:
                print "skipping: ", s.name
                continue
            id = s.original_id
            query = "SELECT id, name FROM sessions WHERE original_id = %d" % id
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            assert len(rows) == 1
            dss_prime_session_id = rows[0][0]
            name = rows[0][1]
            print name

            # okay, write it to DSS'!
            query = "INSERT INTO periods VALUES (DEFAULT, %d, '%s', %5.2f)" % \
                (dss_prime_session_id
               , p.start
               , p.duration)
            print query
            self.cursor.execute(query)
             
                
           
