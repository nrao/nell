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

    def getStaticContactInfo(self, username, queryUser, queryPassword):
        "Get contact info for username, using given credentials for CAS."

        udb = NRAOUserDB.NRAOUserDB( \
            self.baseURL
          , queryUser
          , queryPassword
          , opener=urllib2.build_opener())
        key = 'userByAccountNameEquals'
        el = udb.get_data(key, username)
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

    def parseUserXML(self, element):
        "Parses a given Element object representing user info into a dict."
        # TBF: must be a better way of doing this
        # TBF: looked into lxml.objectify, but couldn't get it to work properly
        userInfo = {}
        # just do it by hand!
        # name section
        name = self.findTag(element, "name")
        if name is not None:
            nameKeys = ['prefix', 'first-name', 'middle-name', 'last-name']
            userInfo['name'] = self.parseSectionText(name, nameKeys)
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
            # TBF: postal addresses
        # affiliation-info section
        # misc-info section
        # account-info section

        return userInfo

