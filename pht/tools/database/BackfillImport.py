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

from django.core.management import setup_environ
import settings
setup_environ(settings)

from datetime         import datetime
import math

from PstImport import PstImport
from pht.models       import *
from scheduler.models import Project, Sesshun, Target as DssTarget

class BackfillImport(PstImport):

    def __init__(self, quiet = True):
        PstImport.__init__(self, quiet = quiet)

    def importProjects(self, dss_projects = None):
        if dss_projects is None:
            dss_projects = Project.objects.filter(complete = False)
        projects     = [p for p in dss_projects if self.checkPst(p.pcode)]
        projects_bad = [p for p in dss_projects if not self.checkPst(p.pcode)]

        if not self.quiet:
            print len(projects), 'projects found in the PST.'
            print len(projects_bad), 'projects not found in the PST.'

        for project in projects:
            try:
                proposal = Proposal.objects.get(pcode = project.pcode)
            except Proposal.DoesNotExist:
                if not self.quiet: print 'Importing', project.pcode
                self.importProject(project)

    def importProject(self, project):
        pcode    = project.pcode.replace('GBT', 'GBT/').replace('VLBA', 'VLBA/')
        proposal = self.importProposal(pcode, semester = project.semester.semester)
        # make sure we maintain the PHT/DSS connection
        proposal.dss_project = project
        proposal.save()
        self.importDssSessions(project, proposal)

        # make a record of what we did.
        self.report()

    def importDssSessions(self, project, proposal):
        for s in proposal.session_set.all():
            s.delete()

        for s in project.sesshun_set.all():
            session = Session(proposal = proposal
                            , dss_session = s
                            , name = s.name
                            , scheduler_notes = s.notes
                            , comments = s.accounting_notes
                            , pst_session_id = 0
                            , semester = proposal.semester
                            , observing_type = s.observing_type
                            )
            session.save()

            self.setSessionReceivers(session, s)
            self.setSessionTarget(session, s)
            self.setSessionAllotment(session, s)
            session.session_type = session.determineSessionType()
            session.weather_type = session.determineWeatherType()

            # defaults
            flags = SessionFlags()
            flags.save()
            session.flags = flags
            day = SessionSeparation.objects.get(separation = 'day')
            m = Monitoring(outer_separation = day)
            m.save()
            session.monitoring = m
            n = SessionNextSemester() 
            n.save()
            session.next_semester = n
            session.save()
         

    def setSessionReceivers(self, pht_session, dss_session):
        """
        Transfers DSS session's receivers to the PHT session.
        Ignores the DSS logic.
        """

        for r in dss_session.rcvrs_specified():
            rcvr = Receiver.get_rcvr(r)
            pht_session.receivers.add(rcvr)
        pht_session.save()    
            
    def setSessionTarget(self, pht_session, dss_session):
        try:
            ra = dss_session.target.horizontal
            ra = 2 * math.pi if ra is not None and ra > 2 * math.pi else ra
            target = Target(ra  = ra
                          , dec = dss_session.target.vertical
                            )
            target.save()
            # use this ra & dec to calc. the other LST values
            min_lst, max_lst = target.calcLSTrange()
            target.min_lst = min_lst
            target.max_lst = max_lst
            target.save()
            center, width = target.calcCenterWidthLST()
            target.center_lst = center
            target.lst_width = width
            target.save()
            pht_session.target = target
            pht_session.save()
        except DssTarget.DoesNotExist:
            pass

    def setSessionAllotment(self, pht_session, dss_session):
        allotment = Allotment(allocated_time = dss_session.allotment.psc_time
                                , semester_time  = dss_session.allotment.max_semester_time
                                 )
        allotment.save()
        pht_session.allotment = allotment
        grade = self.dssGrade2phtGrade(dss_session.allotment.grade)
        if grade is not None:
            pht_session.grade = SessionGrade.objects.get(grade = grade)
        pht_session.save()

    def dssGrade2phtGrade(self, grade):
        "Simple mapping: round the grade"
        phtGrade = None
        grade = round(grade)
        if grade > 4.0:
            phtGrade = 'A'
        elif grade < 1.0:    
            phtGrade = 'N'
        else:
            gradeMap = {4.0 : 'A', 3.0: 'B', 2.0: 'C', 1.0: 'N'}
            phtGrade = gradeMap.get(grade)
        return phtGrade    
        

if __name__ == '__main__':
    dss = BackfillImport(quiet = False)
    dss_projects = Project.objects.filter(complete = True).filter(semester__semester__gte = '11A')
    dss.importProjects(dss_projects = dss_projects)
