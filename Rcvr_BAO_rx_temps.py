import settings, pg

curr = pg.connect(host   = settings.DATABASES['default']['HOST']
                  , user   = settings.DATABASES['default']['USER']
                  , passwd = settings.DATABASES['default']['PASSWORD']
                  , dbname = settings.DATABASES['default']['NAME']
                    )
query = "select id from receivers where name = 'Rcvr_BAO'"
result = curr.query(query)
rx_id = result.getresult()[0][0]

query = " select * from receiver_temperatures where receiver_id = 6 "
result = curr.query(query)

for r in result.getresult():
    print r
    q = "insert into receiver_temperatures values (default, %s, %s, %s)" % (rx_id, r[2], r[3] )
    print q
    curr.query(q)
