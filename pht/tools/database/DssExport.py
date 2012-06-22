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

from datetime               import timedelta
from django.core.management import setup_environ
import settings
setup_environ(settings)

from pht.models       import *
from scheduler        import models as dss

class DssExport(object):
    "Exports a PHT proposal to a DSS project."

    def __init__(self, quiet = True):
        self.quiet = quiet

    def exportProposals(self, pcodes):
        for pcode in pcodes:
            self.exportProposal(pcode)

    def exportProposal(self, pcode):
        proposal = Proposal.objects.get(pcode = pcode)
        if proposal.dss_project:
            return proposal.dss_project
        else:
            # Even though the proposal doesn't have a project, we should
            # still check to see if one exists and if so associate it
            # with this proposal.
            try:
                project = dss.Project.objects.get(pcode = pcode)
            except dss.Project.DoesNotExist:
                pass
            else:
                proposal.dss_project = project
                proposal.save()
                return project

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
        proposal.dss_project = project
        proposal.save()

        if not self.quiet:
            print 'Imported:', project.pcode

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

        # friend
        if proposal.friend:
            friend = dss.Friend.objects.create(project = project, user = proposal.friend)

        # investigators
        try:
            dss_pi = dss.User.objects.get(pst_id = proposal.pi.pst_person_id)
        except dss.User.DoesNotExist:
            dss_pi = self.createDssUser(proposal.pi)
        except dss.User.MultipleObjectsReturned:
            dss_pi = dss.User.objects.filter(pst_id = proposal.pi.pst_person_id).exclude(auth_user = None)[0]
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
            except dss.User.MultipleObjectsReturned:
                user = dss.User.objects.filter(pst_id = proposal.pi.pst_person_id).exclude(auth_user = None)[0]
            if user.pst_id != dss_pi.pst_id:
                i = dss.Investigator(project = project
                                   , user    = user
                                   )
                i.save()

        self.exportSessions(proposal, project)

        return project

    def exportSessions(self, proposal, project):
        for s in proposal.session_set.all():
            self.exportSession(s, project)

    def exportSession(self, pht_session, project):
        # Don't create the DSS session if it hasn't been allocated time.
        if pht_session.allotment.allocated_time is None:
            return

        status = dss.Status.objects.create(
            enabled    = False
          , authorized = False
          , complete   = False
          , backup     = False
        )
        allotment = dss.Allotment.objects.create(
            psc_time          = pht_session.allotment.allocated_time 
          , total_time        = pht_session.allotment.allocated_time
          , max_semester_time = pht_session.allotment.allocated_time
          , grade             = self.mapGrade(pht_session.grade.grade)
        )
        min_dur, max_dur = self.getMinMaxDuration(pht_session)
        dss_session = dss.Sesshun.objects.create(
            project        = project
          , session_type   = self.getSessionType(pht_session)
          , observing_type = pht_session.observing_type
          , allotment      = allotment
          , status         = status
          , name           = pht_session.name
          , frequency      = self.getDefaultFrequency(pht_session)
          , max_duration   = max_dur
          , min_duration   = min_dur
        )

        # Associate the new DSS session with its PHT session
        pht_session.dss_session = dss_session
        pht_session.save()

        source = ', '.join([s.target_name for s in pht_session.sources.all()])
        target = dss.Target.objects.create(
            system     = dss.System.objects.get(name = 'J2000')
          , session    = dss_session
          , vertical   = pht_session.target.dec or 0.0
          , horizontal = pht_session.target.ra or 0.0
          , source     = source if len(source) < 256 else source[:256]
        )

        for r in pht_session.receivers.all():
            rg = dss.Receiver_Group.objects.create(session = dss_session)
            dss_r = dss.Receiver.objects.get(name = r.name)
            rg.receivers.add(dss_r)
            rg.save()
        
        if pht_session.session_type.type == 'Fixed':
            for p in pht_session.period_set.all():
                self.createPeriod(p, dss_session)

        elif pht_session.session_type.type == 'Elective':
            #  TBF: The PHT doesn't currently handle electives.
            #       Assuming all periods belong to one elective.
            elective = dss.Elective.objects.create(
                session  = dss_session
              , complete = False
            )
            for p in pht_session.period_set.all():
                period = self.createPeriod(p, dss_session)
                elective.periods.add(period)
            elective.save()

        elif pht_session.session_type.type == 'Windowed':
            for p in pht_session.period_set.all():
                period = self.createPeriod(p, dss_session)
                window = dss.Window.objects.create(
                    session        = dss_session
                  , default_period = period
                  , complete       = False
                  , total_time     = period.duration
                )
                period.window = window
                period.save()
                window_start = \
                  period.start - timedelta(days = pht_session.monitoring.window_size - 1)
                window_range = dss.WindowRange.objects.create(
                    window     = window
                  , start_date = window_start
                  , duration   = pht_session.monitoring.window_size
                )

    def createPeriod(self, pht_period, dss_session):
        sType = dss_session.session_type.type
        period = dss.Period.objects.create(
            session = dss_session
          , state   = dss.Period_State.objects.get(name = 'Scheduled') if sType == 'fixed' else \
                        dss.Period_State.objects.get(name = 'Pending') 
          , start   = pht_period.start
          , duration = pht_period.duration
          , score    = -1.0
          )
        pa = dss.Period_Accounting(scheduled = 0.0)
        pa.save()
        period.accounting = pa
        period.save()
        self.addPeriodReceivers(period, [r.abbreviation for r in pht_period.session.receivers.all()])
        return period

    def addPeriodReceivers(self, dss_period, abbreviations):
        for abbr in abbreviations:
            rp = dss.Period_Receiver(receiver = dss.Receiver.objects.get(abbreviation = abbr), period = dss_period)
            rp.save()

    def getMinMaxDuration(self, pht_session):
        period_time = pht_session.allotment.period_time
        duration    = pht_session.allotment.allocated_time / pht_session.allotment.repeats

        if pht_session.session_type.type in ('Fixed', 'Windowed', 'Elective'):
            return duration, duration

        # Rules for open
        return (min(period_time, 3.0), period_time) if period_time is not None \
               else (min(3, duration), min(12, duration))

    def getDefaultFrequency(self, pht_session):
        "Find the highest center frequency of all the receivers for this session."
        return max([rx.freq_low + ((rx.freq_hi - rx.freq_low) / 2.) for rx in pht_session.receivers.all()])

    def getSessionType(self, pht_session):
        type = 'open' if 'Open' in pht_session.session_type.type \
                      else pht_session.session_type.type.lower()
        return dss.Session_Type.objects.get(type = type)

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

if __name__ == '__main__':
    proposals = [p.pcode for p in Proposal.objects.filter(semester__semester = '12B') 
                   if p.allocatedTime() > 0]
    print 'Importing', len(proposals), 'proposals.'
    DssExport(quiet = False).exportProposals(proposals)
