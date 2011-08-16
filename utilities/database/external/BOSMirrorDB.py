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

import MySQLdb as m
from datetime import datetime, timedelta

class BOSMirrorDB:
    """
    This class is responsible for reading user info from the mirror of
    the BOS DB available in Green Bank.  This is a read-only, MySql DB,
    so we decided it wasn't worth the effort to incorporate this DB
    into our model.
    Take special care with the identification of users.  In the BOS,
    the table.field "cas_user.global_id" does not actually hold the
    value of the 'global id' (the PK of the person table in the PST),
    but rather the 'authentication id' (the PK of the userAuthentication
    table in the PST).
    """

    # mysql -h localhost -u bos --protocol=tcp --port=3307 -p

    # then enter: b0S-AKAE

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "bos"
                     , passwd = "b0S-AKAE"
                     , database = "bos"
                     , port = 3307
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                          , port   = port
                            )
        self.cursor = self.db.cursor()
        self.silent = silent

    def __del__(self):
        self.cursor.close()

    def reservationsRange(self, start, end):
        "A simple reformat of getReservationsByDateRange."
        res = self.getReservationsByDateRange(start, end)
        print "reservatinosRange: ", res
        return [{'id'    : id
               , 'name'  : u
               , 'start' : s.strftime("%m/%d/%Y")
               , 'end'   : e.strftime("%m/%d/%Y")} for id, u, s, e in res] #self.getReservationsByDateRange(start, end)]
               #, 'start' : self.str2dt(s).strftime("%m/%d/%Y")
               #, 'end'   : self.str2dt(e).strftime("%m/%d/%Y")} for id, u, s, e in res] #self.getReservationsByDateRange(start, end)]
 
    def getReservationsByDateRange(self, start, end):
        """
        Uses BOS DB mirror to return a list of reservations and
        their owners that overlap with the given date range.
        """

        if start is None or end is None:
            print "Error: missing date range for getReservationsByDateRange"
            return []

        q = """
        SELECT reservation.startDate, reservation.endDate, person.firstName, person.lastName, cas_user.global_id
        FROM reservation
        JOIN person USING (person_id)
        JOIN tg_user ON personAuthentication_id=user_id
        JOIN cas_user USING (user_id)
        JOIN site USING (site_id)
        WHERE site.code = 'GB'
        AND endDate > DATE(%s)
        AND startDate <= DATE(%s);
        """ % (self.dt2mysql(start), self.dt2mysql(end))

        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        res = [(int(r[4])
              , "%s %s" % (r[2], r[3])
              , r[0]
              , r[1]) for r in rows]
        # returning [(id, name, start date, end date)]
        # where id is *not* the global id from the PST (see above)
        return res

    def dt2mysql(self, dt):
        "datetime to string for mysql query"
        return dt.strftime("%Y%m%d")

    def getReservationsByUserAuthId(self, userAuthId, since = None):
        """
        Uses BOS DB mirror to return list of reservations for
        user represented by it's PST user authentication ID,
        where a reservation is a binary tuple of datetimes
        representing the check-in and check-out dates.
        """
        if userAuthId is None:
            print "Error: getReservationsByUserAuthId arg is None"
            return []

        since = since if since is not None else datetime.now()    
        try:
            sinceStr = self.dt2mysql(since)
            till     = since + timedelta(days = 365)
            tillStr  = self.dt2mysql(till)
        except:
            since = datetime.now()
            till  = since + timedelta(days = 365)
            sinceStr = self.dt2mysql(datetime.now())
            tillStr  = self.dt2mysql(till)

        # NOTE: remember that cas_user.global_id is a misnomer; see above
        q = """
        SELECT reservation.startDate, reservation.endDate 
        FROM reservation
        JOIN person USING (person_id)
        JOIN tg_user ON personAuthentication_id=user_id
        JOIN cas_user USING (user_id) 
        JOIN site USING (site_id)
        WHERE site.code = 'GB' 
        AND endDate >= %s
        AND startDate <= %s
        AND cas_user.global_id = %d
        ORDER BY reservation.startDate;
        """ % (sinceStr, tillStr, userAuthId)

        print q
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        print rows
        return rows
        #reservations = [(self.str2dt(r[0]), self.str2dt(r[1])) for r in rows] 
        #print "reservations: ", reservations
        #return reservations

    def str2dt(self, str):
        "YYYY-MM-DD -> DateTime"
        return datetime.strptime(str, "%Y-%m-%d")

    def dt2str(self, dt):
        "YYYY-MM-DD -> DateTime"
        return dt.strftime("%Y-%m-%d")


