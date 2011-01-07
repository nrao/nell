import lxml.etree as et

from test_utils              import NellTestCase
from nell.utilities          import PSTMirrorDB, PSTQueryService
from sesshuns.models         import *

class TestPSTQueryService(NellTestCase):

    def setUp(self):
        super(TestPSTQueryService, self).setUp()

        self.ui = PSTQueryService()

        self.me = User(first_name = "Paul"
                     , last_name = "Marganian"
                     , role_id = 1
                     , pst_id = 821)
        self.me.save()

        #<?xml version="1.0" encoding="UTF-8"?>
        self.xmlStr =  """
        <nrao:query-result xmlns:nrao="http://www.nrao.edu/namespaces/nrao" >
        <nrao:user id="823" globalid="821" domestic="true" xmlns:nrao="http://www.nrao.edu/namespaces/nrao">
        <nrao:name>
        <nrao:prefix>Mr</nrao:prefix>
        <nrao:first-name>Paul</nrao:first-name>
        <nrao:middle-name>Raffi</nrao:middle-name>
        <nrao:last-name>Marganian</nrao:last-name>
        </nrao:name>
        <nrao:contact-info>
        <nrao:email-addresses>
        <nrao:default-email-address addr="pmargani@nrao.edu">
        <nrao:description>Work</nrao:description>
        </nrao:default-email-address>
        <nrao:additional-email-address addr="paghots@hotmail.com">
        <nrao:description>Other</nrao:description>
        </nrao:additional-email-address>
        <nrao:additional-email-address addr="pmargani@gmail.com">
        <nrao:description>Personal</nrao:description>
        </nrao:additional-email-address>
        </nrao:email-addresses>
        <nrao:postal-addresses>
        <nrao:additional-postal-address>
        <nrao:address-type>Office</nrao:address-type>
        <nrao:streetline>NRAO</nrao:streetline>
        <nrao:streetline>PO Box 2</nrao:streetline>
        <nrao:city>Green Bank</nrao:city>
        <nrao:state>West Virginia</nrao:state>
        <nrao:country>USA</nrao:country>
        <nrao:postal-code>24944</nrao:postal-code>
        </nrao:additional-postal-address>
        <nrao:additional-postal-address>
        <nrao:address-type>Other</nrao:address-type>
        <nrao:streetline>49 columbus Ave.</nrao:streetline>
        <nrao:city>W. Bridgewater</nrao:city>
        <nrao:state>Massachusetts</nrao:state>
        <nrao:country>United States</nrao:country>
        <nrao:postal-code>02379</nrao:postal-code>
        </nrao:additional-postal-address>
        </nrao:postal-addresses>
        <nrao:phone-numbers>
        <nrao:default-phone-number number="304-456-2202">
        <nrao:description>Work</nrao:description>
        </nrao:default-phone-number>
        </nrao:phone-numbers>
        </nrao:contact-info>
        <nrao:affiliation-info>
        <nrao:default-affiliation id="5">
        <nrao:formal-name>National Radio Astronomy Observatory </nrao:formal-name>
        </nrao:default-affiliation>
        <nrao:additional-affiliation id="269">
        <nrao:formal-name>Oregon, University of</nrao:formal-name>
        </nrao:additional-affiliation>
        </nrao:affiliation-info>
        <nrao:misc-info>
        <nrao:user-type>NRAO Staff</nrao:user-type>
        <nrao:web-site>http://www.geocities.com/mangophenomena/</nrao:web-site>
        </nrao:misc-info>
        <nrao:account-info>
        <nrao:account-name>pmargani</nrao:account-name>
        <nrao:encrypted-password>d59c3e6cc6236139bd94307de0e775cc</nrao:encrypted-password>
        <nrao:entry-status>Suspect</nrao:entry-status>
        </nrao:account-info>
        </nrao:user>
        </nrao:query-result>
        """
        self.xml = et.fromstring(self.xmlStr)
        self.xmlDict = \
        {'contact-info': \
            {'phone-numbers':   {'default-phone-number': {'description' : 'Work'
                                                         ,'number' : '304-456-2202'}}
           , 'email-addresses': {'default-email-address': {'description' : 'Work'
                                                          ,'addr' : 'pmargani@nrao.edu'}
                             , 'additional-email-address': [{'description' : 'Other'
                                                            ,'addr' : 'paghots@hotmail.com'}
                                                          , {'description' : 'Personal'
                                                            ,'addr' : 'pmargani@gmail.com'}]}
           , 'postal-addresses': [{'city': 'Green Bank'
                                 , 'streetlines': ['NRAO', 'PO Box 2']
                                 , 'address-type': 'Office'
                                 , 'state': 'West Virginia'
                                 , 'country': 'USA'
                                 , 'postal-code': '24944'}
                                 , {'city': 'W. Bridgewater'
                                 , 'streetlines': ['49 columbus Ave.']
                                 , 'address-type': 'Other'
                                 , 'state': 'Massachusetts'
                                 , 'country': 'United States'
                                 , 'postal-code': '02379'}]
            }
            , 'name': {'prefix': 'Mr'
                     , 'first-name': 'Paul'
                     , 'middle-name': 'Raffi'
                     , 'last-name': 'Marganian'}
            , 'account-info': {'account-name': 'pmargani'
                             , 'entry-status': 'Suspect'}
            , 'id': '823'
            , 'globalid': '821'
            , 'affiliation-info': [("National Radio Astronomy Observatory ", True)
                             , ("Oregon, University of", False)]
        }

    def test_parseUserXML(self):
        i = self.ui.parseUserXML(self.xml)
        self.assertEqual(i, self.xmlDict)

    def test_parseUserDict(self):
        info = self.ui.parseUserDict(self.xmlDict)
        # expected values
        emails = ['pmargani@nrao.edu'
                , 'paghots@hotmail.com'
                , 'pmargani@gmail.com']
        emailDescs = ['pmargani@nrao.edu (Work)'
                    , 'paghots@hotmail.com (Other)'
                    , 'pmargani@gmail.com (Personal)']
        phones = ['304-456-2202']
        phoneDescs = ['304-456-2202 (Work)']
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
        self.assertEquals('Suspect', info['status'])

    # THis is NOT a unit -test: it actually interacts w/ the PST service!
    def test_pstServices(self):

        globalid = 821
        userAuthId = 823

        username =  self.ui.getUsername(self.me.pst_id)
        self.assertEquals('pmargani', username)

        id = self.ui.getIdFromUsername(username)
        self.assertEquals(globalid, id)

        # TBF: for some reason, the returned info has something trivially
        # different then self.xmlDict, but I don't know what.
        info = self.ui.getStaticContactInfoByUserName(username)
        self.assertEquals(self.xmlDict['name'],info['name'])

        info = self.ui.getStaticContactInfoByID(self.me.pst_id)
        self.assertEquals(self.xmlDict['name'],info['name'])

        info = self.ui.getProfileByID(self.me)
        self.assertEquals('pmargani', info['username'])

        id = self.ui.getIdFromUserAuthenticationId(userAuthId)
        self.assertEquals(globalid, id)

