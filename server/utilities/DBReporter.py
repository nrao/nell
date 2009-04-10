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
        print "*** Projects ***"
        print "Total # of Projects: %d, Total Hrs: %5.2f" % (numProjs, totalProjHrs)
        print ""
    
        semesters = Semester.objects.all()
        proj_types = Project_Type.objects.all()
    

        projSems = self.binProject(projs, semesters, "semester")
        self.printInfo(projSems, "Projects by Semester: ", "Semester")

        projTypes = self.binProject(projs, proj_types, "project_type")
        self.printInfo(projTypes, "Projects by Type: ", "Type")

        projThesis = self.binProject(projs, [True, False], "thesis")
        self.printInfo(projThesis, "Projects by Thesis: ", "Thesis")

        # gather stats on sessions - how many, how many of what type, total hrs ..
        sess = Sesshun.objects.all()
        numSess = len(sess)
        totalSessHrs = sum([s.allotment.total_time for s in sess])
        print "*** Sessions ***" 
        print "Total # of Sessions: %d, Total Hrs: %5.2f" % (numSess, totalSessHrs)
        print ""

        sess_types = Session_Type.objects.all()
        obs_types = Observing_Type.objects.all()
        grade_types = ['A','B','C']
        num_rcvr_grps = range(4)
        bools = [True, False]

        info = self.binSesshun(sess, semesters, "project.semester")
        self.printInfo(info, "Sessions By Semester:", "Semester") 
        info = self.binSesshun(sess, sess_types, "session_type")
        self.printInfo(info, "Sessions By Type:", "Type") 
        info = self.binSesshun(sess, obs_types, "observing_type")
        self.printInfo(info, "Sessions By Obs Type:", "Obs Type") 
        info = self.binSesshun(sess, grade_types, "letter_grade", True)
        self.printInfo(info, "Sessions By Grade:", "Grade") 
        info = self.binSesshun(sess, num_rcvr_grps, "num_rcvr_groups", True)
        self.printInfo(info, "Sessions By Num Receiver Groups:", "# Rcvr Grps") 
        info = self.binSesshun(sess, bools, "status.enabled") 
        self.printInfo(info, "Sessions By Enabled:", "Enabled") 
        info = self.binSesshun(sess, bools, "status.authorized") 
        self.printInfo(info, "Sessions By Authorized:", "Authorized") 
        info = self.binSesshun(sess, bools, "status.complete") 
        self.printInfo(info, "Sessions By Complete:", "Complete") 
        info = self.binSesshun(sess, bools, "status.backup") 
        self.printInfo(info, "Sessions By Backup:", "Backup") 
        info = self.binSesshun(sess, bools, "scheduable", True) 
        self.printInfo(info, "Sessions By Scheduable:", "Scheduable") 

        # gather stats on windows - how many, how many hrs, etc
        # TBF: what to do with cadence?
        wins = Window.objects.all()
        info = self.binWindow(wins, [True, False], "required") 
        self.printInfo(info, "Windows by Required (Hrs is N/A):", "Required")

        numOpts = {}
        numOpts['0'] = (len([w for w in wins if w.num_opportunities() == 0]),0)
        numOpts['1'] = (len([w for w in wins if w.num_opportunities() == 1]),0)
        numOpts['>1'] = (len([w for w in wins if w.num_opportunities() > 1]),0)
        self.printInfo(numOpts, "Windows by Num Opportunities (Hrs is N/A):"
                     , "# Opts")
        
        # gather stats on periods

        print "*** Problems ***"
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

        # try to reproduce the project listing that Carl produces
        # in openpropstbsdetail.pdf

    def binWindow(self, windows, bins, attrib):
        r = {}
        for bin in bins:
            binW = [w for w in windows if w.__getattribute__(attrib) == bin]
            r[str(bin)] = (len(binW), 0) # Hrs is N/A
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

    def printInfo(self, info, title, header):

        # the first col should have a width to accomodate the biggest thing
        keys = info.keys()
        keys.sort()
        maxKeys = max(keys, key=len)
        col1 = len(max([header, maxKeys], key=len))
        cols = [col1, 5, 10]
        print title 
        print header.rjust(cols[0]), "#".rjust(cols[1]), "Hrs".rjust(cols[2])
        print "-" * (sum(cols) + 3)
        for k in keys:
            print k.rjust(cols[0]), str(info[k][0]).rjust(cols[1]), str(info[k][1]).rjust(cols[2]) 
        print ""

