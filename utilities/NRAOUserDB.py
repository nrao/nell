import logging

from urlparse import urlparse, urlunparse
from urllib import urlencode

import urllib2
from urllib2 import URLError

try:
    import lxml.etree as ET
except:
    #print "can't import lxml!"
    pass

from caslib import login_to_cas_service, CASLoginError
from caslib.validating_https import ValidatingHTTPSConnection


_log = logging.getLogger(__name__)


class XMLNS(object):
    '''Utility class to generate xml names using clark notation'''

    def __init__(self, ns=None):
        self.ns = ns

    def __getitem__(self, attr, default=None):
        if self.ns:
            return '{%s}%s' % (self.ns, attr.replace('_', '-'))
        return attr

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)

        except AttributeError:
            return self[attr]

nrao = XMLNS('http://www.nrao.edu/namespaces/nrao')

class TryAuthenticating(RuntimeError):
    '''Perhaps you should try logging in?  Mmmm?'''

    login_url = None
    '''The last url retrieved'''

    def __init__(self, login_url, *args):
        super(TryAuthenticating, self).__init__(*args)
        self.login_url = login_url


class NRAOUserDB(object):

    def __init__(self, url, username=None, password=None, opener=None):
        '''

        :param url:             Location of the QueryFilter service
        :param username:        Account that may query the user database
        :param password:        Password for username
        :param opener:          Optional configured :class:`urllib2.OpenerDirector`
        '''

        self.url = url
        self.username = username
        self.password = password
        self.opener = opener

    def _get_user_data(self, url):
        # This interface is kind of dodgy, we have a few different failure modes to cover.
        try:
            fh = self.opener.open(url)
            login_url = fh.url

        except URLError, e:
            # URLError - We _could_ get this if PST sent an error code
            # other wise it's probably a connection or configuration problem.
            raise TryAuthenticating(e.url, str(e))

        # If the query doesn't find any data, QueryFilter gives us an
        # incomplete document.  The xml parser won't do anything useful
        # with it, but it is PST-speak for ENOENT.  No need to retry
        # anything.

        # We have to peek.  Can't mess around with itertools.tee or anything
        # like that because lxml.etree (C lib) won't like it.  So, just read.
        # But don't go overboard, these shouldn't be very big records.
        doc_str = fh.read(0x4000)

        if doc_str == '<?xml version="1.0" encoding="UTF-8"?>':
            return None

        #print "****************doc_str: "
        #print doc_str
        #print "************* end doc_str"
        doc_str_unicode = unicode(doc_str, "iso-8859-1")
        doc_str = doc_str_unicode.encode("UTF-8")
        try:
            user_data = ET.fromstring(doc_str)

        except SyntaxError, e: # lxml.etree will generate this
            # Probably the HTML login page
            #print e
            raise TryAuthenticating(login_url, 'received something that was not well formed xml; maybe a login form?')

        #TBF only user queries return that tag
        #user_data_root_tag = user_data.tag
        #if user_data_root_tag != nrao.user:
        #    raise TryAuthenticating(login_url, 'received %r; expected %r' % (user_data_root_tag, nrao.user))

        return user_data


    def get_user_data(self, username):
        '''Try to retrieve user profile information for a user'''

        scheme, host, path, params, query, fragment = urlparse(self.url)
        query = urlencode([('userByAccountNameEquals', username)], True)
        url = urlunparse((scheme, host, path, params, query, fragment))

        _log.info('Retrieving user profile for: %s', username)

        try:
            user_data = self._get_user_data(url)
        except TryAuthenticating, e:
            # TryAuthenticating may be a good idea, better tell an adult!
            if not e.login_url or not self.username:
                _log.exception(e)
                raise

            # This may raise a URLError or CASLoginError.  There's nothing much
            # to be done about it though, so I'm not handling it.
            _log.info('Failed: %s', e)
            # FIXME: It would be good to check that we haven't been redirected
            # someplace strange before we send off our credentials.  Hopefully
            # certificate validation will lessen this possibility.
            login_to_cas_service(e.login_url, self.username, self.password, opener=self.opener)

            # If that worked, then give it another go
            user_data = self._get_user_data(url)

        if user_data is not None: # FutureWarning says test for None
            return user_data

    def get_data(self, key, value):
        '''Try to retrieve user profile information for a user, via key, value'''

        scheme, host, path, params, query, fragment = urlparse(self.url)
        query = urlencode([(key, value)], True)
        url = urlunparse((scheme, host, path, params, query, fragment))

        _log.info('Retrieving user profile with key/value: %s/%s', key, value)

        try:
            user_data = self._get_user_data(url)
        except TryAuthenticating, e:
            # TryAuthenticating may be a good idea, better tell an adult!
            if not e.login_url or not self.username:
                _log.exception(e)
                raise

            # This may raise a URLError or CASLoginError.  There's nothing much
            # to be done about it though, so I'm not handling it.
            _log.info('Failed: %s', e)
            # FIXME: It would be good to check that we haven't been redirected
            # someplace strange before we send off our credentials.  Hopefully
            # certificate validation will lessen this possibility.
            login_to_cas_service(e.login_url, self.username, self.password, opener=self.opener)

            # If that worked, then give it another go
            user_data = self._get_user_data(url)

        if user_data is not None: # FutureWarning says test for None
            return user_data

def get_user_data(cas_user_name):
    global udb
    return udb.get_user_data(cas_user_name)


