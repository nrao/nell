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

from tools.database import UserInfoTools
from scheduler.models         import *
from test_utils              import NellTestCase

class TestUserInfoTools(NellTestCase):

    def test_findUserMatches(self):

        # setup - create a DSS user that matches someone you KNOW
        # exists in the PST
        hacker = User(last_name = "Marganian"
                    , first_name = "Paul"
                    , role = Role.objects.all()[0]
                     )
        hacker.save()
 
        # write results to a file
        f = open("TestUserInfoTools.txt", 'w')
        un = UserInfoTools.UserInfoTools(output_file = f)
        un.findUserMatches()
        f.close()

        # check file for results
        f = open("TestUserInfoTools.txt", 'r')
        lines = f.readlines()
        self.assertEqual(4, len(lines))
        self.assertTrue("User: Marganian, Paul, Projects:" in lines[1])
        self.assertTrue("pmargani   821  True pmargani@nrao.edu" in lines[3])

        # clean up
        hacker.delete()

    def test_findReportUserInfo(self):

        # setup - create a DSS user that matches someone you KNOW
        # exists in the PST
        hacker = User(last_name = "Marganian"
                    , first_name = "Paul"
                    , pst_id = 821
                    , role = Role.objects.all()[0]
                     )
        hacker.save()
        # and setup someone who does not exist
        professional_software_engineer = User(last_name = "Hocus"
                                            , first_name = "Pocus"
                                            , role = Role.objects.all()[0]
                                             )
        professional_software_engineer.save()                                             
        
        # write results to a file
        f = open("TestUserInfoTools.txt", 'w')
        un = UserInfoTools.UserInfoTools(output_file = f)
        un.reportUserInfo()
        f.close()

        # check file for results
        f = open("TestUserInfoTools.txt", 'r')
        lines = f.readlines()
        self.assertEqual(9, len(lines))
        self.assertTrue("len(users):  2" in lines[2])
        self.assertTrue("len(noPstId):  1" in lines[3])
        self.assertTrue("len(matched):  1" in lines[4])
        self.assertTrue("len(mismatched):  0" in lines[5])

        # clean up
        hacker.delete()
        professional_software_engineer.delete()

    def test_assignPstIds(self):

        # setup - create a DSS user that matches someone you KNOW
        # exists in the PST
        hacker = User(last_name = "Marganian"
                    , first_name = "Paul"
                    #, pst_id = 821
                    , role = Role.objects.all()[0]
                     )
        hacker.save()
        # and setup someone who does not exist
        professional_software_engineer = User(last_name = "Hocus"
                                            , first_name = "Pocus"
                                            , role = Role.objects.all()[0]
                                             )
        professional_software_engineer.save()                                             
        
        # write results to a file
        f = open("TestUserInfoTools.txt", 'w')
        un = UserInfoTools.UserInfoTools(output_file = f)
        un.assignPstIds()
        f.close()

        # check file for results
        f = open("TestUserInfoTools.txt", 'r')
        lines = f.readlines()
        self.assertEqual(12, len(lines))
        self.assertTrue("Found pst_id for user:  Marganian, Paul pmargani 821" in lines[1])
        self.assertTrue("Did NOT find pst_id for user:  Hocus, Pocus" in lines[3])

        # clean up
        hacker.delete()
        professional_software_engineer.save()

