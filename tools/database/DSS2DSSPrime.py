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

from scheduler.models import *
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
            #if s.name in ['Fixed Summer Maintenance', 'testing']:
            #    print "skipping: ", s.name
            #    continue
            id = s.original_id
            query = "SELECT id, name FROM sessions WHERE original_id = %d" % id
            print query
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            # should always get at least one or none
            assert len(rows) < 2 
            # because testing and maintenance isn't in dss'
            if p.session.name in ['testing', 'Fixed Summer Maintenance']:
                original_id = 'NULL'
                dss_prime_session_id  = 'NULL'
            else:
                original_id = str(p.session.original_id)
                dss_prime_session_id = str(rows[0][0])
                
            # okay, write it to DSS'!
            # strucutre
            # id - PK
            # session_name- string (to id sessions w/ out ids)
            # original_id - int, can be null (testing & maintenance ~in dss')
            # session_id  - int, can be null
            # start       - datetime
            # duration    - string (cant handle floats)
            query = """
            INSERT INTO periods VALUES
            (DEFAULT, %s, %s, '%s', '%s', %5.2f)
            """ % \
                (original_id
               , dss_prime_session_id
               , s.name
               , p.start
               , p.duration)
            print query
            self.cursor.execute(query)
             
                
           
