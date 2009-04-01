import unittest
import pg

from server import settings

class NellTestCase(unittest.TestCase):

    def setUp(self):
        dbname = "test_" + settings.DATABASE_NAME
        c = pg.connect(user = "dss", dbname = dbname)
        sql = open("populate_db.sql").read()
        c.query(sql)
        c.close()

    def tearDown(self):
        dbname = "test_" + settings.DATABASE_NAME
        c = pg.connect(user = "dss", dbname = dbname)

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
        
        # Filter out unneed information
        tables = [i["Name"] for i in r.dictresult()
                     if 'auth' not in i["Name"] and
                        'django' not in i["Name"] and
                        '_id_seq' not in i["Name"]]

        # Truncate all tables
        sql = "truncate table " + ", ".join(tables)
        c.query(sql)

        # Resequence ids on all tables
        for tb_name in tables:
            reseq_cmd = """
            BEGIN;
            SELECT setval('"%s_id_seq"', coalesce(max("id"), 1), max("id") IS NOT null) FROM "%s";
            COMMIT;
            """ % (tb_name, tb_name)
            c.query(reseq_cmd)

        c.close()
        
