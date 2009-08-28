from utilities import NRAOUserDB
import lxml.etree as ET
import urllib2

class UserInfo(object):

    # TBF: should try to use a more object like XML parser
    # TBF: we are parsing first to a dict, then further parsing that dict. BAD
    """
    This class is responsible for dynamically retrieving and parsing
    info about a given user from the PST query services.  It utilitizes
    NRAOUserDB to get around their CAS authentication.
    """

    def __init__(self):

        self.baseURL = 'https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
        self.ns = "{http://www.nrao.edu/namespaces/nrao}"
        self.udb = None

    def getProfileByID(self
                     , user
                     , queryUser
                     , queryPassword):

        info = self.getStaticContactInfoByID(user.pst_id
                                           , queryUser
                                           , queryPassword)

        # what profile info do we already have?
        emails = [e.email for e in user.email_set.all()]

        return self.parseUserDict(info, emails, [], [])

    def parseUserDict(self, info, emails2 = [], phones2 = [], postals2 = []):   
        "Convinience method so you don't have to deal with bad info dictionary."

        username = None
        accntInfo = info.get('account-info', None)
        if accntInfo is not None:
            username = accntInfo.get('account-name', None)

        # prepend info w/ what we already have
        emails  = [e for e in emails2]
        phones  = [p for p in phones2]
        postals = [p for p in postals2]

        contacts = info.get('contact-info', None)
        # got contacts?
        if contacts is not None:
            pst_emails = contacts.get('email-addresses', None)
            # got emails?
            if pst_emails is not None:
                default = pst_emails.get('default-email-address', None)
                if default is not None and default not in emails:
                    emails.append(default)
                others = pst_emails.get('additional-email-address', None)
                if others is not None:
                    for other in others:
                        if other not in emails:
                            emails.append(other)
            pst_phones = contacts.get('phone-numbers', None)                
            # got phones?
            # TBF: phone & email code is redundant - use a single function
            if pst_phones is not None:
                default = pst_phones.get('default-phone-number', None)
                if default is not None and default not in phones:
                    phones.append(default)
                others = pst_phones.get('additional-phone-number', None)
                if others is not None:
                    for other in others:
                        if other not in phones:
                            phones.append(other)
            # got postal addresses?
            pst_postals = contacts.get('postal-addresses', None)
            if pst_postals is not None:
                for pst_postal in pst_postals:
                    # convert the dict to a single string
                    streets = ', '.join(pst_postal.get('streetlines', []))
                    lines = [streets
                           , pst_postal.get('city', '')
                           , pst_postal.get('state', '')
                           , pst_postal.get('postal-code', '')
                           , pst_postal.get('country', '')
                           , "(%s)" % pst_postal.get('address-type', 'N/A')
                           ]
                    str = ', '.join(lines)      
                    postals.append(str)

        return dict(emails = emails
                  , phones = phones
                  , postals = postals
                  , username = username)

    def getStaticContactInfoByUserName(self, username, queryUser,queryPassword):
        return self.getStaticContactInfo('userByAccountNameEquals'
                                       , username
                                       , queryUser
                                       , queryPassword)

    def getStaticContactInfoByID(self, id, queryUser,queryPassword):
        return self.getStaticContactInfo('userById'
                                       , id
                                       , queryUser
                                       , queryPassword)

    def getStaticContactInfo(self, key, value, queryUser, queryPassword):
        "Get contact info from query service, using given credentials for CAS."

        # make sure we only log once
        if self.udb is None:
        #    self.udb = NRAOUserDB.NRAOUserDB( \
            self.udb = NRAOUserDB( \
                self.baseURL
              , queryUser
              , queryPassword
              , opener=urllib2.build_opener())

        el = self.udb.get_data(key, value)

        return self.parseUserXML(el)

    def findTag(self, node, tag):
        # TBF: why do all the XML tags have the namepace attatched?
        return node.find(self.ns + tag)

    def parseSectionText(self, sec, keys):
        "Parses sections like name"
        values = {}
        for k in keys:
            v = self.findTag(sec, k)
            if v is not None:
                values[k] = v.text
        return values   

    def parseSectionList(self, sec, tagBase, attr):
        values = {}
        defaultTag = "default-%s" % tagBase
        addTag = "additional-%s" % tagBase
        default = self.findTag(sec, defaultTag)
        if default is not None:
            values[defaultTag] = default.get(attr)
        others = sec.findall(self.ns + addTag)
        if len(others) > 0:
            values[addTag] = []
        for i in range(len(others)):
            values[addTag].append(others[i].get(attr))
        return values

    def parseSection(self, sec, secName, secDetailName, attr):
        "Parses sections like email-addresses and phone-numbers"
        values = {}
        s = self.findTag(sec, secName)
        if s is not None:
            values = self.parseSectionList(s, secDetailName, attr)
        return values

    def parsePostals(self, sec):
        postals = []
        keys = ['address-type', 'city', 'state', 'country', 'postal-code']
        s = self.findTag(sec, 'postal-addresses')
        if s is not None:
            tags = s.findall(self.ns + 'additional-postal-address')
            for tag in tags:
                address = self.parseSectionText(tag, keys)
                streets = tag.findall(self.ns + 'streetline')
                address['streetlines'] = [st.text for st in streets]
                postals.append(address)    
            tags = s.findall(self.ns + 'default-postal-address')
            # TBF: redundant
            for tag in tags:
                address = self.parseSectionText(tag, keys)
                streets = tag.findall(self.ns + 'streetline')
                address['streetlines'] = [st.text for st in streets]
                postals.append(address)    
        return postals

    def parseUserXML(self, element):
        "Parses a given Element object representing user info into a dict."
        # TBF: must be a better way of doing this
        # TBF: looked into lxml.objectify, but couldn't get it to work properly
        userInfo = {}
        # just do it by hand!
        # top level attributes
        id = None
        items = element.items()
        for key, value in items:
            if key == 'id':
                id = value
        userInfo['id'] = id        
        # name section
        name = self.findTag(element, "name")
        if name is not None:
            nameKeys = ['prefix', 'first-name', 'middle-name', 'last-name']
            userInfo['name'] = self.parseSectionText(name, nameKeys)
        # account-info
        at = self.findTag(element, "account-info")
        if at is not None:
            actKeys = ['account-name'] # need anything else?
            userInfo['account-info'] = self.parseSectionText(at, actKeys)
        # contact-info section
        ci = self.findTag(element, "contact-info")
        if ci is not None:
            userInfo['contact-info'] = {}
            userInfo['contact-info']['email-addresses'] = self.parseSection(ci
                                                                          , 'email-addresses'
                                                                          , 'email-address'
                                                                          , 'addr')
            userInfo['contact-info']['phone-numbers'] = self.parseSection(ci
                                                                        , 'phone-numbers'
                                                                        , 'phone-number'
                                                                        , 'number')
            userInfo['contact-info']['postal-addresses'] = self.parsePostals(ci)                                                                        
            # TBF: postal addresses
        # affiliation-info section
        # misc-info section
        # account-info section

        return userInfo


