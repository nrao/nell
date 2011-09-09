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

from test_utils                           import BenchTestCase, timeIt
from utilities.database.external.AstridDB import AstridDB

class TestAstridDB(BenchTestCase):

    def setUp(self):

        self.pcodes = ["GBTMy-Project", "TGBT-MyLittlePony"]
        self.acodes = ["AGBTMy_Project", "TGBT_MyLittlePony"] 

    def test_dssCode2astridCode(self):

        adb = AstridDB(dbname = "turtle_sim", test = True)
        for i in range(len(self.pcodes)):
            self.assertEquals(self.acodes[i]
                            , adb.dssCode2astridCode(self.pcodes[i]))

    def test_addProjects(self):

        adb = AstridDB(dbname = "turtle_sim", test = True, quiet = True)

        self.assertEquals(adb.host, "gbtdata.gbt.nrao.edu")
        self.assertEquals(adb.user, "turtle_admin")
        self.assertEquals(adb.dbname, "turtle_sim")

        # make sure the DB is clean
        for acode in self.acodes:
            self.assertEquals(False, adb.astridCodeExists(acode))

        # here's what we're actually testing
        adb.addProjects(self.pcodes)

        # make sure they got in, then clean up
        for acode in self.acodes:
            self.assertEquals(True, adb.astridCodeExists(acode))
            adb.removeAstridCode(acode)
            self.assertEquals(False, adb.astridCodeExists(acode))

       
    def test_astridCodeExists(self):

        # Note: this is not really a unit test, since it connects
        # to an external DB.  This DB can be changed by anyone,
        # though it's a safe bet that this projects won't change.
        adb = AstridDB(dbname = "turtle_sim", test = True)
        r = adb.astridCodeExists("my little pony")
        self.assertEquals(False, r)
        r = adb.astridCodeExists("AGBT01A_020")
        self.assertEquals(True, r)



