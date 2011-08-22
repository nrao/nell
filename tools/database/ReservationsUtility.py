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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime           import datetime, timedelta
from scheduler.models    import *

class ReservationsUtility(object):

    """
    This class provides a work around for the problem that the query of the
    BOS services does not work in Haskell.  The workaround is that we will
    regularly pull these over in python into a DB, which haskell can read.
    Since this info is only for scheduling, it's okay that the DB won't be
    dynamic - as long as each morning's scheduling run gets the latest
    reservation info.
    """

    def updateReservations(self):
        "Main functionality of class - retrieve them, store them."

        # grab the latest res info
        currentRes = self.getReservationsFromBOS()

        # if that worked, clean up the current reservations:
        staleRes = Reservation.objects.all()
        for r in staleRes:
            r.delete()

        # save the latest info to the database
        # since we aren't cleaning out the DB, watch for reduncant entries
        for user, dates in currentRes:
            for date in dates:
                print "new reservation: ", user, date
                new = Reservation(user       = user
                                , start_date = date[0]
                                , end_date   = date[1]
                                )
                new.save()

    def getReservationsFromBOS(self):
        "Use the BOS mirror to get all reservations for DSS users."

        res = []
        users = User.objects.all()
        for user in users:
            try:
                print user, user.pst_id
                rs = user.getReservations()
            except:
                print "Error retrieving reservations for: ", user
                rs = []
            if len(rs) != 0:
                print "!!!!!!!!!!!!!!", rs
                res.append((user, rs))
        print res            
        return res            

if __name__ == "__main__":
    ReservationsUtility().updateReservations()
