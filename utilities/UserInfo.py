from utilities import NRAOUserDB
import lxml.etree as ET
import urllib2

class UserInfo(object):

    """
    This class is responsible for dynamically retrieving and parsing
    info about a given user from the PST query services.  It utilitizes
    NRAOUserDB to get around their CAS authentication.
    """

    def __init__(self):

        self.baseURL = 'https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
        self.ns = "{http://www.nrao.edu/namespaces/nrao}"

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

        udb = NRAOUserDB.NRAOUserDB( \
            self.baseURL
          , queryUser
          , queryPassword
          , opener=urllib2.build_opener())
        #key = 'userByAccountNameEquals'
        #el = udb.get_data(key, username)
        el = udb.get_data(key, value)
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


