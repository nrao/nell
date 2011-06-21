# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

from nell.scheduler.models import *
from nell.utilities.TimeAccounting  import TimeAccounting
from nell.utilities  import TimeAgent

class DBReporter:

    """
    This class is responsible for reporting on the state of the database.
    It provides statistical summarries, as well as alerts on any potential
    issues.
    Right now it is currently used to report on newly projects transferred
    from Carl's system, w/ a format similar to Carl's for cross checking
    purposes.  Using the revision system, one can view how the old
    'report' method used to try and replicate Carl's report exactly, but
    this is no longer used.
    """

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

    def reportProjectSummaryBySemester(self, semester = None):

        if semester is None:
            projs = Project.objects.order_by("pcode").all()
        else:
            projs = Project.objects.filter(semester__semester = semester ).order_by("pcode")
            
        self.reportProjectSummary(projs)

    def reportProjectSummaryByPcode(self, pcodes):

        projs = []
        for pcode in pcodes:
            ps = Project.objects.filter(pcode = pcode)
            projs.extend(ps)
        self.reportProjectSummary(projs)

    def reportProjectSummary(self, projs):    

        # *** General Info ***
        # gather stats on projects - how many, how many of what type, total hrs ..

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
            ssIds = ["%s" % s.original_id for s in ss]
            ssIds.sort()
            ssIdStrs = " ".join(ssIds)
            data = [p.pcode, str(len(ss)), "%5.2f" % hrs, ssIdStrs]
            self.printData(data, cols)
        self.add("\n") 
  
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

    def reportProjectDetails(self, projects, pcodes):

        self.add("Project Details for projects: %s\n" % (", ".join(pcodes)))

        projs = [p for p in projects if p.pcode in pcodes]

        for proj in projs:
            self.projectDetails(proj)

    def projectDetails(self, project):
        
        self.add("Project %s:\n" % project.pcode)
        for a in project.allotments.all():
            self.add("Allotment: %s\n" % a)
        for s in project.sesshun_set.all():
            self.add("  Session name : %s, vpkey : %d, hrs : %5.2f\n" % \
                (s.name, s.original_id, s.allotment.total_time))
            for p in s.period_set.all():
                self.add("    Period %s for %5.2f Hrs\n" % (p.start, p.duration))

        

