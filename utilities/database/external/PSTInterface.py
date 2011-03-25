
class PSTInterface(object):

    """
    Abstract class for retrieving contact info (profiles) out of
    PST.
    """

    def getUsername(self, pst_id):
        pass

    def getIdFromUsername(self, username):
        pass

    def getIdFromUserAuthenticationId(self, userAuth_id):
        pass

    def getProfileByID(self, user, use_cache = True):
        pass

    def getStaticContactInfoByUserName(self, username, use_cache = True):
        pass

    def getStaticContactInfoByID(self, id, use_cache = True):
        pass
