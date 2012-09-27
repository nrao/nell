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

from django.test         import TestCase

from datetime import datetime, date, timedelta

from scheduler  import models as dss
from pht.tools.database import DssExport
from pht.models import *
from pht.utilities import *
from pht.httpadapters.SessionHttpAdapter import SessionHttpAdapter
from pht.tools.SourceConflicts import SourceConflicts
from pht.tests.utils import *

class TestSourceConflicts(TestCase):

    fixtures = ['proposal_GBT12A-002.json', 'scheduler.json']


    def setUp(self):

        # get the one proposal and it's one session
        proposal = Proposal.objects.all()[0]
        self.proposal = proposal
        for s in self.proposal.session_set.all():
            s.grade = SessionGrade.objects.get(grade = 'A')
            s.save()

        s = proposal.session_set.all()[0]

        # give it some values so it will show up in plot
        s.grade = SessionGrade.objects.get(grade = 'A')
        s.target.min_lst = 0.0
        s.target.max_lst = hr2rad(12.5)
        s.target.save()
        time = 6.5 # hrs
        s.allotment.allocated_time = time # hrs
        s.allotment.save()
        s.save()
        self.session = s

    # TBF: stick this in a utility somewhere        
    def createSession(self, p):
        "Create a new session for the tests"
        return createSession(p)

    def createProposal(self):
        proposalType  = ProposalType.objects.get(type = "Director's Discretionary Time")
        status        = Status.objects.get(name = 'Submitted')
        abstract      = '' 
        semester      = Semester.objects.get(semester = '10A')
        name          = ''
        pcode         = 'GBT10A-009'
        proposal = Proposal(pst_proposal_id = 0
                      , proposal_type   = proposalType
                      , status          = status
                      , semester        = semester
                      , pcode           = pcode
                      , create_date     = datetime.now()
                      , modify_date     = datetime.now()
                      , submit_date     = datetime.now()
                      , title           = name
                      , abstract        = abstract
                      , joint_proposal  = False 
                      )
        proposal.save()
        return proposal

    def createSrc(self, proposal, ra = 0.0, dec = 0.0):
        src = Source(proposal = proposal
                  , ra = ra
                  , dec = dec
                     )
        src.save()
        return src

    def test_calcAnglularDistance(self):

        src1 = Source(ra = 0.0
                    , dec = 0.0)
        src2 = Source(ra = 0.0
                    , dec = 0.0)

        sc = SourceConflicts()
        d = sc.calcAngularDistance(src1, src2)
        self.assertAlmostEqual(0.0, d, 3)
   
        # from Carl's report For GBT12B-364:
        # source NGC 1266
        src1.ra = 0.85526951111895499
        src1.dec = -0.042364958710075701
        # source NGC1266, GBT10A-014
        src2.ra = 0.85526223891373798 #sexHrs2rad('03:16:00.0')
        src2.dec = -0.0423630194553513 #sexDeg2rad('-02:25:37.0')
        d = sc.calcAngularDistance(src1, src2)
        self.assertAlmostEqual(0.0258519896867, rad2arcMin(d), 5)
        #print "deltaRa: ", rad2arcMin(abs(src2.ra - src1.ra))
        #print "deltaDec: ", rad2arcMin(abs(src2.dec - src1.dec))

        # source NGC 3665
        src1.ra = 2.9876837023847602
        src1.dec = 0.67653858425479396
        # source SDSS J112346 ...; GBT08A-033
        src2.ra = 2.9835247282213602 #sexHrs2rad('11:23:46')
        src2.dec = 0.67338971939598802 #sexDeg2rad('38:34:56')
        d = sc.calcAngularDistance(src1, src2)
        self.assertAlmostEqual(15.549314042, rad2arcMin(d), 5)
        #print "deltaRa: ", rad2arcMin(abs(src2.ra - src1.ra))
        #print "deltaDec: ", rad2arcMin(abs(src2.dec - src1.dec))


    def test_getAnglularDistance(self):
        src1 = self.createSrc(self.proposal)
        src2 = self.createSrc(self.proposal)

        sc = SourceConflicts()

        self.assertEqual(0, len(sc.distances))

        # calculate it and stick it in the cache!
        d = sc.getAngularDistance(src1, src2)
        self.assertAlmostEqual(0.0, d, 3)

        self.assertEqual(1, len(sc.distances))
        key = (src1.id, src2.id)
        self.assertAlmostEqual(0.0, sc.distances[key], 3)
      
        # make sure we use the cache when switching sources around
        d = sc.getAngularDistance(src2, src1)
        self.assertAlmostEqual(0.0, d, 3)

        self.assertEqual(1, len(sc.distances))
        key = (src1.id, src2.id)
        self.assertAlmostEqual(0.0, sc.distances[key], 3)
      
    def test_getLowestRcvr(self):

        # test the simplest case of one sess w/ one rcvr
        sc = SourceConflicts()
        lr = sc.getLowestRcvr(self.proposal)
        r  = self.session.receivers.all()[0]
        self.assertEqual(r, lr)

        # now add another sess w/ more then one rcvr
        s = self.createSession(self.proposal)
        s.receivers.add(Receiver.objects.get(abbreviation = 'Q'))
        s.receivers.add(Receiver.objects.get(abbreviation = '800'))
        s.save()
        lr = sc.getLowestRcvr(self.proposal)
        self.assertEqual('800', lr.abbreviation) 


    def test_calcSearchRadiusForRcvr(self):
        # a silly test really - they ALL get calculated in the __init__
        sc = SourceConflicts()
        r  = Receiver.objects.get(name = 'Rcvr4_6') 
        rad = sc.calcSearchRadiusForRcvr('C')
        self.assertAlmostEquals(0.0014544, rad, 7)

    def test_withinProprietaryDate(self):

        s      = self.proposal.session_set.all()[0]
        src0   = self.proposal.source_set.all()[0]
        tpcode = self.proposal.pcode

        # Need a DSS Project for this
        export   = DssExport()
        project  = export.exportProposal(tpcode)
        proposal = Proposal.objects.get(pcode = tpcode)
        period   = dss.Period.objects.create(session = project.sesshun_set.all()[0]
                                           , start = datetime(2012, 6, 10)
                                           , duration = 8
                                           , state = dss.Period_State.objects.get(name = 'Scheduled')
                                           )

        # turn the crank
        sc = SourceConflicts()
        _, result = sc.withinProprietaryDate(proposal, now = datetime(2012, 6, 12))
        self.assertTrue(result)

        _, result = sc.withinProprietaryDate(proposal, now = datetime(2013, 6, 12))
        self.assertTrue(not result)

    def test_findConflicts(self):

        s = self.proposal.session_set.all()[0]
        src0 = self.proposal.source_set.all()[0]
        tpcode = self.proposal.pcode

        # create a new proposal w/ sessions and sources
        newP = self.createProposal() 
        newS = self.createSession(newP)
        newS.grade = SessionGrade.objects.get(grade = 'A')
        newS.receivers.add(Receiver.objects.get(abbreviation = 'Q'))
        newS.receivers.add(Receiver.objects.get(abbreviation = '800'))
        newS.save()
        # make conflict
        src1 = self.createSrc(newP) 
        src1.target_name = src0.target_name
        src1.ra = src0.ra 
        src1.dec = src0.dec 
        src1.save()
        # make another conflict
        src2 = self.createSrc(newP) 
        src2.target_name = src0.target_name + "!"
        src2.ra = src0.ra + (src0.ra*0.0002)
        src2.dec = src0.dec - (src0.dec*0.0002)
        src2.save()

        # turn the crank
        sc = SourceConflicts()
        sc.findConflicts()
        cf = sc.conflicts

        # check the results
        self.assertEqual(2, len(cf))
        self.assertEqual(['GBT10A-009','GBT12A-002'], sorted(cf.keys()))
        # we've already tested these results below in the other test
        scf1 = cf['GBT12A-002']['conflicts']
        self.assertEqual(2, len(scf1))
        # but not for conflicts for this newly created proposal
        c = cf['GBT10A-009']
        self.assertEqual('GBT10A-009', c['proposal'].pcode)
        self.assertEqual('800', c['lowestRx'].abbreviation)
        self.assertAlmostEqual(0.0090175344, c['searchRadius'], 5)
        # the conflicts are the mirror of eachother
        scf2 = c['conflicts']
        self.assertAlmostEqual(2, len(scf2))
        for i in range(2):    
            self.assertEqual(scf1[i]['targetSrc']
                           , scf2[i]['searchedSrc'])
            self.assertEqual(scf2[i]['targetSrc']
                           , scf1[i]['searchedSrc'])
            self.assertAlmostEqual(scf1[i]['distance']
                                 , scf2[i]['distance'], 5)
            


    def test_findConflictsBetweenProposals(self):

        s = self.proposal.session_set.all()[0]
        src0 = self.proposal.source_set.all()[0]
        tpcode = self.proposal.pcode

        # create a new proposal w/ sessions and sources
        newP = self.createProposal() 
        newS = self.createSession(newP)
        newS.receivers.add(Receiver.objects.get(abbreviation = 'Q'))
        newS.receivers.add(Receiver.objects.get(abbreviation = '800'))
        newS.save()
        src1 = self.createSrc(newP) 
        src2 = self.createSrc(newP) 
                      
        # Look for conflicts - there should be none 
        sc = SourceConflicts()
        sc.findConflictsBetweenProposals(self.proposal, newP)
        self.assertEqual(1, len(sc.conflicts.keys()))
        self.assertEqual(tpcode, sc.conflicts[tpcode]['proposal'].pcode)
        self.assertEqual('Rcvr4_6', sc.conflicts[tpcode]['lowestRx'].name)
        self.assertAlmostEqual(0.0014544410433286077
                             , sc.conflicts[tpcode]['searchRadius']
                             , 6)
        self.assertEqual(0, len(sc.conflicts[tpcode]['conflicts']))                             
        # now make a conflict
        src1.target_name = src0.target_name
        src1.ra = src0.ra 
        src1.dec = src0.dec 
        src1.save()

        # make sure we detect it
        sc.conflicts = {}
        sc.distances = {}
        sc.findConflictsBetweenProposals(self.proposal, newP)
        self.assertEqual(1, len(sc.conflicts[tpcode]['conflicts'])) 
        # check out the only conflict
        cf = sc.conflicts[tpcode]['conflicts'][0]
        self.assertEqual(src0.id, cf['targetSrc'].id)
        self.assertEqual(src1.id, cf['searchedSrc'].id)
        self.assertEqual('GBT10A-009', cf['searchedProp'].pcode)
        self.assertEqual(0, cf['level'])
        self.assertAlmostEqual(0.00000, cf['distance'], 5)

        # make another conflict - a little more subtle
        src2.target_name = src0.target_name + "!"
        src2.ra = src0.ra + (src0.ra*0.0002)
        src2.dec = src0.dec - (src0.dec*0.0002)
        src2.save()

        # make sure we detect both 
        sc.conflicts = {}
        sc.distances = {}
        sc.findConflictsBetweenProposals(self.proposal, newP)
        # check out the new conflict
        self.assertEqual(2, len(sc.conflicts[tpcode]['conflicts'])) 
        cf = sc.conflicts[tpcode]['conflicts'][1]
        self.assertEqual(src0.id, cf['targetSrc'].id)
        self.assertEqual(src2.id, cf['searchedSrc'].id)
        self.assertEqual('GBT10A-009', cf['searchedProp'].pcode)
        self.assertEqual(0, cf['level'])
        self.assertAlmostEqual(0.0009417, cf['distance'], 5)
