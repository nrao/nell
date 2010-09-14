import MySQLdb as m

class PSTMirrorDB(object):
    """
    This class is responsible for reading user info from the mirror of
    the PST DB available in Green Bank.  This is a read-only, MySql DB,
    so we decided it wasn't worth the effort to incorporate this DB
    into our model.
    """

    def __init__(self, host = "trent.gb.nrao.edu"
                     , user = "nrao_200"
                     , passwd = ""
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

        person_id, username, enabled = self.getBasicInfo(userAuth_id)
        print person_id, username
        print enabled

        emails, emailDescs = self.getEmails(person_id)

        print emails
        print emailDescs
        print self.getPhones(person_id)

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
        
        print q

        # TBF: use worker method below
        self.cursor.execute(q)
        rows = self.cursor.fetchall()

        emails = []
        emailDescs = []
        for r in rows:
            e = r[0]
            ed = "%s (%s)" % (e, r[1])
            emails.append(e)
            emailDescs.append(ed)

        return emails, emailDescs

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

    def getContactInfoWorker(self, query, fnc ):

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


