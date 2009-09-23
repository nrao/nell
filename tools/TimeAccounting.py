from datetime        import datetime, timedelta

class TimeAccounting:

    """
    This class is responsible for calculating some of the equations specified in
    Memo 11.2.
    """
    
    # Project leve time accounting
    def getProjectTotalTime(self, proj):
        return sum([a.total_time for a in proj.allotments.all()])

    def getProjSessionsTotalTime(self, proj):
        ss = proj.sesshun_set.all()
        return sum([s.allotment.total_time for s in ss])

    def getObservedProjTime(self, proj):
        ss = proj.sesshun_set.all()
        return sum([self.getObservedTime(s) for s in ss])

    def getProjTimeLost(self, proj):
        ss = proj.sesshun_set.all()
        return sum([self.getTimeLost(s) for s in ss])

    def getProjTimeToOtherSession(self, sess):
        ss = proj.sesshun_set.all()
        return sum([self.getTimeToOtherSession(s) for s in ss])

    def getProjTime(self, type, proj):
        "Generic method for bubbling up all period accting up to the project"
        ss = proj.sesshun_set.all()
        return sum([self.getTime(type, s) for s in ss])

    # Session level time accounting
    def getObservedTime(self, sess):
        now = datetime.utcnow()
        ps = sess.period_set.all()
        return sum([p.accounting.observed() for p in ps if p.end() < now])
        
    def getTimeLeft(self, sess):
        obs = self.getObservedTime(sess)
        return sess.allotment.total_time - obs

    def getTimeLost(self, sess):
        ps = sess.period_set.all()
        return sum([p.accounting.lost_time() for p in ps])

    def getTimeToOtherSession(self, sess):
        ps = sess.period_set.all()
        return sum([p.accounting.other_session() for p in ps])

    def getTimeNotBillable(self, sess):
        ps = sess.period_set.all()
        return sum([p.accounting.not_billable for p in ps])

    def getTime(self, type, sess):
        "Generic method for bubbling up all period accting up to the session"
        ps = sess.period_set.all()
        return sum([p.accounting.__getattribute__(type) for p in ps])

