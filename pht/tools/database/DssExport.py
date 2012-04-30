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

from pht.models       import *
from scheduler        import models as dss

class DssExport(object):
    "Exports a PHT proposal to a DSS project."

    def __init__(self, pcodes = [], quiet = True):
        self.quiet = quiet
        self.pcodes = pcodes

    def exportProposals(self, pcodes):
        for pcode in self.pcodes:
            self.exportProposal(pcode)

    def exportProposal(self, pcode):
        proposal = Proposal.objects.get(pcode = pcode)
        if proposal.dss_project:
            return proposal.dss_project

        semester = dss.Semester.objects.get(semester = proposal.semester.semester)
        p_type   = dss.Project_Type.objects.get(type = 'non-science') if 'TGBT' in proposal.pcode else \
                   dss.Project_Type.objects.get(type = 'science')
        project = dss.Project(semester         = semester
                            , project_type     = p_type
                            , pcode            = proposal.pcode
                            , name             = proposal.title
                            , thesis           = proposal.isThesis()[1]
                            , complete         = False
                            , notes            = ''
                            , schedulers_notes = '' #proposal.comments.nrao_comment
                            , disposition      = ''
                            , abstract         = proposal.abstract
                            )

        project.save()
        # allotments
        for grade, time in proposal.allocatedTimeByGrade():
            allotment = dss.Allotment(psc_time = time
                                    , total_time = time
                                    , max_semester_time = time
                                    , grade = self.mapGrade(grade)
                                    )
            allotment.save()
            pa = dss.Project_Allotment(project = project, allotment = allotment)
            pa.save()

        # investigators
        try:
            dss_pi = dss.User.objects.get(pst_id = proposal.pi.pst_person_id)
        except dss.User.DoesNotExist:
            dss_pi = self.createDssUser(proposal.pi)
            i = dss.Investigator(project = project
                               , user    = dss_pi
                               )
            i.principal_investigator = True
            i.save()

        for author in proposal.author_set.all():
            try:
                user = dss.User.objects.get(pst_id = author.pst_person_id)
            except dss.User.DoesNotExist:
                user = self.createDssUser(author)
            if user.pst_id != dss_pi.pst_id:
                i = dss.Investigator(project = project
                                   , user    = user
                                   )
                i.save()

        return project

    def createDssUser(self, author):
        user = dss.User(pst_id = author.pst_person_id
                      , first_name = author.first_name
                      , last_name  = author.last_name
                      )
        user.save()
        return user

    def mapGrade(self, grade):
        "Maps a character grade to a numberical one for DSS."
        gradeMap = {'A' : 4.0
                  , 'B' : 3.0
                  , 'C' : 2.0
                  , 'D' : 1.0
                   }

        g = gradeMap[grade[0]]
        return g + .2 if '+' in grade else (g - .2 if '-' in grade else g)
