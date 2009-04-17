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

    def __init__(self, quiet = False, filename = None):
        
        self.ta = TimeAccounting()
        self.lines = ""
        self.quiet = quiet
        self.filename = filename 

    def add(self, lines):
        if not self.quiet:
            print lines
        self.lines += lines

    def printLines(self):
        
        if not self.quiet:
            print self.lines
            
        if self.filename:
            f = file(self.filename, 'w')
            f.writelines(self.lines)
            f.close()

    def report(self):

        # *** General Info ***
        # gather stats on projects - how many, how many of what type, total hrs ..
        projs = Project.objects.all()
        numProjs = len(projs)
        totalProjHrs = sum([self.ta.getProjectTotalTime(p) for p in projs])
        self.add("\n*** Projects ***\n")
        self.add("Total # of Projects: %d, Total Hrs: %5.2f\n\n" % (numProjs, totalProjHrs))
    
        semesters = Semester.objects.all().order_by('semester')
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
        self.add( "\n*** Sessions ***\n") 
        self.add( "Total # of Sessions: %d, Total Hrs: %5.2f\n\n" % (numSess, totalSessHrs))

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

        self.add("\n*** Problems ***\n")
        # projects w/ out sessions?
        self.add("Projects w/ out sessions: %d\n" % len([p for p in projs if len(p.sesshun_set.all()) == 0]))

        # sessions w/ out projects?
        self.add("Sessions w/ out projects: %d\n" % len([s for s in sess if s.project is None]))

        # windowed sessions w/ no windows?
        self.add("Windowed Sessions /w out windows: %d\n" % len([s for s in sess if (s.session_type.type in ['windowed','vlbi','fixed']) and len(s.window_set.all()) == 0]))

        # non-windowed sessions w/ a window?
        self.add("Non-Windowed Sessions /w windows: %d\n" % len([s for s in sess if (s.session_type.type not in ['windowed','vlbi','fixed']) and len(s.window_set.all()) > 0]))

        # windows w/ out sessions?

        # session w/ min > max duration
        self.add("Sessions w/ min > max duration: %d\n" % len([s for s in sess if s.min_duration > s.max_duration]))
        # sessions w/ time < min duration?
        self.add("Sessions w/ min duration < total time: %d\n" % len([s for s in sess if s.min_duration > s.allotment.total_time]))

        # sessions w/ hr angle range < min duration?

        # try to reproduce the project listing that Carl produces
        # in openpropstbsdetail.pdf
        self.add("\nProject Details ***\n")

        # Here's a summary of Carl's report content
        # Trimester Header
        # Project Header:
        # Code, Title, Rk, Grade, PI, Alloc. time, B/D (?), Sched. time, Bands, 
        # Backends, Obs Type, Prop. Type
        projHeaders = ["Proposal", "Title", "P.I.", "Rk", "G", "Alloc"
                     , "B/D", "Sched", "Bands", "Back Ends", "Obs Type"
                     , "T-J"]
        projHeaderCols = [12, 76, 24, 3, 1, 5, 5, 5, 12, 12, 12, 3]
        # Session Header:
        # name?, #, len(hrs), LST, +/- (?), Sep, Del, Cmpl, TotHrs, lobs, 
        # Comment, Grade, Alloc, B/D, Sched, Bands, Backedns, Req, Outer#, Sep 
        sessHeaders = ["Name", "#", "Len(hrs)", "LST", "+/-", "Sep(d)", "Del(d)", "Compl", "TotHrs", "lobs", "Comment", "G", "Alloc", "B\D", "Sched", "Bands", "Back Ends", "Req", "Outer#", "Sep"]
        sessCols = [14, 1, 8, 12, 3, 6, 6, 5, 6, 9, 12, 1, 5, 3, 5, 8, 9, 8, 3, 5]
        # Trimester Footer:
        # # proposals, total time, time remaining, # proposals started (?)
        semesterFooter = ["Total #", "TotalTime", "Remaining"]
        semesterCols = [7, 9, 9]

        for sem in semesters:
            self.add("Trimester: %s\n\n" % sem.semester)
            s = Semester.objects.get(semester = sem)
            # get the projects for this semester
            projs = Project.objects.filter(semester = s).order_by("pcode")
            if len(projs) > 0:
                self.printData(projHeaders, projHeaderCols, True) 
             
            # TBF: time accounting: Carl isn't giving us history here
            # so if a project was allotted 30 hours, and used up 18,
            # we'll just see that it was allotted 12 ...
            for proj in projs:
                pi = proj.principal_contact()
                if pi is None:
                    pi = ""
                else:
                    pi = pi.__str__()
                # for each proj, print summary
                projData = [proj.pcode
                          , proj.name
                          , pi   
                          , "N/A" # DSS doesn't care about ranke
                          , "" #TBF: Carl doesn't list project grade
                          , "%5.2f" % self.ta.getProjectTotalTime(proj)
                          , "N/A" #TBF: how to map B/D?
                          , "" # Carl leaves these blank instead of zero
                          , self.getCarlRcvrs(proj.rcvrs_specified())
                          , "N/A" # DSS doesn't care about back ends
                          , "TBF" # TBF: how to map these to our Session types?
                          , "TBF" # TBF: what to do with these?
                          ]
                print projData          
                self.printData(projData, projHeaderCols)          

                ss = proj.sesshun_set.order_by("name")

                # print session header
                if len(ss) > 0:
                    self.printData(sessHeaders, sessCols, True)

                for s in ss:    
                    # for each session, print summary
                    sData = [
                             s.name # s.unique_name()
                           , "%d" % self.getCarlRepeats(s) 
                           , "%5.2f" % self.getCarlLenHrs(s)
                           , "TBF" # how to compute LST?
                           , "TBF" # how to compute LST range?
                           , "TBF" # use cadence interval?
                           , "0" # TBF: del always zero?
                           , "TBF" # TBF WTF?
                           , "%5.2f" % s.allotment.total_time
                           , "N/A" # last obs. unknown cause no history
                           , self.getCarlSessionComment(s)
                           , s.letter_grade()
                           , "%5.2f" % s.allotment.total_time
                           , "N/A"
                           , ""
                           , self.getCarlRcvrs(s.rcvrs_specified())
                           , "N/A"
                           , "TBF"
                           , "TBF"
                           , "TBF"]

                    self.printData(sData, sessCols)    


            # print semester summary
            semData = ["%d" % (len(projs))
                     , "%5.2f" % sum([self.ta.getProjectTotalTime(p) \
                                         for p in projs])
                     , "TBF"]
            if len(projs) > 0:
                self.printData(semesterFooter, semesterCols, True)
                self.printData(semData       , semesterCols)

        # finally ...
        self.printLines()

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
        self.add("\n" + title + "\n") 
        self.printData([header, "#", "Hrs"], cols, True)
        for k in keys:
            self.add(" ".join([k[0:cols[0]].rjust(cols[0]), \
                               str(info[k][0])[0:cols[1]].rjust(cols[1]), \
                               str(info[k][1])[0:cols[2]].rjust(cols[2])]) + "\n")

    def printData(self, data, cols, header = False):
        self.add(" ".join([h[0:c].rjust(c) for h, c in zip(data, cols)]) + "\n")
        if header:
            self.add(("-" * (sum(cols) + len(cols))) + "\n")

    def getCarlRcvrs(self, rcvrs):
        "Given an array of DSS rcvr names, return concated Carl version."
        # TBF: convert to Carl abbreviations
        return "".join(rcvrs)

    def getCarlRepeats(self, sess):
        # assume one or no cadences
        cs = sess.cadence_set.all()
        if len(cs) == 1:
            return cs[0].repeats
        else:
            return 0

    def getCarlSessionComment(self, sess):
        # TBF: get source name, position ...
        return ""

    def getCarlLenHrs(self, sess):
        # TBF: is this right?
        repeats = self.getCarlRepeats(sess)
        if repeats != 0:
            return sess.allotment.total_time/repeats
        else:
            return 0
