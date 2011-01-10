from test_utils              import NellTestCase
from nell.utilities          import PSTMirrorDB, PSTQueryService

class TestPSTMirrorDB(NellTestCase):

    # this really isn't a 'unit test' since I'm interacting with PST's
    # Database, but a test is better then no test
    def test_getProfileByID(self):

        db = PSTMirrorDB()
        # 821 - pst_id for pmargani
        globalId = 821
        info = db.getStaticContactInfoByID(globalId)

        # expected values
        emails = ['pmargani@nrao.edu'
                , 'paghots@hotmail.com'
                , 'pmargani@gmail.com']
        emailDescs = ['pmargani@nrao.edu (Work)'
                    , 'paghots@hotmail.com (Other)'
                    , 'pmargani@gmail.com (Personal)']
        phones = ['304-456-2202', '304-456-2206']
        phoneDescs = ['304-456-2202 (Work)', '304-456-2206 (Other)']
        postals = \
            ['NRAO, PO Box 2, Green Bank, West Virginia, 24944, USA, (Office)'
           , '49 columbus Ave., W. Bridgewater, Massachusetts, 02379, United States, (Other)']
        affiliations = ['National Radio Astronomy Observatory '
                      , 'Oregon, University of']
        self.assertEquals(emails, info['emails'])
        self.assertEquals(emailDescs, info['emailDescs'])
        self.assertEquals(phones, info['phones'])
        self.assertEquals(phoneDescs, info['phoneDescs'])
        self.assertEquals(postals, info['postals'])
        self.assertEquals(affiliations, info['affiliations'])
        self.assertEquals('pmargani', info['username'])
        self.assertEquals(True, info['status'])
        self.assertEquals(globalId, info['person_id'])
        self.assertEquals(823, info['personAuth_id'])

    def test_getIdFromUserAuthenticationId(self):

        db = PSTMirrorDB()
        globalId = 821
        userAuthId = 823
        username = 'pmargani'
        id = db.getIdFromUserAuthenticationId(userAuthId)
        self.assertEquals(globalId, id)

    def test_getBadProfile(self):
        "Make sure we can handle bogus info."

        db = PSTMirrorDB()
        username = db.getUsername(0)
        self.assertEquals(None, username)

    # this is even more un "unit" test - we're interface with TWO
    # external systems
    def test_compareProfiles(self):
        "Compare the outputs from PSTQueryService & PSTMirrorDB"

        globalId =821

        db = PSTMirrorDB()
        # 823 - pst_id for pmargani
        mirror = db.getStaticContactInfoByID(globalId)

        ui = PSTQueryService()
        xml = ui.getStaticContactInfoByID(globalId)
        pst = ui.parseUserDict(xml)

        # get rid of any elements that are different
        # by design, status key is different
        mirror.pop('status')
        mirror.pop('first_name')
        mirror.pop('last_name')
        mirror.pop('person_id')
        mirror.pop('personAuth_id')
        pst.pop('status')
    def test_getIdFromUsername(self):

        db = PSTMirrorDB()
        globalId = 821
        username = 'pmargani'
        id = db.getIdFromUsername(username)
        self.assertEquals(globalId, id)
        un = db.getUsername(globalId)
        self.assertEquals(username, un)

    def test_getBadProfile(self):
        "Make sure we can handle bogus info."

        db = PSTMirrorDB()
        username = db.getUsername(0)
        self.assertEquals(None, username)

    # this is even more un "unit" test - we're interface with TWO
    # external systems
    def test_compareProfiles(self):
        "Compare the outputs from PSTQueryService & PSTMirrorDB"

        globalId =821

        db = PSTMirrorDB()
        # 823 - pst_id for pmargani
        mirror = db.getStaticContactInfoByID(globalId)

        ui = PSTQueryService()
        xml = ui.getStaticContactInfoByID(globalId)
        pst = ui.parseUserDict(xml)

        # get rid of any elements that are different
        # by design, status key is different
        mirror.pop('status')
        mirror.pop('first_name')
        mirror.pop('last_name')
        mirror.pop('person_id')
        mirror.pop('personAuth_id')
        pst.pop('status')
        # for some reason, the XML derived addresses aren't in order
        mirror.pop('postals')
        pst.pop('postals')
        self.assertEquals(mirror, pst)

