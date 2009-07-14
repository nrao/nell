from sesshuns.models import *
from TimeAccounting  import TimeAccounting
from utilities       import TimeAgent

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

        # project summary: for each project, how many sess, hrs, etc.
        self.add("\n")    
        self.add("Project Summary (modeled from Carl's report): \n")
        header = ["Name", "#", "Hrs", "Original IDs"]
        cols = [10, 5, 6, 50]
        self.printData(header, cols, True)
        for p in projs:
            ss = p.sesshun_set.all()
            hrs = self.ta.getProjSessionsTotalTime(p)
            ssIds = ["%d" % s.original_id for s in ss]
            ssIdStrs = " ".join(ssIds)
            data = [p.pcode, str(len(ss)), "%5.2f" % hrs, ssIdStrs]
            self.printData(data, cols)
        self.add("\n")    

        # now do the same kind of thing, but this time specifying 
        # how much time is left
        self.add("\n")    
        self.add("Project Time Usage Summary: \n")
        header = ["Name", "Rcvrs", "Grade", "Type", "Proj Hrs", "Obs Hrs", "Proj Left"]
        cols = [15, 15, 10, 10, 10, 10, 10]
        self.printData(header, cols, True)
        for p in projs:
            rcvrs = "".join(p.rcvrs_specified())
            total = self.ta.getProjectTotalTime(p)
            sTotal = self.ta.getProjSessionsTotalTime(p)
            observed = self.ta.getObservedProjTime(p)
            remaining = total - observed
            sRemaining = sTotal - observed
            ss = p.sesshun_set.all()
            types = []
            for s in ss:
                t = s.session_type.type
                type = t[0]
                if type not in types:
                    types.append(type)
            numSess = len(p.sesshun_set.all())
            if numSess == 0:
                aveGrade = 0.0
            else:
                aveGrade = sum([s.allotment.grade for s in p.sesshun_set.all()])/numSess
            data = [p.pcode, rcvrs, "%5.2f" % aveGrade, "%s" % "".join(types), "%5.2f" % total, "%5.2f" % observed, "%5.2f" % remaining]
            self.printData(data, cols)
        self.add("\n")    

        # now, try to point out any sessions that have time left that really 
        # should not:
        #   * only worry about open - that's all we're responsible
        #   * only worry about sessions that rcvrs up for the summer.
        badRcvrs = ['450', '600', 'K', 'Ka', 'Q', 'MBA', 'Z', 'Hol']
        ss = Sesshun.objects.order_by('name')
        for s in ss:
            timeLeft = self.ta.getTimeLeft(s)
            if timeLeft > s.min_duration and \
               s.session_type.type == 'open' and \
               True not in [r in badRcvrs for r in  s.rcvrs_specified()]:
                self.add("Session that should have been scheduled more: %s\n" % s)
                #self.add( "open session w/ bad rcvr: %s\n" % s)
                #self.add( "rcvr: %s\n" % "".join(s.rcvrs_specified()))

            

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
        info = self.binSesshun(sess, bools, "schedulable", True) 
        self.printInfo(info, "Sessions By Scheduable:", "Scheduable") 
         
        info = self.binSesshunNumTargets(sess)
        self.printInfo(info, "Sessions By Num Targets:", "# Targets") 

        info = self.binSesshunNumCadences(sess)
        self.printInfo(info, "Sessions By Num Cadences:", "# Cadences") 

        info = self.binSesshunNumCadences([s for s in sess 
            if s.session_type.type == "vlbi"])
        self.printInfo(info, "VLBI Sessions By Num Cadences:", "# Cadences") 

        info = self.binSesshunNumCadences([s for s in sess 
            if s.session_type.type == "fixed"])
        self.printInfo(info, "Fixed Sessions By Num Cadences:", "# Cadences") 

        info = self.binSesshunNumCadences([s for s in sess 
            if s.session_type.type == "windowed"])
        self.printInfo(info, "Windowed Sessions By Num Cadences:", "# Cadences") 
        info = self.binSesshunNumCadences([s for s in sess 
            if s.session_type.type == "open"])
        self.printInfo(info, "Open Sessions By Num Cadences:", "# Cadences") 
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
        
        # more details on cadences ...
        data = self.cadenceDetails([s for s in sess
            if s.session_type.type == "open"])
        self.printCadenceDetails("Open Session Cadence Details: ", data)
        data = self.cadenceDetails([s for s in sess
            if s.session_type.type == "fixed"])
        self.printCadenceDetails("Fixed Session Cadence Details: ", data)
        data = self.cadenceDetails([s for s in sess
            if s.session_type.type == "windowed"])
        self.printCadenceDetails("Windowed Session Cadence Details: ", data)
        
        # more details on windows
        # TBF: this might get ugly once we start creating these from 
        # cadences
        self.add("\n\nDetails on Windows: \n")
        wins = Window.objects.all()
        for w in wins:
            self.add("%s: %s\n" % (w.session.name, w))
            for o in w.opportunity_set.all():
                self.add("    %s\n" % o)
        self.add("\n")        

        # gather stats on periods

        self.add("\n*** Problems ***\n")
        # projects w/ out sessions?
        self.add("Projects w/ out sessions: %d\n" % len([p for p in projs if len(p.sesshun_set.all()) == 0]))

        # sessions w/ out projects?
        self.add("Sessions w/ out projects: %d\n" % len([s for s in sess if s.project is None]))

        # project time != sum( session time) - only applicable for our import
        badProjTimes = [(p, self.ta.getProjectTotalTime(p) - self.ta.getProjSessionsTotalTime(p)) for p in projs if abs(self.ta.getProjectTotalTime(p) - self.ta.getProjSessionsTotalTime(p)) > 0.1]
        if len(badProjTimes) > 0:
            self.add("Projects w/ times != sum(session times): %s\n" % badProjTimes)

        totalProjHrs = sum([self.ta.getProjectTotalTime(p) for p in projs])
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
        sessHeaders = ["Name", "#", "Len(hrs)", "LST", "N", "+/-", "Sep(d)", "Del(d)", "Compl", "TotHrs", "lobs", "Comment", "G", "Alloc", "B\D", "Sched", "Bands", "Back Ends", "Req", "Outer#", "Sep"]
        sessCols = [14, 3, 8, 12, 1, 3, 6, 6, 5, 6, 9, 30, 1, 5, 3, 5, 8, 9, 8, 3, 5]
        # Trimester Footer:
        # # proposals, total time, time remaining, # proposals started (?)
        semesterFooter = ["Total #", "TotalTime", "Remaining"]
        semesterCols = [7, 9, 9]

        for sem in semesters:
            self.add("\nTrimester: %s\n\n" % sem.semester)
            s = Semester.objects.get(semester = sem)
            # get the projects for this semester
            projs = Project.objects.filter(semester = s).order_by("pcode")
            if len(projs) > 0:
                self.printData(projHeaders, projHeaderCols, True) 
             
            # TBF: time accounting: Carl isn't giving us history here
            # so if a project was allotted 30 hours, and used up 18,
            # we'll just see that it was allotted 12 ...
            for proj in projs:
                # for each proj, print summary
                projData = [proj.pcode
                          , proj.name
                          , self.getCarlInvestigators(proj)   
                          , "N/A" # DSS doesn't care about ranke
                          , "" #TBF: Carl doesn't list project grade
                          , "%5.2f" % self.ta.getProjectTotalTime(proj)
                          , "N/A" #TBF: how to map B/D?
                          , "" # Carl leaves these blank instead of zero
                          , self.getCarlRcvrs(proj.rcvrs_specified())
                          , "N/A" # DSS doesn't care about back ends
                          , self.getObsTypes(proj) # use DSS obs types  
                          , "N/A" # TBF: what to do with these?
                          ]
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
                           , self.getCarlNightTimeFlag(s)
                           , "TBF" # how to compute LST range?
                           , "%s" % self.getCarlSeperation(s) 
                           , "N/A" # TBF: del always zero?
                           , "0" # no history, always zero
                           , "%5.2f" % s.allotment.total_time
                           , "N/A" # last obs. unknown because no history
                           , self.getCarlSessionComment(s)
                           , s.letter_grade()
                           , "%5.2f" % s.allotment.total_time
                           , self.getSessionTypeLetter(s) # use DSS own meaning
                           , "" # no history
                           , self.getCarlRcvrs(s.rcvrs_specified())
                           , "N/A"
                           , self.getCarlStartDate(s) 
                           , "N/A"
                           , "N/A"]

                    self.printData(sData, sessCols)    

                    # print any details that are getting cutoff:
                    if len(sData[11]) > sessCols[11]:
                        self.add("\nComment Details: %s\n\n" % sData[11])
                    #if len(s.cadence_set.all()) > 0:    
                    #    ests = [TimeAgent.est2utc(c.start_date) for c in s.cadence_set.all() if c.start_date is not None]
                    #    self.add("Cadences: %s, UTC starts: %s\n\n" % (s.cadence_set.all(), ests))

                # give a space between each project
                self.add("\n\n")

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

    def binSesshunNumTargets(self, sess):
        nums = {}
        nums['0']  = (len([s for s in sess if s.target_set.all() == []])    , 0)
        nums['1']  = (len([s for s in sess if len(s.target_set.all()) == 1]), 0)
        nums['>1'] = (len([s for s in sess if len(s.target_set.all()) > 1]) , 0)
        return nums

    def binSesshunNumCadences(self, ss):
        nums = {}
        nums['0']  = (len([s for s in ss if len(s.cadence_set.all()) == 0]), 0)
        nums['1']  = (len([s for s in ss if len(s.cadence_set.all()) == 1]), 0)
        nums['>1'] = (len([s for s in ss if len(s.cadence_set.all()) > 1]) , 0)
        return nums

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

    def cadenceDetails(self, ss):
        all = [s for s in ss if  len(s.cadence_set.all()) != 0]
        # sessions w/ out start dates?
        noStart = [s for s in ss 
            if len(s.cadence_set.all()) != 0
            and self.getCadenceAttr(s, "start_date") is None]
        # sessions w/ out end dates
        noEnd = [s for s in ss 
            if len(s.cadence_set.all()) != 0
            and self.getCadenceAttr(s, "end_date") is None]
        # sessions w/ and intervals = 0
        #singles  = [s for s in ss if self.getCadenceAttr(s, "repeats") == 1 \
        #                         and self.getCadenceAttr(s, "intervals") == "0"]
        singles  = [s for s in ss if self.getCadenceAttr(s, "intervals") == "0"]
        # intervals == "#" or "#,#,..."?                         
        regulars = [s for s in ss 
            if self.getCadenceAttr(s, "intervals") is not None and
            "," not in self.getCadenceAttr(s, "intervals")] 
        electives = [s for s in ss  
            if self.getCadenceAttr(s, "intervals") is not None and
            "," in self.getCadenceAttr(s, "intervals")] 
        return dict( all       = all
                   , noStart   = noStart
                   , noEnd     = noEnd
                   , singles   = singles
                   , regulars  = regulars
                   , electives = electives )

    def getCadenceAttr(self, s, a):
        cs = s.cadence_set.all()
        if len(cs) == 0:
            return None
        else:
            return cs[0].__getattribute__(a)

    def printLongLine(self, line, width):
        numLines = (len(line) / width) + 1
        start = 0
        for i in range(numLines):
            start = i * width
            end = start + width
            part = line[start:end]
            self.add(part + "\n")

    def printCadenceDetails(self, title, details):
        self.add("\n" + title + "\n")
        header = ["Type", "#", "Some Examples"]
        cols = [18, 5, 80]
        self.printData(header, cols, True)
        types = [("All", "all")
               , ("No End Date", "noEnd")
               , ("No Start Date", "noStart")
               , ("Intervals = 0", "singles")
               , ("Scalar Intervals", "regulars")
               , ("Vector Intervals", "electives")
               ]
        for type, key in types:
            num = str(len(details[key]))
            names = ",".join([s.name for s in details[key]])
            self.printData([type, num, names], cols)

        # all examples
        for type, key in types:
            names = ",".join([s.name for s in details[key]])
            if len(names) > cols[2]:
                self.add("\nAll Examples for %s : \n" % type)
                self.printLongLine(names, cols[2])

         # all examples w/ details
        for type, key in types:
            ss = details[key]
            if len(ss) > 0:
                self.add("\nAll Examples w/ Details for %s : \n" % type)
                for s in ss:
                    #self.add("Org.ID: %d, Session: %s, %s\n" % (s.original_id, s, s.cadence_set.all()))
                    self.printLongLine("Org.ID: %d, Session: %s, %s\n" % (s.original_id, s, s.cadence_set.all()), cols[2])

    def getCarlInvestigators(self, proj):
        "String looks like: pi [coi], only if coi is different from pi"
        pi = proj.principal_investigator()
        if pi is None:
            pi = ""
        else:
            pi = pi.__str__()
        pc = proj.principal_contact()
        if pc is None:
            pc = ""
        else:
            pc = pc.__str__()
        if pi == pc:
            invs = pi
        else:
            invs = "%s[%s]" % (pi, pc)
        return invs    

    def getSessionTypeLetter(self, s):
        return s.session_type.type[0].upper()

    def getObsTypes(self, proj):
        "Creates a string representing all the different obs types in the proj"
        types = []
        for s in proj.sesshun_set.all():
            type = s.observing_type.type[0].upper()
            if type not in types:
                types.append(type)
        return "".join(types)

    def getCarlRcvrs(self, rcvrs):
        "Given an array of DSS rcvr names, return concated Carl version."
        # TBF: convert to Carl abbreviations
        return "".join(rcvrs)

    def getCarlStartDate(self, sess):
        # TBF: watch for Window entries as well.
        # assume one cadence
        cs = sess.cadence_set.all()
        if len(cs) > 0:
            c = cs[0]
            if c.start_date is not None:
                start = TimeAgent.est2utc(c.start_date).strftime("%m/%d/%y")
            else:
                start = ""
        else:
            start = ""
        return start    

    def getCarlRepeats(self, sess):
        # assume one or no cadences
        cs = sess.cadence_set.all()
        if len(cs) == 1:
            return cs[0].repeats
        else:
            return 1

    def getCarlSeperation(self, sess):
        # assume one or no cadences
        cs = sess.cadence_set.all()
        if len(cs) == 1:
            return cs[0].intervals
        else:
            return ""

    def getCarlNightTimeFlag(self, sess):
        flag = ""
        for op in sess.observing_parameter_set.all():
            if op.parameter.name == "Night-time Flag" and op.boolean_value:
                flag = "T"
        return flag

    def getCarlSessionComment(self, sess):
        # get source name, position ...
        # TBF: assume one target?
        ts = sess.target_set.all()
        if len(ts) > 0:
            posName = "[%5.2f, %5.2f]/%s" % (ts[0].horizontal
                                           , ts[0].vertical
                                           , ts[0].source)
        else:
            posName = ""
        # params
        ops = sess.observing_parameter_set.all()
        opList = [] 
        for op in ops:
            value = "%s(%s)" % (op.parameter.name, op.value())
            opList.append(value)
        opStr = ",".join(opList)    
            
        return "[%d] %s/%s" % ( sess.original_id, posName, opStr)
                                          

    def getCarlLenHrs(self, sess):
        # TBF: is this right?
        repeats = self.getCarlRepeats(sess)
        if repeats != 0:
            return sess.allotment.total_time/repeats
        else:
            return 0
