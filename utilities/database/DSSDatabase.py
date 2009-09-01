from utilities.database.DSSPrime2DSS import DSSPrime2DSS
from utilities.database.UserNames    import UserNames
from sesshuns.models import *

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

        # responsible for filling in info on users using the PST
        self.un = UserNames()

    def create(self, trimester):
        "Method for creating a new DSS database "
        # transfer the stuff that is trimester independent
        self.dss_prime.transfer()
        # transfer the trimester dependent stuff - schedtime table!
        self.dss_prime.transfer_fixed_periods(trimester)
        # user the PST query services to fill in all the user info
        self.get_user_info()

            
    def get_user_info(self):
        """
        Here's all the hoops you have to jump through to get our User table
        in sync with the PST.
        """

        # who's missing that really needs to be in here?
        self.create_admins()
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


    # TBF: perhaps this should be in UserNames?
    def create_admins(self):
        "Creates users who probably aren't on a GBT proposal in the PST"

        admins = [("Paul", "Marganian", "pmargani", 823)
                , ("Mark", "Clark", "windyclark", 1063)
                , ("Amy", "Shelton", "ashelton", 556 )
                , ("Dan", "Perera", 'dperera', 2705)
                # who else?
                 ]

        for first_name, last, user, id in admins:
            # don't make'm unless you have to
            u = first(User.objects.filter(username = user)) 
            if u is not None:
                continue
            # you have to
            u = User(original_id = 0
               , sanctioned  = True
               , first_name  = first_name 
               , last_name   = last 
               , username    = user
               , pst_id      = id 
               , role        = first(Role.objects.filter(role = "Administrator"))
                 )
            u.save()
        
