from datetime        import datetime, timedelta

class TimeAccounting:

    """
    This class is responsible for calculating some of the equations specified in
    Memo 11.2.
    """
    
    def __init__(self):

         # if these match up to the Period_Accounting fields, they work
        self.fields = ['scheduled'
                     , 'observed'
                     , 'time_billed'
                     , 'unaccounted_time'
                     , 'short_notice'
                     , 'not_billable'
                     , 'lost_time'
                     , 'lost_time_weather'
                     , 'lost_time_rfi'
                     , 'lost_time_other'
                     , 'other_session'
                     , 'other_session_weather'
                     , 'other_session_rfi'
                     , 'other_session_other'
                     ]
       
    # Project leve time accounting
    def getProjectTotalTime(self, proj):
        return sum([a.total_time for a in proj.allotments.all()])

    def getProjectTimes(self, proj):
        "Returns dict. of times organized by grade"
        times = []
        for a in proj.allotments.all():
            t = dict(psc_time          = a.psc_time
                   , total_time        = a.total_time
                   , max_semester_time = a.max_semester_time
                   , grade             = a.grade
                   , sess_total_time   = self.getSessTotalByGrade(proj, a.grade)
                     )
            times.append(t)
        return times

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

    def getSessTotalByGrade(self, proj, grade):
        "Sums session alloted times that have matching grade."
        return sum([s.allotment.total_time for s in proj.sesshun_set.all() \
            if s.allotment.grade == grade])
            
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
        return sum([p.accounting.get_time(type) for p in ps])

    def jsondict(self, proj):
        "Contains all levels of time accounting info"
        
        # project level
        
        notes = proj.accounting_notes 
        dct = dict(pcode        = proj.pcode
                 , notes        = notes if notes is not None else ""
                 , times        = self.getProjectTimes(proj) 
                 , sessions     = []
                 )
        for field in self.fields:
            dct.update({field : self.getProjTime(field, proj)})
        
        # session level
        for s in proj.sesshun_set.all():
            notes = s.accounting_notes
            if notes is None:
                notes = ""
            sdct = dict(name    = s.name
                      , notes   = notes
                      , periods = [])
            for field in self.fields:
                sdct.update({field : self.getTime(field, s)})

             # period level
            for p in s.period_set.all():
                pdct = dict(id = p.id)
                for field in self.fields:
                    pdct.update({field : p.accounting.get_time(field)})
                sdct['periods'].append(pdct)    

            dct['sessions'].append(sdct)    

        return dct                

    def update_from_post(self, proj, dct):
        "Sets all appropriate time accounting fields in tiered objects"
        
       
        assert proj.pcode == dct.get('pcode', None)
        
        # assign project level info
        proj.notes = dct.get('notes', None)
        proj.save()

        # assign session level info
        sdcts = dct.get('sessions', [])
        for sdct in sdcts:
            name = sdct.get('name', None)
            s = [s for s in proj.sesshun_set.all() if s.name == name][0]
            s.notes = sdct.get('notes', None)
            s.save()

            # assigne period level info
            pdcts = sdct.get('periods', [])
            for pdct in pdcts:
                id = pdct.get('id', None)
                p = [p for p in s.period_set.all() if p.id == id][0]
                for field in self.fields:
                    value = pdct.get(field, None)
                    p.accounting.set_changed_time(field, value)
                    p.accounting.save()
            
