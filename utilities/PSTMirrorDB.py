import MySQLdb as m

class PSTMirrorDB(object):
    """
    This class is responsible for reading user info from the mirror of
    the PST DB available in Green Bank.  This is a read-only, MySql DB,
    so we decided it wasn't worth the effort to incorporate this DB
    into our model.
    Note that the formatting of the resulting profile info does not make
    complete sense; but the format is dictated by being backward compatible
    with the output form UserInfo.  The excpetion to this is the 'status'
    field, which is not displayed, but only used for internal purposes.
    """

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "nrao_200"
                     , passwd = "wugupHA8"
                     , database = "nrao_200"
                     , silent   = True
                 ):
        self.db = m.connect(host   = host
                          , user   = user
                          , passwd = passwd
                          , db     = database
                            )
        self.cursor = self.db.cursor()
        self.silent = silent

    def __del__(self):
        self.cursor.close()

    def getProfileByID(self, user):
        try:
            # Note: our pst_id is their userAuthentication PK.
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

    def getStaticContactInfoByID(self, userAuth_id):
        """
        This returns the same output as the method of the same name in UserInfo.
        The excpetion to this is the status field.
        """

        person_id, username, enabled = self.getBasicInfo(userAuth_id)

        emails, emailDescs   = self.getEmails(person_id)
        phones, phoneDescs   = self.getPhones(person_id)
        postals, postalDescs = self.getPostals(person_id)
        affiliations         = self.getAffiliations(person_id)

        return dict(emails = emails
                  , emailDescs = emailDescs
                  , phones = phones
                  , phoneDescs = phoneDescs
                  , postals = postalDescs
                  , affiliations = affiliations
                  # this field is the only one that differs from UserInfo
                  , status = enabled
                  , username = username)

    def getBasicInfo(self, userAuth_id):

        q = """
        SELECT p.person_id, ua.personName, p.enabled
        FROM person as p, userAuthentication as ua
        WHERE p.personAuthentication_id = %d
        AND p.personAuthentication_id = ua.userAuthentication_id
        """ % userAuth_id

        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        return (rows[0][0], rows[0][1], bool(rows[0][2]))

    def getEmails(self, person_id):

        # the query ensures that the first will be the 
        # default value, if there is one.
        q = """
        SELECT email, emailType 
        FROM email
        WHERE person_id = %d
        ORDER BY defaultEmail DESC
        """ % person_id
        
        return self.getContactInfoWorker(q, self.row2email)

    def row2email(self, row):
        return row[0], row[1]

    def getPhones(self, person_id):

        # the query ensures that the first will be the 
        # default value, if there is one.
        q = """
        SELECT phone, phoneType 
        FROM phone
        WHERE person_id = %d
        ORDER BY defaultPhone DESC
        """ % person_id

        return self.getContactInfoWorker(q, self.row2phone)

    def row2phone(self, row):
        return row[0], row[1]

    def getPostals(self, person_id):

        q = """
        SELECT a.street1, a.street2, a.street3, a.street4, 
           a.city, s.stateName, c.addressCountry, a.postalCode,
           t.addressType
        FROM address as a, addressState as s, addressCountry as c,
             addressType as t, address_addressType as aat
        WHERE a.addressState_id  = s.addressState_id  
          AND a.addressCountry_id = c.addressCountry_id 
          AND aat.address_id = a.address_id
          AND aat.addressType_id = t.addressType_id
          AND person_id = %d 
        ORDER BY defaultAddress DESC
        """ % person_id

        return self.getContactInfoWorker(q, self.row2postal)

    def row2postal(self, row):

        streetRows = row[:4]
        streets = ""
        for s in streetRows:
            if s is not None and s != "":
                streets += s + ", "

        address = "%s%s, %s, %s, %s," % (streets, row[4], row[5], row[7], row[6])
        return address, row[8]

    def getAffiliations(self, person_id):

        q = """
        SELECT o.formalName 
        FROM organization as o, person_organization as po 
        WHERE po.organization_id = o.organization_id 
          AND po.person_id = %d
        """ % person_id

        self.cursor.execute(q)
        rows = self.cursor.fetchall()
  
        return [r[0] for r in rows]
            
    def getContactInfoWorker(self, query, fnc ):
        """
        Executes the given query, and uses the passed in function to 
        convert the result to one list of results, and then the same
        list but with the descriptive type appended to the end of each
        result.
        """

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        values = []
        valueDescs = []
        for r in rows:
            v, type = fnc(r)
            vd = "%s (%s)" % (v, type)
            values.append(v)
            valueDescs.append(vd)

        return values, valueDescs    
       
    def findPeopleByNames(self, firstName, lastName):
        """
        This is a utilitly used for finding users who have been newly 
        transferred over from Carl's system into the DSS, and still do
        not have a pst_id or username associated with them.
        """

        query = """
        SELECT person_id, enabled 
        FROM person 
        WHERE firstName = '%s' 
          AND lastName = '%s'
        """ % (firstName, lastName)

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print rows
        return rows


