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

from test_utils              import NellTestCase
from nell.utilities.database.external          import PSTMirrorDB

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

