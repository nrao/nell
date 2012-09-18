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

from django.test        import TestCase
from pht.tools.database import BulkSourceImport
from pht.models         import Proposal
from pht.models         import Source
from pht.models         import SourceCoordinateEpoch

class TestBulkSourceImport(TestCase):

    # must use django.test.TestCase if we want fixtures
    fixtures = ['proposal_GBT12A-002.json']

    def setUp(self):

        self.proposal = Proposal.objects.all()[0]

        self.ex1 = "NGC3242; PNe; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;"
        self.ex2 = "NGC3242 ; PNe ; Equatorial ; J2000 ; 10:24:46.1 ; -18:38:32 ; Barycentric ; Optical ; 4.70;"
        self.ex3 = "NGC3242 Pos1; G1, G2, G3; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;"


        self.lines = [self.ex1, self.ex2, self.ex3]

    def test_importFromLine(self):

        # the example lines from the PST docs should import!
       
        i = BulkSourceImport()
        epoch = SourceCoordinateEpoch.objects.get(epoch = 'J2000')

        src = i.importFromLine(self.ex1, self.proposal.id)
        self.assertEqual('NGC3242', src.target_name)
        self.assertEqual(epoch, src.coordinate_epoch)

        src = i.importFromLine(self.ex2, self.proposal.id)
        self.assertEqual('NGC3242', src.target_name)
        self.assertEqual(epoch, src.coordinate_epoch)

        src = i.importFromLine(self.ex3, self.proposal.id)
        self.assertEqual('NGC3242 Pos1', src.target_name)
        self.assertEqual(epoch, src.coordinate_epoch)

        # cleanup
        for s in i.sources:
            s.delete()

    def test_tryImportFromLine(self):    

        i = BulkSourceImport()
        epoch = SourceCoordinateEpoch.objects.get(epoch = 'J2000')

        # no errors
        src, err = i.tryImportFromLine(self.ex1, 0, self.proposal.id)
        self.assertTrue(err is None)
        self.assertEqual('NGC3242', src.target_name)
        self.assertEqual(epoch, src.coordinate_epoch)

        # Replace J2000 with illegal value 'quack'
        ex2 = "NGC3242; PNe; Equatorial; quack; 10:24:46.1; -18:38:32; Barycentric; Optical; 4.70;"
        src, err = i.tryImportFromLine(ex2, 0, self.proposal.id)
        self.assertTrue(src is None)
        expErr = "Error on line 0: SourceCoordinateEpoch matching query does not exist."
        self.assertEqual(expErr, err) 

        # a line that's too short
        ex3 = "NGC3242; PNe; Equatorial; J2000; 10:24:46.1; -18:38:32; Barycentric; " 
        src, err = i.tryImportFromLine(ex3, 0, self.proposal.pcode)
        self.assertTrue(src is None)
        expErr = 'Error on line 0: Missing values; should be 9 per line'
        self.assertEqual(expErr, err) 

        # cleanup
        for s in i.sources:
            s.delete()

    def test_importSourcesFromLines(self):    

        originalNum = len(Source.objects.all())

        i = BulkSourceImport(pcode = self.proposal.pcode)
        epoch = SourceCoordinateEpoch.objects.get(epoch = 'J2000')

        result, err = i.importSourcesFromLines(self.lines)
        self.assertEqual(True, result)
        self.assertTrue(err is None)
        self.assertEqual(3, len(i.sources))

        newNum = len(Source.objects.all())
        self.assertEqual(3, newNum - originalNum)
        
        # cleanup
        for s in i.sources:
            s.delete()

    def test_importSourcesFromLinesError(self):    

        originalNum = len(Source.objects.all())

        i = BulkSourceImport(pcode = self.proposal.pcode)
        epoch = SourceCoordinateEpoch.objects.get(epoch = 'J2000')
        badLine = "NGC3242 Pos1; G1, G2, G3; Equatorial; J2000; 10:24:46.1; -18:38:32; Barry Sharp; Optical; 4.70;"
        lines = [self.ex1, self.ex2, badLine]

        result, err = i.importSourcesFromLines(lines)
        self.assertEqual(False, result)
        self.assertTrue(err is not None)

        # make sure we cleaned up
        self.assertEqual(0, len(i.sources))

        newNum = len(Source.objects.all())
        self.assertEqual(0, newNum - originalNum)
