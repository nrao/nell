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

from pht.tools.database import PstImport
from pht.models         import Proposal
from pht.models         import ImportReport

class TestPstImport(TestCase):

    fixtures = ['scheduler.json']

    def setUp(self):
        self.pst = PstImport()

    def test_importProposal(self):
        proposal = self.pst.importProposal('GBT/12A-002')
        self.assertTrue(proposal is not None)
        self.assertTrue(len(proposal.sci_categories.all()) > 0)
        self.assertTrue(len(proposal.session_set.all()) > 0)
        s = proposal.session_set.all().order_by('name')[0]
        self.assertEquals("GBT12A-002 - 1", s.name)
        self.assertTrue(len(proposal.source_set.all()) > 0)
        src = proposal.source_set.all()[0]
        self.assertAlmostEquals(4.79908, src.ra, 2)
        self.assertAlmostEquals(4.7932, s.target.ra, 4)
        self.assertAlmostEquals(-0.2146, s.target.dec, 4)
        self.assertTrue(len(s.sources.all()) > 0)
        self.assertTrue(len(s.receivers.all()) > 0)
        self.assertTrue(len(s.receivers_granted.all()) > 0)
        self.assertEquals(s.receivers.all()[0].name
                        , s.receivers_granted.all()[0].name)
        self.assertTrue(len(s.backends.all()) > 0)
        self.assertTrue(s.allotment is not None)
        self.assertTrue(s.target is not None)
        self.assertTrue(s.next_semester is not None)
        self.assertEqual('Open - Low Freq', s.session_type.type)
        self.assertEqual('Poor', s.weather_type.type)
        self.assertEqual('spectral line', s.observing_type.type)

        # test the reports
        self.pst.report()
        reports = ImportReport.objects.all()
        self.assertEqual(1, len(reports))
        self.assertTrue(0 < len(reports[0].report))
        proposal.delete()

    def test_importProposal_GBT13A_072(self):
        "Had problems import this ones resources."
        proposal = self.pst.importProposal('GBT/13A-072')
        for s in proposal.session_set.all():
            self.assertTrue(len(s.receivers.all()) > 0)

    def test_semesterFromPcode(self):

        self.assertEquals("12A", self.pst.semesterFromPcode("GBT/12A-002"))
        self.assertEquals("12B", self.pst.semesterFromPcode("GBT/12B-012"))
        self.assertEquals("12B", self.pst.semesterFromPcode("VLBA/12B-012"))
        self.assertEquals(None, self.pst.semesterFromPcode("Chewbacca"))

    def test_proposalUsesGBT(self):

        # GBT/12A-002
        pId = 5813
        self.assertEquals(True, self.pst.proposalUsesGBT(pId, "GBT"))
        # VLBA only
        pId = 5821
        self.assertEquals(False, self.pst.proposalUsesGBT(pId, "VLBA"))

    def test_importProposals(self):
        self.pst.importProposals('12A')
        ps = Proposal.objects.all()
        expSessTypes = [
              'Fixed'
            , 'Open - High Freq 1'
            , 'Open - High Freq 2'
            , 'Open - Low Freq'
            , 'Windowed'
            ]
        expObsTypes = [ 'continuum'
                      , 'pulsar'
                      , 'radar'
                      , 'spectral line'
                      , 'vlbi']

        self.checkProposals(ps, expSessTypes, expObsTypes)

    def test_importProposals_13A(self):
        self.pst.importProposals('13A')
        ps = Proposal.objects.all()
        expSessTypes = [
              'Fixed'
            , 'Open - High Freq 1'
            , 'Open - High Freq 2'
            , 'Open - Low Freq'
            , 'Windowed'
            ]
        expObsTypes = [ 'continuum'
                      , 'pulsar'
                      , 'spectral line'
                      , 'vlbi']

        self.checkProposals(ps, expSessTypes, expObsTypes)

    def checkProposals(self, ps, expSessTypes, expObsTypes):
        self.assertTrue(len(ps) > 0)
        stypes = []
        otypes = []
        wtypes = []
        noObsType = 0
        for p in ps: 
            self.assertTrue(len(p.session_set.all()) > 0)
            # make sure all vlbi/a sessions are fixed
            if 'vlbi' in p.pcode.lower() or 'vlba' in p.pcode.lower():
                for s in p.session_set.all():
                    self.assertEqual('Fixed', s.session_type.type)
            for s in p.session_set.all():
                self.assertTrue(s.session_type is not None)
                self.assertTrue(s.observing_type is not None)
                self.assertTrue(s.weather_type is not None)
                # collect the various types being set
                if s.session_type is not None and \
                    s.session_type.type not in stypes:
                    stypes.append(s.session_type.type)
                if s.observing_type is not None and \
                    s.observing_type.type not in otypes:
                    otypes.append(s.observing_type.type)
                if s.weather_type is not None and \
                    s.weather_type.type not in wtypes:
                    wtypes.append(s.weather_type.type)
                if s.observing_type is None:
                    noObsType += 1
            p.delete()

        self.assertEqual(0, noObsType)
        # make sure the types we are setting are reasonable
        self.assertEquals(expObsTypes, sorted(otypes))
        self.assertEquals(expSessTypes, sorted(stypes))
        self.assertEquals(['Excellent', 'Good', 'Poor'], sorted(wtypes))

        self.assertEqual(0, len(self.pst.badFrontends))
        self.assertEqual(0, len(self.pst.badBackends))

    def test_importProposals_12B(self):
        self.pst.importProposals('12B')
        self.assertTrue(len(Proposal.objects.all()) > 0)
        for p in Proposal.objects.all():
            self.assertTrue(len(p.session_set.all()) > 0)
            p.delete()

        self.assertEqual(0, len(self.pst.badFrontends))
        self.assertEqual(0, len(self.pst.badBackends))
