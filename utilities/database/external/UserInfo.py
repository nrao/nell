from   PSTMirrorDB        import PSTMirrorDB

class UserInfo(PSTMirrorDB):

    """
    Control whether or not this class pulls info on users from the
    PST via their Query Serivce or the DB Mirror, simply by changing
    the parent class.
    The PSTMirrorDB should be the default, since this is much faster,
    but we want to be able to easily toggle between the two in case 
    there are failures.
    """




