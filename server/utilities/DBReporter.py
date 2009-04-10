from sesshuns.models import *
from utilities.TimeAccounting import TimeAccounting

class DBReporter:

    """
    This class is responsible for reporting on the state of the database.
    It provides statistical summarries, as well as alerts on any potential
    issues.
    """

    # 1st round of requirements gathered from Beta Test code:
    # lint.py, reports.py

    # TBF: cant' calculate used times because there are no Periods

    def __init__(self):
        
        self.ta = TimeAccounting()

    def report(self):

        # *** General Info ***
        # gather stats on projects - how many, how many of what type, total hrs ..
        projs = Project.objects.all()
        numProjs = len(projs)
        totalProjHrs = sum([self.ta.getProjectTotalTime(p) for p in projs])
        print numProjs, totalProjHrs
    
        semesters = Semester.objects.all()
        proj_types = Project_Type.objects.all()
    
        print self.binProject(projs, semesters, "semester")
        print self.binProject(projs, proj_types, "project_type")
        print self.binProject(projs, [True, False], "thesis")

        # gather stats on sessions - how many, how many of what type, total hrs ..
        sess = Sesshun.objects.all()
        numSess = len(sess)
        totalSessHrs = sum([s.allotment.total_time for s in sess])
        print numSess, totalSessHrs

        sess_types = Session_Type.objects.all()
        obs_types = Observing_Type.objects.all()
        grade_types = ['A','B','C']
        num_rcvr_grps = range(4)
        bools = [True, False]
        print self.binSesshun(sess, sess_types, "session_type")
        print self.binSesshun(sess, obs_types, "observing_type")
        print self.binSesshun(sess, grade_types, "letter_grade", True)
        print self.binSesshun(sess, num_rcvr_grps, "num_rcvr_groups", True)
        print self.binSesshun(sess, bools, "status.enabled") 
        print self.binSesshun(sess, bools, "status.authorized") 
        print self.binSesshun(sess, bools, "status.complete") 
        print self.binSesshun(sess, bools, "status.backup") 
        print self.binSesshun(sess, bools, "scheduable") 

        # gather stats on windows - how many, how many hrs, etc
        # TBF: what to do with cadence?
        wins = Window.objects.all()
        print self.binWindow(wins, [True, False], "required") 
        numOpts = {}
        numOpts['0'] = len([w for w in wins if w.num_opportunities() == 0])
        numOpts['1'] = len([w for w in wins if w.num_opportunities() == 1])
        numOpts['>1'] = len([w for w in wins if w.num_opportunities() > 1])
        print numOpts
        
        # gather stats on periods

        # *** Problems ***
        # projects w/ out sessions?
        print "Projects w/ out sessions: ", len([p for p in projs if len(p.sesshun_set.all()) == 0])

        # sessions w/ out projects?
        print "Sessions w/ out projects: ", len([s for s in sess if s.project is None])

        # windowed sessions w/ no windows?
        print "Windowed Sessions /w out windows: ", len([s for s in sess if (s.session_type.type in ['Windowed','VLBI']) and len(s.window_set.all()) == 0])

        # non-windowed sessions w/ a window?
        print "Non-Windowed Sessions /w windows: ", len([s for s in sess if (s.session_type.type not in ['Windowed','VLBI']) and len(s.window_set.all()) > 0])

        # windows w/ out sessions?

        # session w/ min > max duration
        print "Sessions w/ min > max duration: ", [s for s in sess if s.min_duration > s.max_duration]
        # sessions w/ time < min duration?
        print "Sessions w/ min duration < total time: ", [s for s in sess if s.min_duration > s.allotment.total_time]

        # sessions w/ hr angle range < min duration?

    def binWindow(self, windows, bins, attrib):
        r = {}
        for bin in bins:
            binW = [w for w in windows if w.__getattribute__(attrib) == bin]
            r[str(bin)] = len(binW)
        return r

    def binProject(self, projs, bins, attrib):
        r = {}
        for bin in bins:
            binProj = [p for p in projs if p.__getattribute__(attrib) == bin]
            binProjHrs = sum([self.ta.getProjectTotalTime(p) for p in binProj])
            r[str(bin)] = (len(binProj), binProjHrs)
        return r

    def binSesshun(self, sess, bins, attribs, attribFnc = False):
        r = {}
        # attributes can be "attrib", or "attrib.attrib"
        parts = attribs.split(".")
        for bin in bins:
            if len(parts) == 1:
                attrib = parts[0]
                # for one attrib, we must support difference between a member
                # var and a method
                if attribFnc:
                    binSess = [s for s in sess if s.__getattribute__(attrib)() == bin]
                else:    
                    binSess = [s for s in sess if s.__getattribute__(attrib) == bin]
            elif len(parts) == 2:
                # in this case, we don't support methods
                a1, a2 = parts
                binSess = [s for s in sess \
                    if s.__getattribute__(a1).__getattribute__(a2) == bin]
            else:
                raise "binSesshun only supports <= 2 attributes"
            binSessHrs = sum([s.allotment.total_time for s in binSess])
            r[str(bin)] = (len(binSess), binSessHrs)
        return r



