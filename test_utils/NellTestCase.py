import unittest
import pg
import settings

from django.db  import transaction

class NellTestCase(unittest.TestCase):

    def __init__(self, *args, **kws):
        super(NellTestCase, self).__init__(*args, **kws)
        self.c = None

    def connect(self):
        dbname = "test_" + settings.DATABASE_NAME
        port   = int(settings.DATABASE_PORT) if settings.DATABASE_PORT != '' else 5432
        return pg.connect(host   = settings.DATABASE_HOST
                     , user   = settings.DATABASE_USER
                     , passwd = settings.DATABASE_PASSWORD
                     , port   = port
                     , dbname = dbname)

    def setUp(self):
        if hasattr(settings, "CACHE_BACKEND"):
            settings.CACHE_BACKEND = "dummy:///" # disable caching for testing
        c = self.connect()

        sql = open("populate_db.sql").read()
        c.query(sql)
        c.close()

    def tearDown(self):
        c = self.connect()
        # Query to list all table names in the db
        sql = """SELECT c.relname as "Name"
                 FROM pg_catalog.pg_class c
                    JOIN pg_catalog.pg_roles r ON r.oid = c.relowner
                    LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                 WHERE c.relkind IN ('r','v','S','')
                    AND n.nspname <> 'pg_catalog'
                    AND n.nspname !~ '^pg_toast'
                    AND pg_catalog.pg_table_is_visible(c.oid);
              """
        r = c.query(sql)
        
        #  Exceptions are tables that we don't want to truncated, because they're 
        #  initialization has been moved to scheduler/fixtures/initial_data.json
        exceptions = ['receivers']

        # Filter out information not needed
        tables = [i["Name"] for i in r.dictresult()
                     if '_id_seq' not in i["Name"] and i["Name"] not in exceptions]

        #  Commit any outstanding db transactions before truncating tables
        transaction.commit()

        # Truncate all tables
        sql = "truncate table " + ", ".join(tables)
        c.query(sql)

        # Resequence ids on all tables
        for tb_name in tables:
            if 'auth'   not in tb_name and \
               'django' not in tb_name and \
               'cache'  not in tb_name:
                reseq_cmd = """
                BEGIN;
                SELECT setval('"%s_id_seq"', coalesce(max("id"), 1), max("id") IS NOT null) FROM "%s";
                COMMIT;
                """ % (tb_name, tb_name)
                c.query(reseq_cmd)

        c.close()
