from sesshuns.models    import *
from datetime           import datetime, timedelta
from utilities          import NRAOBosDB

class ReservationsUtility(object):

    """
    This class provides a work around for the problem that the query of the
    BOS services does not work in Haskell.  The workaround is that we will
    regularly pull these over in python into a DB, which haskell can read.
    Since this info is only for scheduling, it's okay that the DB won't be
    dynamic - as long as each morning's scheduling run gets the latest
    reservation info.
    """

    def __init__(self):

        self.bos = NRAOBosDB()

    def updateReservations(self):
        "Main functionality of class - retrieve them, store them."

        # grab the latest res info
        try:
            currentRes = self.getReservationsFromBOS()
        except:
            print "exception in retrieving reservations from BOS"
            return

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
        "Use the query service to get all reservations for DSS users."

        res = []
        # TBF: there may be better query services to use,
        # but this is the only one that's been tested enough
        users = User.objects.all()
        for user in users:
            print user
            if user.username is not None:
                rs = self.bos.getReservationsByUsername(user.username
                                                      , use_cache = False)
                if len(rs) != 0:
                    print "!!!!!!!!!!!!!!", rs
                    res.append((user, rs))
        print res            
        return res            


