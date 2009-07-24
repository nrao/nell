import logging, urllib2, NRAOUserDB


# This will give some clues as to what is going on
def get_user_info(usernames, query_user_account, query_user_password):
    logging.basicConfig()
    logging.root.level = logging.INFO

    udb = NRAOUserDB.NRAOUserDB('https://my.nrao.edu/nrao-2.0/secure/QueryFilter.htm', query_user_account, query_user_password, opener=urllib2.build_opener())

    # The result is an lxml.etree._Element (or xml.etree.ElementTree.Element)
    for username in usernames:
        el = udb.get_user_data(username) 
        print "el for username: ", username
        print el
