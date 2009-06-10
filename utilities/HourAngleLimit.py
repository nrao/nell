import TimeAgent
import pg

db = 'dss'

class HourAngleLimit:

    def __init__(self):
        self.c = pg.connect(user = "dss", dbname = db)

    def limit(self, freq, dec):
        "Returns the HA offset in hours."
        pquery = self.c.query(
            """SELECT boundary FROM hour_angle_boundaries
               WHERE frequency=%d AND declination=%d""" % \
               (self.freqIndex(freq), self.decIndex(dec)))
        result = pquery.getresult()[0][0]
        return result

    # TBF Are these functions not needed anywhere else?
    def decIndex(self, rad):
        retval = int(round(TimeAgent.rad2deg(rad)))
        return max(-46, min(90, retval))

    def freqIndex(self, f):
        retval = int(round(f))
        return max(2, min(50, retval))
