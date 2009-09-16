from utilities.database.DSSPrime2DSS  import DSSPrime2DSS
from utilities.database.Schedtime2DSS import Schedtime2DSS
from utilities.database.UserNames     import UserNames
from sesshuns.models                  import *

class DSSDatabase(object):
    
    """
    This class is responsible for populating a DSS database that has already
    been primed with static information (observing types table, etc.) with
    the data necessary for running the DSS for a semester.
    The main tasks are: transferring data from an intermediary DB that
    Carl populates, tranferring raw tables we get from Carl's system, and
    filling in missing information on users (from the PST).
    To prepare the database for a specific trimester (including things like
    rcvr schedules), this class should be extended.
    """

    def __init__(self, database = "dss_prime", interactive = False):

        self.interactive = interactive

        # responsible for data transfers
        self.dss_prime = DSSPrime2DSS(database = database)
        self.schedtime = Schedtime2DSS(database = database)

        # responsible for filling in info on users using the PST
        self.un = UserNames()

    def create(self, trimester):
        "Method for creating a new DSS database "
        # transfer the stuff that is trimester independent
        self.dss_prime.transfer()
        # user the PST query services to fill in all the user info
        self.get_user_info()
        # transfer the trimester dependent stuff - schedtime table!
        # order here is important because we need the user info
        # to be all there first
        # NOTE: if this fails to find certain users, add them to
        # UserNames.createMissingUsers and run again.
        self.schedtime.transfer_fixed_periods(trimester)

            
    def get_user_info(self):
        """
        Here's all the hoops you have to jump through to get our User table
        in sync with the PST.
        """

        # who's missing that really needs to be in here?
        self.un.createMissingUsers()
        self.un.setAdminRoles()

        if self.interactive:
            # first, what's the status?
            print "First, check DB vs. PST."
            print "Are these differences in names acceptable?"
            self.un.confirmUserInfo('dss', 'MrNubbles!')
            x = raw_input("Continue and get missing IDs/usernames? CtrlX if not.")

        self.un.getUserNamesFromProjects('dss', 'MrNubbles!')

        self.un.getUserNamesFromIDs('dss', 'MrNubbles!')

        if self.interactive:
            print "Finally, check DB vs. PST one more time: "
            self.un.confirmUserInfo('dss', 'MrNubbles!')

            print "Fix the rest."
            print ""
            self.un.findMissingUsers()


    def validate_receiver_schedule(self):
        "compares the periods brought over by schedtime w/ the rcvr schedule."

        # make sure we don't have periods scheduled at times where
        # there isn't a required rcvr available
        ps = Period.objects.all()
        bad = []
        for p in ps:
            if not p.has_required_receivers():
                #print "bad period: ", p
                bad.append(p)
        # report
        for b in bad:
            print "Session (%s, %d) at %s for %f hours needs rcvrs: %s" % \
                (b.session.name
               , b.session.original_id
               , b.start
               , b.duration
               , b.session.receiver_list_simple())
        print "number of periods w/ out required receivers: ", len(p)

        # TBF: now make sure that receiver changes happen on maintenance days
        # cast a wide enough net to make this trimester agnostic
        #start = date(
        #rs = Receiver_Schedule(start, 


