from datetime        import datetime, timedelta

class TimeAccounting:

    """
    This class is responsible for calculating some of the equations specified in
    Memo 11.2.
    There is a basic principle here:  all Periods have a number of time
    accounting fields (see Period_Accounting class).  These fields bubble up
    to their Sessions and Projects simply by summing them up, regardless of
    Period state.  
    This can be easily seen by examining the report generated by this class.
    Here is an example:

                        Description Proj Hr Sess Hr      SC      OB      TB      UT      SC      NB      LT     LTW     LTR     LTO      OS     OSW     OSR     OSO

--------------------------------------------------------------------------------------------------------------------------------------------------------------------

                Project: GBT09C-085   24.00   24.00    4.50    4.50    4.00    0.00    0.00    0.50    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00

             Session: GBT09C-085-01           24.00    4.50    4.50    4.00    0.00    0.00    0.50    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00

  Period: 2009-11-30 16:00 for 4.50                    4.50    4.50    4.00    0.00    0.00    0.50    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00
    
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
    
        # for reports
        self.reportLines = []
        self.quietReport = False

    # *** High level time accounting ***

    # These methods are simply convenience methods: they merely show how
    # the lower level methods below can be used

    def getCompletedTimeBilled(self, obj, now=datetime.utcnow()):
        """
        What is the billed time from all the scheduled periods in the past?
        """
        return self.getTime("time_billed", obj, dt=now, past=True)

    def getTimeRemainingFromCompleted(self, obj, now=datetime.utcnow()):
        "Allocated - time billed by completed periods"
        tb = self.getTime("time_billed", obj, now, True)
        if obj.__class__.__name__ == "Project":
            total = self.getProjectTotalTime(obj)
        else: 
            total = obj.allotment.total_time
        return total - tb    
        
    def getUpcomingTimeBilled(self, obj, now=datetime.utcnow()):
        """
        What is the billed time from all the scheduled periods in the future?
        """
        return self.getTime("time_billed", obj, dt=now, past=False)


    # *** Project level time accounting ***

    def getProjectTotalTime(self, proj):
        """
        Projects can have n allotments (w/ n grades).
        What is the sum of all these?
        """
        return sum([a.total_time for a in proj.allotments.all()])

    def getProjectSchedulableTotalTime(self, proj):
        """
        Projects can have n allotments (w/ n grades).
        What is the portion of all these that is actually schedulable?
        """
        total       = self.getProjectTotalTime(proj)
        schedulable = self.getProjSessionsSchedulableTotalTime(proj)
        return min(schedulable, total)

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
        """
        A project is alloted a certain amount of time (by grade).
        But the sum of it's sessions' alloted time can actually be different.
        """
        ss = proj.sesshun_set.all()
        return sum([s.allotment.total_time for s in ss])

    def getProjSessionsSchedulableTotalTime(self, proj):
        """
        A project is alloted a certain amount of time (by grade).
        But the sum of it's sessions' schedulable alloted time can actually 
        be different.
        """
        ss = proj.sesshun_set.all()
        return sum([s.allotment.total_time for s in ss if s.schedulable()])

    # *** Session level time accounting ***

    def getSessTotalByGrade(self, proj, grade):
        "Sums session alloted times that have matching grade."
        return sum([s.allotment.total_time for s in proj.sesshun_set.all() \
                    if s.allotment.grade == grade])
    
    # *** Object independent methods ***

    def getTimeRemaining(self, obj):
        return self.getTimeLeft(obj)

    def getTimeLeft(self, obj):
        "Compares alloted time to billed time for projects or sessions"
        tb = self.getTime("time_billed", obj)
        # ignores grade!
        if obj.__class__.__name__ == "Project":
            total = self.getProjectTotalTime(obj)
        else: 
            total = obj.allotment.total_time
        return total - tb    

    def getTime(self, type, obj, dt=None, past=False):
        """
        Generic method for bubbling up all period accting up to the sess/proj.
        Note that if dt is None, this counts *all* Periods, regardless of 
        position in time, and period state.
          type : one of the Period_Accounting field names listed in self.fields
          obj : either a project or session object
          dt : filter periods summed by this date.  ignore if None
          past : get periods before or after given dt
        """
        assert type in self.fields
        if obj.__class__.__name__ == "Project":
            ss = obj.sesshun_set.all()
            t = sum([self.getTime(type, s, dt, past) for s in ss])
        else:
            ps = obj.period_set.all()
            if dt is None:
                # count all periods
                t =sum([p.accounting.get_time(type) for p in ps])
            else:
                # time dependent
                if past:
                    t = self.getCompletedTime(type, ps, dt)
                else:
                    t = self.getUpcomingTime(type, ps, dt)
        return t            

    def getCompletedTime(self, type, ps, dt):
        "Add up the given type of time for those period before given time"
        #ps = [p for p in periods if not p.isDeleted() and p.end() < dt]
        #return sum([p.accounting.get_time(type) for p in ps])
        # for now, ignore state!
        return sum([p.accounting.get_time(type) for p in ps if p.start <= dt])

    def getUpcomingTime(self, type, ps, dt):
        "Add up the given type of time for those period after given time"
        #ps = [p for p in periods if not p.isDeleted() and p.start > dt]
        #return sum([p.accounting.get_time(type) for p in ps])
        # for now, ignore state!
        return sum([p.accounting.get_time(type) for p in ps if p.start > dt])

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
            dct.update({field : self.getTime(field, proj)})
        
        # session level
        for s in proj.sesshun_set.all():
            notes = s.accounting_notes
            sdct = dict(name       = s.name
                      , grade      = s.allotment.grade
                      , total_time = s.allotment.total_time
                      , notes      = notes if notes is not None else ""
                      , periods    = []
                      )
            for field in self.fields:
                sdct.update({field : self.getTime(field, s)})

             # period level
            for p in s.period_set.all():
                pdct = dict(id = p.id
                          , start = p.start.strftime('%Y-%m-%d %H:%M')
                          , duration = p.duration)
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
            
    def report(self, project, filename = None):
        "Prints out the json of a project's time accounting"

        # init report
        self.reportLines = []

        # map from field names to their Memo 11 abbreviations
        headers =     {'scheduled' : 'SC'
                     , 'observed'  : 'OB'
                     , 'time_billed' : 'TB'
                     , 'unaccounted_time' : 'UT'
                     , 'short_notice' : 'SC'
                     , 'not_billable' : 'NB'
                     , 'lost_time' : 'LT'
                     , 'lost_time_weather' : 'LTW'
                     , 'lost_time_rfi' : 'LTR'
                     , 'lost_time_other' : 'LTO'
                     , 'other_session' : 'OS'
                     , 'other_session_weather' : 'OSW'
                     , 'other_session_rfi' : 'OSR'
                     , 'other_session_other' : 'OSO'
                     }

        json = self.jsondict(project)

        numberWidth = 7
        cols = [35, numberWidth, numberWidth]
        header = ["Description", "Proj Hrs", "Sess Hrs"]
        for field in self.fields:
            cols.append(numberWidth)
            header.append(headers[field])
        self.printData(header, cols, True)

        # project level
        desc = "Project: %s" % project.pcode
        total_time = "%5.2f" % self.getProjectTotalTime(project)
        sess_total_time = "%5.2f" % self.getProjSessionsTotalTime(project)
        data = [desc, total_time, sess_total_time]
        self.printFields(data, json, cols)

        # session level
        sds = json['sessions']
        for sd in sds:
            desc = "Session: %s" % sd['name']
            total_time = "%5.2f" % sd['total_time']
            data = [desc, "", total_time]
            data = self.printFields(data, sd, cols)

            # period level
            periods = sd['periods']
            for p in periods:
                desc = "Period: %s for %3.2f" % \
                    (p['start'], p['duration'])
                data = [desc, "", ""]
                self.printFields(data, p, cols)

        # save it to a file?
        if filename is not None:
            f = open(filename, 'w')
            f.writelines(self.reportLines)

    def printFields(self, data, dct, cols):
        "For use with printing reports"
        for field in self.fields:
            data.append("%5.2f" % dct[field])
        self.printData(data, cols)

    def add(self, lines):
        "For use with printing reports"
        if not self.quietReport:
            print lines
        self.reportLines += lines

    def printData(self, data, cols, header = False):
        "For use with printing reports."
        self.add(" ".join([h[0:c].rjust(c) for h, c in zip(data, cols)]) + "\n")
        if header:
            self.add(("-" * (sum(cols) + len(cols))) + "\n")
