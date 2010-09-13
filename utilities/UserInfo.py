from   NRAOUserDB         import NRAOUserDB

from   django.core.cache import cache
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

    # Log in only once to minimize authentication overhead.
    __userDB = NRAOUserDB( \
                'https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm'
              , 'QueryAgent'
              , 'iBlertFoo'
              , opener = urllib2.build_opener())

    def __init__(self):
        self.ns    = "{http://www.nrao.edu/namespaces/nrao}"

    def getProfileByID(self, user, use_cache = True):
        try:
            info = self.getStaticContactInfoByID(user.pst_id, use_cache)
        except:
            return dict(emails       = []
                      , emailDescs   = []
                      , phones       = ['Not Available']
                      , phoneDescs   = ['Not Available']
                      , postals      = ['Not Available']
                      , affiliations = ['Not Available']
                      , status       = 'Not Available'
                      , username     = user.username)
        else:
            return self.parseUserDict(info)

    def parseUserDict(self, info):
        "Convinience method so you don't have to deal with bad info dictionary."
        # TBF: we wouldn't need this function if the XML parsing didn't
        # suck so bad.

        # got username?
        username = None
        accntInfo = info.get('account-info', None)
        if accntInfo is not None:
            username = accntInfo.get('account-name', None)
            status   = accntInfo.get('entry-status', None)

        # got affiliations?
        afs = info.get('affiliation-info', [])
        # strip out the flag that tells us which one is default
        affiliations = [af[0]  for af in afs]

        emails   = []
        phones   = []
        postals  = []
        # some consumers will want just the plain emails, since they'll
        # use them to send actuall emails, while others want a more 
        # descriptive format
        emailDescs  = []
        phoneDescs  = []
        contacts = info.get('contact-info', None)

        # got contacts?
        if contacts is not None:
            # got emails?
            pst_emails = contacts.get('email-addresses', None)
            try:
                emails, emailDescs = self.parseUserDictEntry(pst_emails
                                                           , 'email-address'
                                                           , 'addr')
            except:
                emails = []
                emailDescs = []

            # got phones?
            pst_phones = contacts.get('phone-numbers', None)                
            try:
                phones, phoneDescs = self.parseUserDictEntry(pst_phones
                                                           , 'phone-number'
                                                           , 'number')
            except:
                phones = []
                phoneDescs = []

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

        return dict(emails       = emails
                  , emailDescs   = emailDescs
                  , phones       = phones
                  , phoneDescs   = phoneDescs
                  , postals      = postals
                  , affiliations = affiliations
                  , status       = status
                  , username     = username)

    def parseUserDictEntry(self, pst_values, name, valueName):
        """
        Takes a dictionary of the form
        { 'default-name' : {'valueName' : 'value', 'description', 'desc'}
        , 'additional-name' : [{'valueName' : 'value', 'description', 'desc'}]}
        and returns two simple lists of:
        [ 'value (desc)', 'value (desc)', ...]
        [ 'value', 'value', ...]
        """
        values = []
        plainValues = []
        if pst_values is not None:
            defaultTag = 'default-%s' % name
            default = pst_values.get(defaultTag, None)
            if default is not None:
                value = default.get(valueName,'')
                defaultStr = "%s (%s)" % (value, default.get('description', ''))
            else:
                defaultStr = None
            if defaultStr is  not None and defaultStr not in values:
                values.append(defaultStr)
                plainValues.append(value)
            additionalTag = 'additional-%s' % name    
            others = pst_values.get(additionalTag, None)
            if others is not None:
                for other in others:
                    value = other.get(valueName,'')
                    otherStr = "%s (%s)" % (value, other.get('description', ''))
                    if otherStr not in values:
                        values.append(otherStr)
                        plainValues.append(value)
        return (plainValues, values)

    def getStaticContactInfoByUserName(self, username, use_cache = True):
        return self.getStaticContactInfo('userByAccountNameEquals', username, use_cache)

    def getStaticContactInfoByID(self, id, use_cache = True):
        return self.getStaticContactInfo('userById', id, use_cache)

    def getStaticContactInfo(self, key, value, use_cache = True):
        """
        Get contact info from query service, using given credentials for CAS.
        The cache is indexed by key value, i.e. if the key is userById, then
        the value is the actual user id.
        """
        cache_key = str(value) # keys have to be strings

        if not use_cache or cache.get(cache_key) is None:
            info = self.parseUserXML(UserInfo.__userDB.get_data(key, value)) or "no reservations"

            if cache.get(cache_key) is None:
                cache.add(cache_key, info)
            else:
                cache.set(cache_key, info)
        else:
            info = cache.get(cache_key)

        return info if info != "no reservations" else None

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

    def parseSectionList(self, sec, tagBase, attr, keys):
        """
        Takes a section like this:
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
        and returns
        { "default-email-address" : "pmargani@nrao.edu"
        , "additional-email-address" : ["1", "etc."] }
        """
        
        values = {}
        defaultTag = "default-%s" % tagBase
        addTag = "additional-%s" % tagBase
        default = self.findTag(sec, defaultTag)
        if default is not None:
            defaultValue = self.parseSectionText(default, keys)
            defaultValue[attr] = default.get(attr)
            values[defaultTag] = defaultValue
        others = sec.findall(self.ns + addTag)
        if len(others) > 0:
            values[addTag] = []
        for i in range(len(others)):
            otherValue = self.parseSectionText(others[i], keys)
            otherValue[attr] = others[i].get(attr)
            values[addTag].append(otherValue)
        return values

    def parseSection(self, sec, secName, secDetailName, attr, keys):
        "Parses sections like email-addresses and phone-numbers"
        values = {}
        s = self.findTag(sec, secName)
        if s is not None:
            values = self.parseSectionList(s, secDetailName, attr, keys)
        return values

    def parsePostals(self, sec):
        """
        Returns a list of dictionaries, where each dict is the result of 
        parsing a section like:
        <nrao:additional-postal-address>
        <nrao:address-type>Office</nrao:address-type>
        <nrao:streetline>NRAO</nrao:streetline>
        <nrao:streetline>PO Box 2</nrao:streetline>
        <nrao:city>Green Bank</nrao:city>
        <nrao:state>West Virginia</nrao:state>
        <nrao:country>USA</nrao:country>
        <nrao:postal-code>24944</nrao:postal-code>
        </nrao:additional-postal-address>
        """
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

    def parseUserXML(self, el):
        "Assumes there is only one user embedded in the XML"
        users = el.getchildren()
        assert len(users) == 1
        element = users[0]
        return self.parseUserXMLWorker(element)

    def parseUserXMLWorker(self, element):
        "Parses a given Element object representing user info into a dict."

        # TBF: must be a better way of doing this
        # TBF: looked into lxml.objectify, but couldn't get it to work properly
        userInfo = {}

        id = None
        # get top level attributes
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
            actKeys = ['account-name', 'entry-status'] # need anything else?
            userInfo['account-info'] = self.parseSectionText(at, actKeys)
        # contact-info section
        ci = self.findTag(element, "contact-info")
        if ci is not None:
            userInfo['contact-info'] = {}
            userInfo['contact-info']['email-addresses'] = \
                self.parseSection(ci
                               , 'email-addresses'
                               , 'email-address'
                               , 'addr'
                               , ['description'])
            userInfo['contact-info']['phone-numbers'] = \
                self.parseSection(ci
                                , 'phone-numbers'
                                , 'phone-number'
                                , 'number'
                                , ['description'])
            userInfo['contact-info']['postal-addresses'] = self.parsePostals(ci)                                                                        
        # affiliation-info section
        # TBF: redundant redundant redundant
        af = self.findTag(element, "affiliation-info")
        if af is not None:
            userInfo['affiliation-info'] = []
            defaultAf = self.findTag(af, "default-affiliation")
            if defaultAf is not None:
                afName = self.findTag(defaultAf, "formal-name")
                if afName is not None:
                    userInfo['affiliation-info'].append((afName.text, True))   
            affiliations = af.findall(self.ns + "additional-affiliation")
            for affiliation in affiliations:
                afName = self.findTag(affiliation, "formal-name")
                if afName is not None:
                    userInfo['affiliation-info'].append((afName.text, False))   

        # misc-info section

        return userInfo


